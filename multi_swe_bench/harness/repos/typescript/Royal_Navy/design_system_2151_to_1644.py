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
        return "node:20-bookworm"
    
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
                """ls -la
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
###ACTION_DELIMITER###
nvm install
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
yarn test
###ACTION_DELIMITER###
yarn build
###ACTION_DELIMITER###
yarn test
###ACTION_DELIMITER###
echo 'yarn test' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn test

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
yarn test

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
yarn test

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
FROM node:20-bookworm

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
RUN git clone https://github.com/Royal-Navy/design-system.git /home/design-system

WORKDIR /home/design-system
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Royal-Navy", "design_system_2151_to_1644")
class DESIGN_SYSTEM_2151_TO_1644(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        # Add patterns for file-level test results (handles prefixes like 'royalnavy.io: ')
        result_patterns = [
            (re.compile(r'PASS\s+(.*\.test\.[jt]sx?)', re.IGNORECASE), 'passed'),
            (re.compile(r'FAIL\s+(.*\.test\.[jt]sx?)', re.IGNORECASE), 'failed'),
            (re.compile(r'SKIP\s+(.*\.test\.[jt]sx?)', re.IGNORECASE), 'skipped'),
            (re.compile(r'✓\s+(.*)'), 'passed'),
            (re.compile(r'✕\s+(.*)'), 'failed'),
            (re.compile(r'○\s+(.*)'), 'skipped')
        ]
        current_test = None
        for line in log.split('\n'):
            # Parse file-level results
            for pattern, status in result_patterns:
                match = pattern.search(line)
                if match:
                    test_file = match.group(1).strip()
                    if status == 'passed':
                        passed_tests.add(test_file)
                    elif status == 'failed':
                        failed_tests.add(test_file)
                    elif status == 'skipped':
                        skipped_tests.add(test_file)
                    break
            # Capture skipped tests (handles it.skip/test.skip with quotes/backticks)
            skip_match = re.search(r'''(it|test)\.skip\(\s*["'`](.*?)["'`]''', line)
            if skip_match:
                test_name = skip_match.group(2).strip()
                skipped_tests.add(test_name)
                current_test = None
                continue
            # Capture test names from it/test blocks (ignores prefixes, handles quotes/backticks)
            test_match = re.search(r'''(?:.*?)(it|test)\(\s*["'`](.*?)["'`]''', line)
            if test_match:
                current_test = test_match.group(2).strip()
                passed_tests.add(current_test)  # Assume pass initially
            # Detect failed tests ('>' in stack traces + Jest's failure markers)
            if current_test and ('>' in line or 'failed' in line.lower()):
                passed_tests.discard(current_test)
                failed_tests.add(current_test)
                current_test = None
            # Handle explicit SKIP in log lines (handles quotes/backticks)
            skip_line_match = re.search(r'''SKIP\s+.*?["'`](.*?)["'`]''', line)
            if skip_line_match:
                test_name = skip_line_match.group(1).strip()
                skipped_tests.add(test_name)
                current_test = None
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
