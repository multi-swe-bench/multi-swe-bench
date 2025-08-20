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
                """cat README.md
###ACTION_DELIMITER###
cat CONTRIBUTING.md
###ACTION_DELIMITER###
apt-get update && apt-get install -y libsndfile1 ffmpeg
###ACTION_DELIMITER###
pip install --upgrade pip && pip install -e '.[dev]'
###ACTION_DELIMITER###
cat pyproject.toml
###ACTION_DELIMITER###
echo 'pytest -v -rA' > /home/haystack/test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -s -rA --durations=0' > /home/haystack/test_commands.sh
###ACTION_DELIMITER###
cat /home/haystack/test_commands.sh
###ACTION_DELIMITER###
echo 'pytest haystack/ -v -s -rA -n auto' > /home/haystack/test_commands.sh
###ACTION_DELIMITER###
echo 'pytest test/ -v -s -rA -n auto' > /home/haystack/test_commands.sh
###ACTION_DELIMITER###
bash /home/haystack/test_commands.sh
###ACTION_DELIMITER###
pip list | grep pytest
###ACTION_DELIMITER###
pip install -e '.[dev]'
###ACTION_DELIMITER###
pip install pytest pytest-cov pytest-custom_exit_code pytest-asyncio pytest-rerunfailures responses
###ACTION_DELIMITER###
bash /home/haystack/test_commands.sh
###ACTION_DELIMITER###
pip install pytest-xdist
###ACTION_DELIMITER###
bash /home/haystack/test_commands.sh
###ACTION_DELIMITER###
pip install torch
###ACTION_DELIMITER###
bash /home/haystack/test_commands.sh
###ACTION_DELIMITER###
echo 'export HAYSTACK_LOGGING_JSON=true && pytest test/ -v -s -rA -n auto' > /home/haystack/test_commands.sh
###ACTION_DELIMITER###
bash /home/haystack/test_commands.sh
###ACTION_DELIMITER###
echo 'HAYSTACK_LOGGING_JSON=true pytest test/ -v -s -rA -n auto' > /home/haystack/test_commands.sh
###ACTION_DELIMITER###
bash /home/haystack/test_commands.sh
###ACTION_DELIMITER###
pip install python-json-logger
###ACTION_DELIMITER###
bash /home/haystack/test_commands.sh
###ACTION_DELIMITER###
echo -e 'export HAYSTACK_LOGGING_JSON=true
pytest test/ -v -s -rA -n auto' > /home/haystack/test_commands.sh
###ACTION_DELIMITER###
bash /home/haystack/test_commands.sh
###ACTION_DELIMITER###
echo -e 'export HAYSTACK_LOGGING_JSON=true
echo "HAYSTACK_LOGGING_JSON is set to $HAYSTACK_LOGGING_JSON"
pytest test/test_logging.py::TestStructuredLoggingJSONRendering::test_logging_as_json -v -s' > /home/haystack/test_commands.sh
###ACTION_DELIMITER###
bash /home/haystack/test_commands.sh
###ACTION_DELIMITER###
pip install structlog
###ACTION_DELIMITER###
echo -e 'export HAYSTACK_LOGGING_JSON=true
pytest test/test_logging.py::TestStructuredLoggingJSONRendering::test_logging_as_json -v -s -rA' > /home/haystack/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
export HAYSTACK_LOGGING_JSON=true
pytest test/test_logging.py::TestStructuredLoggingJSONRendering::test_logging_as_json -v -s -rA

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
export HAYSTACK_LOGGING_JSON=true
pytest test/test_logging.py::TestStructuredLoggingJSONRendering::test_logging_as_json -v -s -rA

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
export HAYSTACK_LOGGING_JSON=true
pytest test/test_logging.py::TestStructuredLoggingJSONRendering::test_logging_as_json -v -s -rA

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
RUN git clone https://github.com/deepset-ai/haystack.git /home/haystack

WORKDIR /home/haystack
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("deepset-ai", "haystack_7709_to_unknown")
class HAYSTACK_7709_TO_UNKNOWN(Instance):
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
        import json
        lines = log.split('\n')
        current_test = None
        # Regex patterns
        test_name_pattern = re.compile(r'^([\w\/]+\.py::[\w:]+)\s*$')
        test_status_same_line = re.compile(r'^([\w\/]+\.py::[\w:]+)\s+(PASSED|SKIPPED|FAILED)\s+\[\s*\d+%?\]')
        status_first_pattern = re.compile(r'^(FAILED|ERROR)\s+([\w\/]+\.py::[\w:]+)')
        status_line_pattern = re.compile(r'^(PASSED|SKIPPED|FAILED)\s+\[\s*\d+%?\]')
        for line in lines:
            # Check if line is a test name (standalone)
            match = test_name_pattern.match(line)
            if match:
                current_test = match.group(1)
                continue
            # Check if line has test name and status on the same line
            match = test_status_same_line.match(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
                current_test = None
                continue
            # Check if line has status first (FAILED/ERROR) followed by test name
            match = status_first_pattern.match(line)
            if match:
                status = match.group(1)
                test_name = match.group(2)
                if status in ['FAILED', 'ERROR']:
                    failed_tests.add(test_name)
                current_test = None
                continue
            # Check if line is a status line (after a standalone test name)
            match = status_line_pattern.match(line)
            if match and current_test is not None:
                status = match.group(1)
                if status == 'PASSED':
                    passed_tests.add(current_test)
                elif status == 'SKIPPED':
                    skipped_tests.add(current_test)
                elif status == 'FAILED':
                    failed_tests.add(current_test)
                current_test = None
                continue
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
