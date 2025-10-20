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
pip install .[dev]
###ACTION_DELIMITER###
hatch install dev
###ACTION_DELIMITER###
pip install hatch
###ACTION_DELIMITER###
hatch install dev
###ACTION_DELIMITER###
hatch -h
###ACTION_DELIMITER###
hatch dep install dev
###ACTION_DELIMITER###
hatch run pytest --version
###ACTION_DELIMITER###
hatch test
###ACTION_DELIMITER###
hatch run dev:pytest
###ACTION_DELIMITER###
hatch run +dev pytest
###ACTION_DELIMITER###
pip install hypothesis pylama setuptools
###ACTION_DELIMITER###
pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
pytest --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
pip install hypothesmith
###ACTION_DELIMITER###
pip install black
###ACTION_DELIMITER###
pytest --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pytest --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
pytest --no-header -rA -p no:cacheprovider -v
###ACTION_DELIMITER###
pip install colorama
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v --no-header -rA --tb=no -p no:cacheprovider

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider

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
RUN git clone https://github.com/PyCQA/isort.git /home/isort

WORKDIR /home/isort
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("PyCQA", "isort_2331_to_2136")
class ISORT_2331_TO_2136(Instance):
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
        passed_tests = set() # Tests that passed successfully
        failed_tests = set() # Tests that failed
        skipped_tests = set() # Tests that were skipped
        import re
        # Regex patterns to match test cases with status
        # Pattern 1: test name followed by status (e.g., "tests/...::test_name PASSED")
        # Captures test names with .py::test or .py:line_number, stops at first whitespace before status
        pattern1 = re.compile(r'(?P<test_name>tests/.*?\.py::[^\s]+|tests/.*?\.py:[0-9]+)\s+(?P<status>PASSED|FAILED|SKIPPED|XFAIL|ERROR)')
        # Pattern 2: status followed by test name (e.g., "PASSED tests/...::test_name")
        # Allows optional [1] after status, captures test names with .py::test or .py:line_number
        pattern2 = re.compile(r'(?P<status>PASSED|FAILED|SKIPPED|XFAIL|ERROR)\s+\[?\d*]?\s*(?P<test_name>tests/.*?\.py::[^\s]+|tests/.*?\.py:[0-9]+)')
        # Track test statuses, overwriting with later entries (e.g., summary)
        test_statuses = {}
        # Process matches from pattern1
        for match in pattern1.finditer(log):
            test_name = match.group('test_name').strip()
            status = match.group('status').strip()
            test_statuses[test_name] = status
        # Process matches from pattern2
        for match in pattern2.finditer(log):
            test_name = match.group('test_name').strip()
            status = match.group('status').strip()
            test_statuses[test_name] = status
        # Populate sets based on final statuses
        for test_name, status in test_statuses.items():
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ['FAILED', 'ERROR', 'XFAIL']:
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
