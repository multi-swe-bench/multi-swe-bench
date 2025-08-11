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
make .develop
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make .develop
###ACTION_DELIMITER###
git submodule update --init
###ACTION_DELIMITER###
sed -i 's/git:\/\/github.com\/nodejs\/http-parser.git/https:\/\/github.com\/nodejs\/http-parser.git/' .gitmodules
###ACTION_DELIMITER###
git submodule update --init
###ACTION_DELIMITER###
git submodule sync && git submodule update --init
###ACTION_DELIMITER###
make .develop
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
make .develop
###ACTION_DELIMITER###
make vtest
###ACTION_DELIMITER###
pip install gunicorn
###ACTION_DELIMITER###
pip install 'setuptools<67.0'
###ACTION_DELIMITER###
make vtest
###ACTION_DELIMITER###
echo 'make vtest' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
make vtest

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
make vtest

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
make vtest

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
RUN git clone https://github.com/aio-libs/aiohttp.git /home/aiohttp

WORKDIR /home/aiohttp
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("aio-libs", "aiohttp_5249_to_5157")
class AIOHTTP_5249_TO_5157(Instance):
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
        test_status = {}  # Track latest status of each test
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        current_file = None
        current_test_name = None
        lines = log.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            prev_line = lines[i-1].strip() if i > 0 else ''
            # Capture current file from lines like "tests/test_run_app.py:428:"
            file_match = re.match(r'^(tests/.*?)\:\d+\:', line)
            if file_match:
                current_file = file_match.group(1)
                continue
            # Capture test name from lines with status (e.g., 'tests/test_connector.py::test_named_pipe_connector PASSED')
            test_status_match = re.match(r'^(tests/.*?\.py::test.*?)\s+(PASSED|FAILED|SKIPPED|XFAIL)$', line)
            if test_status_match:
                test_name = test_status_match.group(1)
                status = test_status_match.group(2)
                if status == 'PASSED':
                    test_status[test_name] = 'passed'
                elif status == 'FAILED':
                    test_status[test_name] = 'failed'
                elif status == 'SKIPPED':
                    test_status[test_name] = 'skipped'
                elif status == 'XFAIL':
                    test_status[test_name] = 'failed'
                continue
            # Capture test name from lines without status (e.g., 'tests/test_connector.py::test_named_pipe_connector')
            test_name_only_match = re.match(r'^(tests/.*?\.py::test.*)$', line)
            if test_name_only_match:
                current_test_name = test_name_only_match.group(1)
                continue
            # Check for PASSED tests
            passed_match = re.match(r'^(.*?)\s+PASSED$', line)
            if passed_match:
                test_name = passed_match.group(1)
                test_status[test_name] = 'passed'
                current_test_name = test_name
                continue
            # Check for XFAIL tests (treated as failed)
            xfail_match = re.match(r'^XFAIL\s+(tests/.*?\.py::test.*)$', line)
            if xfail_match:
                test_name = xfail_match.group(1)
                test_status[test_name] = 'failed'
                continue
            # Check for FAILED tests in standard format
            failed_std_match = re.match(r'^(tests/.*?\.py::test.*?)\s+FAILED$', line)
            if failed_std_match:
                test_name = failed_std_match.group(1)
                test_status[test_name] = 'failed'
                continue
            # Check for SKIPPED tests with reason
            skipped_reason_match = re.match(r'^SKIPPED\s+\[\d+\]\s+(tests/.*?\.py):\d+:\s+.*$', line)
            if skipped_reason_match:
                if current_test_name is not None:
                    test_status[current_test_name] = 'skipped'
                    current_test_name = None  # Reset
                else:
                    # Extract test name from previous line if current_test_name is unset
                    test_match = re.match(r'^(tests/.*?\.py::.*)$', prev_line)
                    if test_match:
                        test_status[test_match.group(1)] = 'skipped'
                continue
            # Check for FAILED tests in error blocks (test name in underscores)
            failed_underscore_match = re.match(r'^_{2,}\s+(test.*?)\s+_{2,}$', line)
            if failed_underscore_match and current_file:
                test_name = failed_underscore_match.group(1)
                full_test_name = f"{current_file}::{test_name}"
                test_status[full_test_name] = 'failed'
                continue
        # Populate results from test_status
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
