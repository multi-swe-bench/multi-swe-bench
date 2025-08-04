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
pip install -e .[dev,docs]
###ACTION_DELIMITER###
./run-tests.py
###ACTION_DELIMITER###
./run-tests.py --quick
###ACTION_DELIMITER###
./run-tests.py --unit
###ACTION_DELIMITER###
pip install 'numpy<2.0'
###ACTION_DELIMITER###
./run-tests.py --unit
###ACTION_DELIMITER###
echo "./run-tests.py --unit" > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
./run-tests.py --unit

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
./run-tests.py --unit

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn  /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
./run-tests.py --unit

""".format(
                    pr=self.pr
                ),
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
RUN git clone https://github.com/pints-team/pints.git /home/pints

WORKDIR /home/pints
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pints-team", "pints_1424_to_759")
class PINTS_1424_TO_759(Instance):
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
        current_test_name = None
        # Regex patterns for standard test lines and summary lines
        statuses = {'ok', 'PASSED', 'FAIL', 'FAILED', 'SKIPPED', 'ERROR'}
        for line in log.split('\n'):
            line = line.rstrip('\r').strip()
            if '...' in line:
                # Split into test part and status part
                test_part, status_part = line.split('...', 1)
                # Extract test name (remove line number)
                if ']' in test_part:
                    test_name = test_part.split(']', 1)[1].strip()
                else:
                    test_name = test_part.strip()
                status_part = status_part.strip()
                # Check if status is on the same line
                if status_part in statuses:
                    if status_part in {'ok', 'PASSED'}:
                        passed_tests.add(test_name)
                    elif status_part in {'FAIL', 'FAILED', 'ERROR'}:
                        failed_tests.add(test_name)
                    elif status_part in {'SKIPPED'}:
                        skipped_tests.add(test_name)
                else:
                    # Track test name for status on subsequent lines
                    current_test_name = test_name
                continue
            # Handle summary lines (e.g., [971] FAIL: test_name)
            elif 'FAIL:' in line or 'ERROR:' in line:
                if ']' in line:
                    part = line.split(']', 1)[1].strip()
                    if part.startswith(('FAIL:', 'ERROR:')):
                        test_name = part.split(':', 1)[1].strip()
                        failed_tests.add(test_name)
                continue
            # Handle multi-line statuses
            elif current_test_name is not None:
                # Check if current line contains the status (with or without line number)
                if ']' in line:
                    status_part = line.split(']', 1)[1].strip()
                else:
                    status_part = line.strip()
                if status_part in statuses:
                    if status_part in {'ok', 'PASSED'}:
                        passed_tests.add(current_test_name)
                    elif status_part in {'FAIL', 'FAILED', 'ERROR'}:
                        failed_tests.add(current_test_name)
                    elif status_part in {'SKIPPED'}:
                        skipped_tests.add(current_test_name)
                    current_test_name = None
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
