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
pip install poetry
###ACTION_DELIMITER###
poetry install
###ACTION_DELIMITER###
echo 'poetry run trial -v tests' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'poetry run trial --verbose tests' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
poetry run trial --help
###ACTION_DELIMITER###
echo 'poetry run trial tests' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
poetry add setuptools
###ACTION_DELIMITER###
poetry add setuptools@^67.9.0
###ACTION_DELIMITER###
poetry run pip install setuptools
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
poetry run trial tests

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
poetry run trial tests

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
poetry run trial tests

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
RUN git clone https://github.com/matrix-org/synapse.git /home/synapse

WORKDIR /home/synapse
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("matrix-org", "synapse_13292_to_12650")
class SYNAPSE_13292_TO_12650(Instance):
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
        lines = log.split('\n')
        current_module = None
        current_class = None
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            # Check for module line (e.g., tests.api.test_auth)
            if re.match(r'^tests(\.\w+)+$', stripped_line):
                current_module = stripped_line
                current_class = None
                continue
            # Check for class line (e.g., "  AuthTestCase")
            class_match = re.match(r'^\s+(\w+)$', line)
            if class_match:
                current_class = class_match.group(1)
                continue
            # Check for test method line with status (e.g., "    test_blocking_mau ... [OK]")
            method_match = re.match(r'^\s+(\w+)\s+[\.\s]+\[(\w+)\]$', line)
            if method_match:
                method_name = method_match.group(1)
                status = method_match.group(2)
                if current_module and current_class:
                    full_test_name = f"{current_module}.{current_class}.{method_name}"
                else:
                    full_test_name = method_name  # Fallback if module/class not found
                # Determine status
                if status == 'OK':
                    passed_tests.add(full_test_name)
                elif status == 'FAIL':
                    failed_tests.add(full_test_name)
                elif status in ['SKIP', 'SKIPPED']:
                    skipped_tests.add(full_test_name)
                continue
            # Check for full test name followed by FAIL (e.g., "tests.storage.test_state.StateStoreTestCase.test_get_state_for_event")
            full_test_match = re.match(r'^tests(\.\w+)+$', stripped_line)
            if full_test_match:
                # Check next two lines for separator and [FAIL]
                if i + 2 < len(lines):
                    next_line = lines[i+1].strip()
                    next_next_line = lines[i+2].strip()
                    if next_line.startswith(('=', '-')) and next_next_line == '[FAIL]':
                        full_test_name = stripped_line
                        failed_tests.add(full_test_name)
                continue
            # Check for FailTest in traceback to capture failed tests
            if 'FailTest' in line:
                # Look back up to 10 lines to find the traceback line with the test method
                for j in range(i-1, max(i-10, 0), -1):
                    traceback_line = lines[j]
                    if 'File "' in traceback_line and ' in test_' in traceback_line:
                        # Extract module and method from the traceback line
                        file_pattern = r'File ".*tests/((?:\w+/)*)test_(\w+)\.py", line \d+, in (test_\w+)'
                        file_match = re.search(file_pattern, traceback_line)
                        if file_match:
                            module_parts = file_match.group(1).rstrip('/').split('/') if file_match.group(1) else []
                            module = 'tests.' + '.'.join(module_parts) + 'test_' + file_match.group(2)
                            method = file_match.group(3)
                            # Look forward up to 10 lines to find the full test name
                            for k in range(i+1, min(i+10, len(lines))):
                                full_test_line = lines[k].strip()
                                if re.match(r'^tests(\.\w+)+$', full_test_line) and module in full_test_line and method in full_test_line:
                                    failed_tests.add(full_test_line)
                                    break
                            break
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
