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
                """ls -la
###ACTION_DELIMITER###
npm install -g pnpm
###ACTION_DELIMITER###
pnpm install
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm run test -- --verbose
pnpm run test:create
pnpm run test:initialize
pnpm run test:migrate' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm run test -- --verbose --run
pnpm run test:create
pnpm run test:initialize
pnpm run test:migrate' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm run test -- --verbose --run' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm run test -- --verbose --run --maxWorkers=4' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm run test -- --verbose --run --maxWorkers=auto --reporter=json' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm run test -- --run --maxWorkers=auto --reporter=json --ci' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm run test -- --run --ci --maxWorkers=auto --reporter=json --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm run test -- --run --ci --maxWorkers=2 --reporter=json --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm run test -- --run --ci --maxWorkers=1 --reporter=json --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm run test -- --ci --maxWorkers=2 --reporter=json --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm run test -- --ci --maxWorkers=2 --reporter=json-stream --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm run test -- --ci --maxWorkers=1 --reporter=json-stream --exit' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm run test --silent -- --ci --maxWorkers=2 --reporter=json-stream --exit' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm run test --silent -- --ci --maxWorkers=1 --reporter=json --exit' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm run test -- --run --ci --maxWorkers=1 --reporter=json' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm run test --silent -- --ci --maxWorkers=2 --reporter=json-stream' > test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
ls -la .github/workflows
###ACTION_DELIMITER###
ls -la .github/actions/prepare
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl && curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && nvm install 18 && nvm use 18 && pnpm install --frozen-lockfile && echo -e '#!/bin/bash
pnpm run test --coverage --ci --maxWorkers=auto' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
CI=true pnpm run test --coverage --maxWorkers=auto' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
CI=true pnpm run test -- --coverage --max-workers=auto' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
CI=true pnpm run test -- --coverage --max-workers=auto --reporter=json' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
CI=true pnpm run test -- --coverage --max-workers=auto --reporter=json

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
CI=true pnpm run test -- --coverage --max-workers=auto --reporter=json

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
CI=true pnpm run test -- --coverage --max-workers=auto --reporter=json

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


@Instance.register("JoshuaKGoldberg", "create_typescript_app_1149_to_513")
class CREATE_TYPESCRIPT_APP_1149_TO_513(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re

        # Pattern for passed tests: matches lines with ✓, captures test file path
        passed_pattern = re.compile(r"\x1b\[32m✓\x1b\[39m\s+([^\s]+)")
        passed_tests = set(passed_pattern.findall(log))
        # Pattern for failed tests: matches lines with ❯, captures test file path
        failed_pattern = re.compile(r"\x1b\[33m❯\x1b\[39m\s+([^\s]+)")
        failed_tests = set(failed_pattern.findall(log))
        # Skipped tests: no examples in logs, so leaving empty
        skipped_tests = set()
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
