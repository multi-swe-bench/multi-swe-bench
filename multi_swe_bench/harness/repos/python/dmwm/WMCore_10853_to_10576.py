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
        return "python:3.9-slim"
    
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
                """cat README.md
###ACTION_DELIMITER###
cat CONTRIBUTING.rst
###ACTION_DELIMITER###
ls -la
###ACTION_DELIMITER###
cat setup_test.py
###ACTION_DELIMITER###
ls -la test
###ACTION_DELIMITER###
cat requirements_py3.txt
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y build-essential libcurl4-openssl-dev default-libmysqlclient-dev libssl-dev libaio1
###ACTION_DELIMITER###
pip3 install -r requirements_py3.txt
###ACTION_DELIMITER###
sed -i 's/rucio-clients==1.25.5/rucio-clients>=1.29.0/' requirements_py3.txt
###ACTION_DELIMITER###
pip3 install -r requirements_py3.txt
###ACTION_DELIMITER###
python3 setup.py test -v
###ACTION_DELIMITER###
pip3 install -e .
###ACTION_DELIMITER###
nose2 -v test/python
###ACTION_DELIMITER###
python3 setup.py test -v
###ACTION_DELIMITER###
echo 'python3 setup.py test -v' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
python3 setup.py test -v

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
python3 setup.py test -v

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
python3 setup.py test -v

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.9-slim

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
RUN git clone https://github.com/dmwm/WMCore.git /home/WMCore

WORKDIR /home/WMCore
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("dmwm", "WMCore_10853_to_10576")
class WMCORE_10853_TO_10576(Instance):
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
        # Unified pattern to match test cases and their statuses (SKIP/ERROR/FAILED/PASSED/PASS/OK)
        test_pattern = re.compile(r'(?:\[\s*\d+\]\s+)?#\d+\s+(.*?)\s+\.\.\.\s+(SKIP|ERROR|FAILED|FAIL|PASSED|PASS|OK)', re.IGNORECASE)
        test_name_pattern = re.compile(r'#\d+\s+(.*?)\s+\.\.\.\s+', re.IGNORECASE)
        # Pattern to match ERROR lines (e.g., "ERROR: testName")
        error_pattern = re.compile(r'(?:\[\s*\d+\]\s+)?(ERROR|FAILED):\s+(.*?)\s*$', re.IGNORECASE)
        # Track test statuses to resolve conflicts (latest status takes precedence)
        test_status = {}
        # Extract tests from unified pattern
        for match in test_pattern.findall(log):
            test_name = match[0].strip()
            status = match[1].upper()
            test_status[test_name] = status
        # Extract ERROR/FAILED tests
        for status, test_name in error_pattern.findall(log):
            test_name = test_name.strip()
            if test_name:
                test_status[test_name] = status.upper()
        # Extract all test names and assume unmarked ones are passed
        for match in test_name_pattern.findall(log):
            test_name = match.strip()
            if test_name and test_name not in test_status:
                test_status[test_name] = 'PASSED'
        # Categorize tests based on final status
        for test_name, status in test_status.items():
            if status in ('PASSED', 'PASS', 'OK'):
                passed_tests.add(test_name)
            elif status in ('SKIP',):
                skipped_tests.add(test_name)
            elif status in ('ERROR', 'FAILED', 'FAIL'):
                failed_tests.add(test_name)
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
