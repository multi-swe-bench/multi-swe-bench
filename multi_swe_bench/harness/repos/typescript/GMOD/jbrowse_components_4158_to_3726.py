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
                """yarn install
###ACTION_DELIMITER###
yarn build
###ACTION_DELIMITER###
yarn test --verbose
###ACTION_DELIMITER###
apt-get update && apt-get install -y tabix
###ACTION_DELIMITER###
apt-get install -y samtools
###ACTION_DELIMITER###
echo 'yarn test --verbose' > /home/jbrowse-components/test_commands.sh
###ACTION_DELIMITER###
cat /home/jbrowse-components/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn test --verbose

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
yarn test --verbose

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
yarn test --verbose

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
RUN git clone https://github.com/GMOD/jbrowse-components.git /home/jbrowse-components

WORKDIR /home/jbrowse-components
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("GMOD", "jbrowse_components_4158_to_3726")
class JBROWSE_COMPONENTS_4158_TO_3726(Instance):
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
        # Extract test suite paths (PASS/FAIL) and test cases
        import re
        suite_pattern = re.compile(r'^(PASS|FAIL) (.*?)(?: \(\d+\.\d+ s\))?$', re.MULTILINE)
        # Capture test cases with symbols (✓/✗/×/-) and stack traces with function names
        test_case_pattern = re.compile(r'^\s+([✓✗×-])\s+(.*?)(?:\s+\(\d+ ms\))?$', re.MULTILINE)  # Indented test cases with symbols
        failed_test_pattern = re.compile(r'^\s*\[\d+\]\s+at\s+([^\s(]+)\s*\((.*?test\.(tsx?|js))[:\d]*\)', re.IGNORECASE | re.MULTILINE)  # Captures function and test file
        current_suite = None
        test_status = {}
        for line in log.split('\n'):
            # Update current suite on PASS/FAIL lines
            suite_match = suite_pattern.match(line)
            if suite_match:
                current_suite = suite_match.group(2)
                suite_status = suite_match.group(1)
            # Capture standard test cases
            test_match = test_case_pattern.match(line)
            if test_match and current_suite:
                symbol = test_match.group(1)
                test_name = f"{current_suite} {test_match.group(2)}"
                if symbol == '✓':
                    test_status[test_name] = 'passed'
                elif symbol in ('✗', '×'):
                    test_status[test_name] = 'failed'
                elif symbol == '-':
                    test_status[test_name] = 'skipped'
                # Override with suite status if suite is failed
                if suite_status == 'FAIL':
                    test_status[test_name] = 'failed'
            # Capture failed tests from stack traces
            failed_match = failed_test_pattern.match(line)
            if failed_match:
                test_file = failed_match.group(2)
                test_func = failed_match.group(1)
                test_name = f"{test_file} {test_func}"
                test_status[test_name] = 'failed'
        # Populate sets from the test_status dictionary
        for test_name, status in test_status.items():
            if status == 'passed':
                passed_tests.add(test_name)
            elif status == 'failed':
                failed_tests.add(test_name)
            elif status == 'skipped':
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
