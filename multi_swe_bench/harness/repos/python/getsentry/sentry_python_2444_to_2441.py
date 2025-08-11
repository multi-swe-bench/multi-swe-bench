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
                """python -m venv .venv
###ACTION_DELIMITER###
source .venv/bin/activate
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install -r requirements-devenv.txt
###ACTION_DELIMITER###
pre-commit install
###ACTION_DELIMITER###
echo 'pytest -v -rA tests/' > /home/sentry-python/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v -rA tests/

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
pytest -v -rA tests/

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
pytest -v -rA tests/

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
RUN git clone https://github.com/getsentry/sentry-python.git /home/sentry-python

WORKDIR /home/sentry-python
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("getsentry", "sentry_python_2444_to_2441")
class SENTRY_PYTHON_2444_TO_2441(Instance):
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
        # Regex patterns to match test names and statuses
        passed_pattern = re.compile(r'^(tests/[\w/]+\.py::test_\w+)\s+PASSED$')
        passed_next_line_pattern = re.compile(r'^tests/[\w/]+\.py::test_\w+$')
        failed_pattern = re.compile(r'^FAILED\s+(tests/[\w/]+\.py::test_\w+)')
        skipped_same_line_pattern = re.compile(r'^(tests/[\w/]+\.py::test_\w+)\s+SKIPPED$')
        skipped_prefix_pattern = re.compile(r'^SKIPPED\s+\[\d+\]\s+(tests/[\w/]+\.py::test_\w+)')
        lines = log.splitlines()
        for i in range(len(lines)):
            line = lines[i].strip()
            # Check for passed tests (current line)
            passed_match = passed_pattern.match(line)
            if passed_match:
                test_name = passed_match.group(1)
                passed_tests.add(test_name)
                continue
            # Check for passed tests (next line)
            if passed_next_line_pattern.match(line):
                if i + 1 < len(lines) and lines[i+1].strip() == 'PASSED':
                    passed_tests.add(line.strip())
                    continue
            # Check for failed tests
            failed_match = failed_pattern.match(line)
            if failed_match:
                test_name = failed_match.group(1)
                failed_tests.add(test_name)
                continue
            # Check for skipped tests (same line)
            skipped_same_match = skipped_same_line_pattern.match(line)
            if skipped_same_match:
                test_name = skipped_same_match.group(1)
                skipped_tests.add(test_name)
                continue
            # Check for skipped tests (prefix)
            skipped_prefix_match = skipped_prefix_pattern.match(line)
            if skipped_prefix_match:
                test_name = skipped_prefix_match.group(1)
                skipped_tests.add(test_name)
                continue
        # Ensure no overlaps (exclusive sets)
        passed_tests -= failed_tests | skipped_tests
        failed_tests -= passed_tests | skipped_tests
        skipped_tests -= passed_tests | failed_tests
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
