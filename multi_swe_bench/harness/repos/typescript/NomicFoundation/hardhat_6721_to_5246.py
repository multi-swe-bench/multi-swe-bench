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
        return "node:20-bullseye-slim"
    
    def image_prefix(self) -> str:
        return "envagent"
       
    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:
        repo_name= self.pr.repo
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
                """npm install -g pnpm
###ACTION_DELIMITER###
pnpm install
###ACTION_DELIMITER###
pnpm build
###ACTION_DELIMITER###
echo 'pnpm run --recursive --workspace-concurrency 1 --no-bail test -- --verbose' > /home/hardhat/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm run --recursive --workspace-concurrency 1 --no-bail test -- --verbose' > /home/hardhat/test_commands.sh
###ACTION_DELIMITER###
chmod +x /home/hardhat/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
pnpm run --recursive --workspace-concurrency 1 --no-bail test -- --verbose

""".replace("[[REPO_NAME]]", repo_name)
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
pnpm run --recursive --workspace-concurrency 1 --no-bail test -- --verbose

""".replace("[[REPO_NAME]]", repo_name)
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
pnpm run --recursive --workspace-concurrency 1 --no-bail test -- --verbose

""".replace("[[REPO_NAME]]", repo_name)
            ),
        ]

    def dockerfile(self) -> str:
        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        dockerfile_content = """
# This is a template for creating a Dockerfile to test patches
# LLM should fill in the appropriate values based on the context

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:20-bullseye-slim

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
RUN git clone https://github.com/NomicFoundation/hardhat.git /home/hardhat

WORKDIR /home/hardhat
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("NomicFoundation", "hardhat_6721_to_5246")
class HARDHAT_6721_TO_5246(Instance):
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

        return 'bash /home/run.sh'

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
        passed_tests = set[str]() # Tests that passed successfully
        failed_tests = set[str]() # Tests that failed
        skipped_tests = set[str]() # Tests that were skipped
        import re
        import json
        # Refined regex to capture test names without symbols
        passed_pattern = re.compile(r'^\s*✔\s+(.*?)\s*$')  # Matches lines starting with ✔
        failed_pattern = re.compile(r'fail|error', re.IGNORECASE)
        summary_pattern = re.compile(r'Summary: (\d+) fails')
        lines = log.split('\n')
        failed_count = 0
        for i, line in enumerate(lines):
            # Extract passed tests
            passed_match = passed_pattern.search(line)
            if passed_match:
                test_name = passed_match.group(1).strip()
                passed_tests.add(test_name)
            # Detect summary failure count
            summary_match = summary_pattern.search(line)
            if summary_match:
                failed_count = int(summary_match.group(1))
            # Extract failed tests (capture test names preceding error messages)
            if failed_pattern.search(line) and i > 0:
                # Check if previous line is a test name (avoids capturing non-test errors)
                prev_line = lines[i-1].strip()
                if prev_line and not failed_pattern.search(prev_line) and (prev_line.startswith(('Should', 'should', 'Handles', 'handles', 'Test', 'test'))):
                    # Remove trailing colon and strip whitespace
                    test_name = prev_line.rstrip(':').strip()
                    failed_tests.add(test_name)
                # Capture exit status indicating failure
                elif 'exit status' in line.lower() and failed_count > 0:
                    test_name = 'Hardhat core test suite'
                    failed_tests.add(test_name)
        # Add skipped tests if patterns exist (e.g., 'SKIPPED' keyword)
        skipped_pattern = re.compile(r'^\s*SKIPPED\s+(.*?)\s*$')
        for line in lines:
            skipped_match = skipped_pattern.search(line)
            if skipped_match:
                test_name = skipped_match.group(1).strip()
                skipped_tests.add(test_name)
        parsed_results = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests
        }
        

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
