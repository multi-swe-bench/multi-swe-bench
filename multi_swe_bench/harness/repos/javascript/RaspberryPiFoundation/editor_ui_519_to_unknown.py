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
        return "ubuntu:latest"
    
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
                """ls
###ACTION_DELIMITER###
node -v
###ACTION_DELIMITER###
apt-get update && apt-get install -y nodejs npm
###ACTION_DELIMITER###
node -v
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo 'ulimit -n 4096 && yarn test --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'ulimit -n 8192 && yarn test --verbose --maxWorkers=2 --testTimeout=30000' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'ulimit -n 8192 && yarn test -- --verbose --maxWorkers=2 --testTimeout=30000' > test_commands.sh
###ACTION_DELIMITER###
echo 'ulimit -n 16384 && yarn test --verbose --maxWorkers=4 --testTimeout=60000' > test_commands.sh
###ACTION_DELIMITER###
echo 'ulimit -n 16384 && yarn test -- --verbose --maxWorkers=1 --testTimeout=60000' > test_commands.sh
###ACTION_DELIMITER###
echo 'ulimit -n 16384 && yarn test -- --verbose --watchAll=false --maxWorkers=2 --testTimeout=60000' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
ulimit -n 16384 && yarn test -- --verbose --watchAll=false --maxWorkers=2 --testTimeout=60000

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
ulimit -n 16384 && yarn test -- --verbose --watchAll=false --maxWorkers=2 --testTimeout=60000

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
ulimit -n 16384 && yarn test -- --verbose --watchAll=false --maxWorkers=2 --testTimeout=60000

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:latest with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:latest

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
RUN git clone https://github.com/RaspberryPiFoundation/editor-ui.git /home/editor-ui

WORKDIR /home/editor-ui
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("RaspberryPiFoundation", "editor_ui_519_to_unknown")
class EDITOR_UI_519_TO_UNKNOWN(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re
        import json
        # Extract test names, failed, and skipped tests
        # Match test/it definitions (handles leading characters)
        test_pattern = re.compile(r".*?(test|it)\s*\(\s*['\"]([^'\"]+)['\"]\s*,")  # Captures test('...', ...) with comma
        # Match skipped tests (xtest/xit) with comma
        skipped_pattern = re.compile(r".*?(xtest|xit)\s*\(\s*['\"]([^'\"]+)['\"]\s*,")  # Captures xtest('...', ...)
        # Match error lines (e.g., '> 34 | ...')
        error_line_pattern = re.compile(r".*>\s+\d+")  # Simplified to match '> ' followed by number
        lines = log.split('\n')
        all_tests = set()
        current_test = None
        # Process lines in forward order to capture tests before errors
        for line in lines:
            # Capture skipped tests
            skipped_match = skipped_pattern.search(line)
            if skipped_match:
                skipped_test = skipped_match.group(2).strip()
                skipped_tests.add(skipped_test)
                continue
            # Capture test/it names and track current test
            test_match = test_pattern.search(line)
            if test_match:
                current_test = test_match.group(2).strip()
                all_tests.add(current_test)
            # Mark current test as failed if error line is found
            if error_line_pattern.search(line) and current_test:
                failed_tests.add(current_test)
                current_test = None  # Reset to avoid misattribution
        # Passed tests = all tests - failed - skipped
        passed_tests = all_tests - failed_tests - skipped_tests
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
