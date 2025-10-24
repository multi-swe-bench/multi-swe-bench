import re
import json
from typing import Optional, Union

from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.instance import Instance, TestResult
from multi_swe_bench.harness.pull_request import PullRequest


class ImageDefault(Image):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    @property
    def config(self) -> Config:
        return self._config

    def dependency(self) -> str:
        return "node:20"

    def image_prefix(self) -> str:
        return "envagent"

    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:
        repo_name = self.pr.repo
        return [
            File(
                ".",
                "fix.patch",
                f"{self.pr.fix_patch}",
            ),
            File(
                ".",
                "test.patch",
                f"{self.pr.test_patch}",
            ),
            File(
                ".",
                "prepare.sh",
                """ls
###ACTION_DELIMITER###
npm install -g pnpm
###ACTION_DELIMITER###
pnpm install
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
set -e
pnpm run test -- --verbose
pnpm run test:create
pnpm run test:initialize
pnpm run test:migrate -- --verbose
EOF
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
set -e
pnpm run test -- --run --verbose
pnpm run test:create
pnpm run test:initialize
pnpm run test:migrate -- --verbose
EOF
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
set -e
pnpm run test -- --run --verbose --threads=1
pnpm run test:create
pnpm run test:initialize
pnpm run test:migrate -- --run --verbose --threads=1
EOF
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
set -e
pnpm run test -- --run --verbose --threads=1
pnpm exec tsx script/create-test-e2e.ts
pnpm exec tsx script/initialize-test-e2e.ts
pnpm run test:migrate -- --verbose --threads=1
EOF
###ACTION_DELIMITER###
pnpm run build
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
pnpm run test -- --run --verbose
pnpm run test:create
pnpm run test:initialize
pnpm run test:migrate -- --run --verbose
EOF
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
export CI=true
pnpm run test -- --run --verbose
pnpm exec tsx script/create-test-e2e.ts
pnpm exec tsx script/initialize-test-e2e.ts
pnpm run test:migrate -- --run --verbose
EOF
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
export CI=true
pnpm run test -- --run --verbose --reporter=json --threads=1
pnpm exec tsx script/create-test-e2e.ts
pnpm exec tsx script/initialize-test-e2e.ts
pnpm run test:migrate -- --run --verbose --reporter=json --threads=1
EOF
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
export CI=true
pnpm run test -- --run --verbose --reporter=json --threads=1 --timeout=300000
 timeout 300s pnpm exec tsx script/create-test-e2e.ts
 timeout 300s pnpm exec tsx script/initialize-test-e2e.ts
pnpm run test:migrate -- --run --verbose --reporter=json --threads=1 --timeout=300000
EOF
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential python3
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
export CI=true
# Combine Vitest tests to reduce setup overhead
pnpm run test -- --run --verbose --threads=2 ./test/... ./script/...
# Run e2e tests in parallel to cut execution time
(timeout 300s pnpm exec tsx script/create-test-e2e.ts) &
(timeout 300s pnpm exec tsx script/initialize-test-e2e.ts) &
wait
EOF
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
export CI=true
# Run all Vitest tests (unit + migrate) in one command with optimized threads
pnpm run test -- --run --verbose --threads=2 ./... script/
# Run e2e tests in parallel with timeouts to limit total runtime
(timeout 300s pnpm exec tsx script/create-test-e2e.ts) &
(timeout 300s pnpm exec tsx script/initialize-test-e2e.ts) &
wait
EOF
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
export CI=true
# Run main tests with limited threads and timeout
pnpm run test -- --run --verbose --threads=1 --timeout=300000
# Run e2e tests sequentially with strict timeouts
timeout 300s pnpm exec tsx script/create-test-e2e.ts
timeout 300s pnpm exec tsx script/initialize-test-e2e.ts
# Run migration tests
pnpm run test:migrate -- --run --verbose --threads=1 --timeout=300000
EOF
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
export CI=true
# Combine main and migration tests in one Vitest run to reduce overhead
pnpm run test -- --run --verbose --threads=1 --timeout=300000 ./... script/
# Run e2e tests with timeouts to limit total runtime
timeout 300s pnpm exec tsx script/create-test-e2e.ts
timeout 300s pnpm exec tsx script/initialize-test-e2e.ts
EOF
###ACTION_DELIMITER###
chmod +x test_commands.sh && cat > test_commands.sh << 'EOF'
#!/bin/bash
export CI=true
# Optimized Vitest run combining main and migration tests
pnpm run test -- --run --verbose --threads=1 --timeout=240000 ./... script/
# Parallel e2e tests with reduced timeouts to limit total runtime
(timeout 240s pnpm exec tsx script/create-test-e2e.ts) &
(timeout 240s pnpm exec tsx script/initialize-test-e2e.ts) &
wait
EOF
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
export CI=true
# Run Vitest on critical test directories with strict timeout
pnpm run test -- --run --verbose --threads=1 --timeout=240000 ./test/... ./script/
# Run e2e tests sequentially to avoid resource contention
timeout 240s pnpm exec tsx script/create-test-e2e.ts
timeout 240s pnpm exec tsx script/initialize-test-e2e.ts
EOF
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
export CI=true
# Run Vitest with 2 threads for faster execution, timeout after 20 minutes
pnpm run test -- --run --verbose --threads=2 --timeout=1200000 ./...
# Run e2e tests in parallel with 10-minute timeouts each
(timeout 600s pnpm exec tsx script/create-test-e2e.ts) &
(timeout 600s pnpm exec tsx script/initialize-test-e2e.ts) &
wait
EOF
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
export CI=true
# Run Vitest with 2 threads, 10-minute timeout
timeout 600s pnpm run test -- --run --verbose --threads=2 ./... || true
# Run e2e tests with 10-minute timeouts each
timeout 600s pnpm exec tsx script/create-test-e2e.ts || true
timeout 600s pnpm exec tsx script/initialize-test-e2e.ts || true
EOF
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
export CI=true
# Run all Vitest tests (including migration) with 1 thread, 15-minute timeout
pnpm run test -- --run --verbose --reporter=json --threads=1 --timeout=900000 ./...
# Run e2e tests in parallel with 15-minute total timeout
(timeout 900s pnpm exec tsx script/create-test-e2e.ts) &
(timeout 900s pnpm exec tsx script/initialize-test-e2e.ts) &
wait
EOF
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
export CI=true
# Combine all Vitest tests (main + migrate) with 2 threads, 15-minute timeout
 timeout 900s pnpm run test -- --run --verbose --threads=2 ./... script/
# Run e2e tests in parallel with 15-minute total timeout
(timeout 900s pnpm exec tsx script/create-test-e2e.ts) &
(timeout 900s pnpm exec tsx script/initialize-test-e2e.ts) &
wait
EOF
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
export CI=true
# Run main tests with 450s timeout
 timeout 450s pnpm run test -- --run --verbose --reporter=json --threads=1
# Run create e2e test with 450s timeout
 timeout 450s pnpm run test:create
# Run initialize e2e test with 450s timeout
 timeout 450s pnpm run test:initialize
# Run migration tests with 450s timeout
 timeout 450s pnpm run test:migrate -- --run --verbose --reporter=json --threads=1
EOF
###ACTION_DELIMITER###
cat > test_commands.sh << 'EOF'
#!/bin/bash
export CI=true
# Combine main and migration tests in one Vitest run
pnpm run test -- --run --verbose --threads=1 ./test/... ./script/
# Run e2e tests with local tsx to reduce overhead
pnpm exec tsx script/create-test-e2e.ts
pnpm exec tsx script/initialize-test-e2e.ts
EOF""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
export CI=true
# Combine main and migration tests in one Vitest run
pnpm run test -- --run --verbose --threads=1 ./test/... ./script/
# Run e2e tests with local tsx to reduce overhead
pnpm exec tsx script/create-test-e2e.ts
pnpm exec tsx script/initialize-test-e2e.ts

""".replace("[[REPO_NAME]]", repo_name),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
if ! git -C /home/[[REPO_NAME]] apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
#!/bin/bash
export CI=true
# Combine main and migration tests in one Vitest run
pnpm run test -- --run --verbose --threads=1 ./test/... ./script/
# Run e2e tests with local tsx to reduce overhead
pnpm exec tsx script/create-test-e2e.ts
pnpm exec tsx script/initialize-test-e2e.ts

""".replace("[[REPO_NAME]]", repo_name),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
if ! git -C /home/[[REPO_NAME]] apply --whitespace=nowarn  /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
#!/bin/bash
export CI=true
# Combine main and migration tests in one Vitest run
pnpm run test -- --run --verbose --threads=1 ./test/... ./script/
# Run e2e tests with local tsx to reduce overhead
pnpm exec tsx script/create-test-e2e.ts
pnpm exec tsx script/initialize-test-e2e.ts

""".replace("[[REPO_NAME]]", repo_name),
            ),
        ]

    def dockerfile(self) -> str:
        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        dockerfile_content = """
# This is a template for creating a Dockerfile to test patches
# LLM should fill in the appropriate values based on the context

# Choose an appropriate base image based on the project's requirements - replace node:20 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:20

## Set noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Install basic requirements
# For example: RUN apt-get update && apt-get install -y git
# For example: RUN yum install -y git
# For example: RUN apk add --no-cache git
RUN apt-get update && apt-get install -y git

# Ensure bash is available
RUN if [ ! -f /bin/bash ]; then         if command -v apk >/dev/null 2>&1; then             apk add --no-cache bash;         elif command -v apt-get >/dev/null 2>&1; then             apt-get update && apt-get install -y bash;         elif command -v yum >/dev/null 2>&1; then             yum install -y bash;         else             exit 1;         fi     fi

WORKDIR /home/
COPY fix.patch /home/
COPY test.patch /home/
RUN git clone https://github.com/JoshuaKGoldberg/create-typescript-app.git /home/create-typescript-app

WORKDIR /home/create-typescript-app
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("JoshuaKGoldberg", "create_typescript_app_1470_to_1173")
class CREATE_TYPESCRIPT_APP_1470_TO_1173(Instance):
    def __init__(self, pr: PullRequest, config: Config, *args, **kwargs):
        super().__init__()
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    def dependency(self) -> Optional[Image]:
        return ImageDefault(self.pr, self._config)

    def run(self, run_cmd: str = "") -> str:
        if run_cmd:
            return run_cmd

        return "bash /home/run.sh"

    def test_patch_run(self, test_patch_run_cmd: str = "") -> str:
        if test_patch_run_cmd:
            return test_patch_run_cmd

        return "bash /home/test-run.sh"

    def fix_patch_run(self, fix_patch_run_cmd: str = "") -> str:
        if fix_patch_run_cmd:
            return fix_patch_run_cmd

        return "bash /home/fix-run.sh"

    def parse_log(self, log: str) -> TestResult:
        # Parse the log content and extract test execution results.
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        import json

        # Strip ANSI escape codes from the log content
        log_clean = re.sub(r"\x1b\[[0-9;]*m", "", log)
        # Extract test names using regex patterns
        # Passed tests are marked with ✓
        passed_matches = re.findall(r"^\s*✓\s+(.*?)\s*\(", log_clean, re.MULTILINE)
        passed_tests.update([match.strip() for match in passed_matches])
        # Failed tests are marked with ❯
        failed_matches = re.findall(r"^\s*❯\s+(.*?)\s*\(", log_clean, re.MULTILINE)
        failed_tests.update([match.strip() for match in failed_matches])
        parsed_results = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
        }

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
