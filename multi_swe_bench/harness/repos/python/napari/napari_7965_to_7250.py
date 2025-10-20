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
        return "ubuntu:latest"
    
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
                """ls
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip libgles2-mesa libglib2.0-0 libgl1-mesa-glx xvfb python3-tk python3-dev
###ACTION_DELIMITER###
apt search libgles2 && apt search libgl1
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip libgles2 libglib2.0-0 libgl1 xvfb python3-tk python3-dev
###ACTION_DELIMITER###
pip install -e .[testing,pyqt5]
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install -e .[testing,pyqt5]
###ACTION_DELIMITER###
echo 'xvfb-run -a pytest -v --no-header -rA --tb=short -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libqt5opengl5 libglu1-mesa
###ACTION_DELIMITER###
echo 'xvfb-run -a pytest -v --no-header -rA --full-trace --capture=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
xvfb-run -a pytest -v --no-header -rA --full-trace --capture=no -p no:cacheprovider

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
xvfb-run -a pytest -v --no-header -rA --full-trace --capture=no -p no:cacheprovider

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
xvfb-run -a pytest -v --no-header -rA --full-trace --capture=no -p no:cacheprovider

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:latest with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:latest

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
RUN git clone https://github.com/napari/napari.git /home/napari

WORKDIR /home/napari
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("napari", "napari_7965_to_7250")
class NAPARI_7965_TO_7250(Instance):
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
        # Regex patterns to match test names and statuses
        # Match test name and status on the same line (with optional text after)
        combined_pattern = re.compile(r'(.+?\.py::test_.+?(?:\[.*?\])?)\s+(PASSED|FAILED|SKIPPED|XFAIL)\b', re.IGNORECASE)
        # Match test name (captures until first whitespace, including parameters)
        test_name_pattern = re.compile(r'(.+?\.py::test_.+?(?:\[.*?\])?)\s', re.MULTILINE)
        # Match status (works with or without surrounding text)
        status_pattern = re.compile(r'\b(PASSED|FAILED|SKIPPED|XFAIL)\b', re.IGNORECASE)
        # Match failed tests with FAILED status (handles warnings/errors on same line)
        failed_pattern = re.compile(r'(.+?\.py::test_.+?(?:\[.*?\])?)\s+FAILED\b', re.IGNORECASE)
        # Match skipped tests with SKIPPED status (handles surrounding text)
        skipped_pattern = re.compile(r'(.+?\.py::test_.+?(?:\[.*?\])?)\s+SKIPPED\b', re.IGNORECASE)
        # Match failed tests in summary table (combines file and function columns)
        failure_summary_pattern = re.compile(r'│\s*(src/napari[^│]+)\s*│\s*(test_[^│]+)\s*│', re.MULTILINE)
        current_test = None
        # Extract failed tests using failed_pattern
        failed_tests.update(match.group(1).strip() for match in failed_pattern.finditer(log))
        # Extract failed tests from summary table (combine file and function)
        for match in failure_summary_pattern.finditer(log):
            file_part = match.group(1).strip()
            test_part = match.group(2).strip()
            failed_tests.add(f"{file_part}::{test_part}")
        # Extract skipped tests using skipped_pattern
        skipped_tests.update(match.group(1).strip() for match in skipped_pattern.finditer(log))
        for line in log.split('\n'):
            # Check for test name and status on the same line
            combined_match = combined_pattern.search(line)
            if combined_match:
                test_name = combined_match.group(1).strip()
                status = combined_match.group(2).upper()
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
                elif status == 'XFAIL':
                    failed_tests.add(test_name)
                continue  # Skip to next line
            # Extract test name if present (status may be on next line)
            test_match = test_name_pattern.search(line)
            if test_match:
                current_test = test_match.group(1).strip()
            # Extract status if present (may follow a test name on a previous line)
            status_match = status_pattern.search(line)
            if status_match:
                status = status_match.group(1).upper()
                if current_test:
                    if status == 'PASSED':
                        passed_tests.add(current_test)
                    elif status == 'FAILED':
                        failed_tests.add(current_test)
                    elif status == 'SKIPPED':
                        skipped_tests.add(current_test)
                    elif status == 'XFAIL':
                        failed_tests.add(current_test)
                    current_test = None
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
