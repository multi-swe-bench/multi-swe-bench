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
        return "python:3.10-slim-bullseye"
    
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
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
pip install -r requirements-jammy.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libapt-pkg-dev
###ACTION_DELIMITER###
pip install -r requirements-jammy.txt
###ACTION_DELIMITER###
echo 'pytest -v --color=yes --cov=charmcraft --cov-config=pyproject.toml --cov-report=xml:results/coverage-test.xml --junit-xml=results/test-results.xml' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'mkdir -p results
pytest -v --color=yes --cov=charmcraft --cov-config=pyproject.toml --cov-report=xml:results/coverage-test.xml --junit-xml=results/test-results.xml' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
mkdir -p results
pytest -v --color=yes --cov=charmcraft --cov-config=pyproject.toml --cov-report=xml:results/coverage-test.xml --junit-xml=results/test-results.xml

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
mkdir -p results
pytest -v --color=yes --cov=charmcraft --cov-config=pyproject.toml --cov-report=xml:results/coverage-test.xml --junit-xml=results/test-results.xml

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
mkdir -p results
pytest -v --color=yes --cov=charmcraft --cov-config=pyproject.toml --cov-report=xml:results/coverage-test.xml --junit-xml=results/test-results.xml

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

# Choose an appropriate base image based on the project's requirements - replace python:3.10-slim-bullseye with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.10-slim-bullseye

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
RUN git clone https://github.com/canonical/charmcraft.git /home/charmcraft

WORKDIR /home/charmcraft
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("canonical", "charmcraft_1430_to_unknown")
class CHARMCRAFT_1430_TO_UNKNOWN(Instance):
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
        # Remove ANSI escape sequences
        clean_log = re.sub(r'\x1b\[[^m]*m', '', log)
        # Pattern for execution lines: e.g., "tests/test_actions.py::test_create_actions_yaml PASSED [  0%]"
        execution_pattern = re.compile(r'^(tests/.*?) (PASSED|FAILED|SKIPPED|XFAILED)(?:\s+\[|$)', re.MULTILINE)
        execution_matches = execution_pattern.findall(clean_log)
        for test_name, status in execution_matches:
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
        # Pattern for summary failed lines: e.g., "FAILED tests/test_infra.py::test_setup_version - AssertionError: ..."
        summary_failed_pattern = re.compile(r'^(FAILED) (tests/[^:]+::[^ ]+) -', re.MULTILINE)
        summary_failed_matches = summary_failed_pattern.findall(clean_log)
        for status, test_name in summary_failed_matches:
            failed_tests.add(test_name)
        # Pattern for summary skipped lines: e.g., "SKIPPED tests/test_foo.py::test_bar - ..."
        summary_skipped_pattern = re.compile(r'^(SKIPPED) (tests/[^:]+::[^ ]+) -', re.MULTILINE)
        summary_skipped_matches = summary_skipped_pattern.findall(clean_log)
        for status, test_name in summary_skipped_matches:
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
