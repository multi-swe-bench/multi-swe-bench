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
        return "python:3.10-slim"
    
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
apt-get update
###ACTION_DELIMITER###
apt-get install -y build-essential
###ACTION_DELIMITER###
pip install .
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install pandas==1.5.3
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install numpy==1.24.4
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install pytest==6.2.5
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install nose && nosetests -v
###ACTION_DELIMITER###
pip install pytest==3.6.4 && pytest -v
###ACTION_DELIMITER###
python setup.py test -v
###ACTION_DELIMITER###
pip install pandas==1.1.5 numpy==1.19.5 pytest==4.6.11 && pytest pvlib/test -v
###ACTION_DELIMITER###
pip install pandas==1.3.5 numpy==1.21.6 pytest==5.4.3 && pytest -v
###ACTION_DELIMITER###
pip install pandas==1.3.5 numpy==1.21.6 pytest==6.2.5 && pytest -v --assert=plain
###ACTION_DELIMITER###
pip install pandas==1.3.5 numpy==1.21.6 pytest==6.2.5 pytest-nose && pytest -v --assert=plain --nose
###ACTION_DELIMITER###
pip install nose2 && nose2 -v
###ACTION_DELIMITER###
pip install pandas==1.3.5 numpy==1.21.6 nose2 && echo 'nose2 -v' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
nose2 -v

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
nose2 -v

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
nose2 -v

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
FROM python:3.10-slim

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
RUN git clone https://github.com/pvlib/pvlib-python.git /home/pvlib-python

WORKDIR /home/pvlib-python
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pvlib", "pvlib_python_219_to_unknown")
class PVLIB_PYTHON_219_TO_UNKNOWN(Instance):
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
        # Compile regex patterns for test statuses
        # Updated regex to capture test names with parameters (e.g., [simple])
        # Updated regex to fully capture test names with parameters
        # Updated regex to handle status followed by whitespace and progress indicators
        # Updated regex to ignore trailing progress indicators
        # Updated regex to match test lines with progress indicators
        # Updated regex to handle lines with or without progress indicators
        # Updated regex to fully capture test names with parameters
        # Updated regex to precisely capture test names with optional parameters
        # Updated regex to flexibly capture full test names with parameters
        # Updated regex to exclude trailing error messages and capture full test names
        # Updated regex to exclude trailing error messages by stopping at whitespace or end of line
        # Updated regex to stop at first whitespace after test name
        pattern1 = re.compile(r'^(pvlib/test/[^:]+::test_[^\s]+)\s+(PASSED|FAILED|SKIPPED|ERROR|XFAILED)(?:\s|$)')
        pattern2 = re.compile(r'^(PASSED|FAILED|SKIPPED|ERROR|XFAILED)\s+(pvlib/test/[^:]+::test_[^\s]+)(?:\s|$)')
        for line in log.splitlines():
            line = line.strip()
            # Check for test name followed by status
            match = pattern1.match(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
            else:
                # Check for status followed by test name
                match = pattern2.match(line)
                if match:
                    status = match.group(1)
                    test_name = match.group(2)
                else:
                    continue  # Skip lines that don't match
            # Categorize the test based on status
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ('FAILED', 'ERROR', 'XFAILED'):
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
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
