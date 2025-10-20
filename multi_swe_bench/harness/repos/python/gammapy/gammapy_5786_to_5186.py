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
pip install -e .
###ACTION_DELIMITER###
apt-get update && apt-get install -y gcc python3-dev
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
echo 'python -m pytest -v gammapy' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest-astropy-header
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install naima
###ACTION_DELIMITER###
echo 'python -m pytest -v gammapy -k "not test_naima_model"' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'python -m pytest -v gammapy --ignore=gammapy/modeling/models/tests/test_io.py' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python -m pytest -v gammapy --ignore=gammapy/modeling/models/tests/test_io.py

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
python -m pytest -v gammapy --ignore=gammapy/modeling/models/tests/test_io.py

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
python -m pytest -v gammapy --ignore=gammapy/modeling/models/tests/test_io.py

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
RUN git clone https://github.com/gammapy/gammapy.git /home/gammapy

WORKDIR /home/gammapy
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("gammapy", "gammapy_5786_to_5186")
class GAMMAPY_5786_TO_5186(Instance):
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
        # Regex patterns to match test cases and their statuses
        # Enhanced patterns to capture test names with flexible formatting
        # More flexible patterns to handle varied formatting
        # Directly match test names adjacent to statuses
        # Adjusted to handle additional text after status (e.g., percentages)
        # More permissive patterns to handle varied test names and formats
        # Precise patterns matching test name structure
        # Account for leading content (e.g., line numbers) with .*?
        # Handle variable whitespace and trailing content
        # Include hyphens in path/filename patterns
        # Expand character classes and use \s+ for separation
        # Explicitly match lines with leading line numbers
        # Handle line numbers with spaces inside brackets
        # Handle additional content after status and optional line numbers for failures
        # Simplified patterns with non-greedy matching for better capture
        # Explicit test name structure with flexible trailing content
        # More permissive test name matching
        # Include trailing content after status
        # Use specific character classes for path components
        # Simplified patterns focusing on test name and status
        # Capture leading content and ignore trailing characters
        # Explicitly match gammapy path structure
        # Flexible path matching to handle deeper directories
        # Explicit path components with flexible matching
        # Explicitly match line numbers at the start
        # Explicitly match digit-only line numbers with optional spaces
        # Make line numbers optional for all statuses
        # Use [^/]+ for path segments to handle non-alphanumeric characters
        # Allow slashes in path segments using non-greedy matching
        # Use greedy matching for path segments to capture multiple subdirectories
        # Use non-greedy matching for path segments to ensure precise capture
        # Explicit line numbers and precise path components
        # Include trailing content after status
        # Simplified non-greedy matching for test names
        # Explicitly match test path structure with valid characters
        # Include trailing content after status to handle percentages
        # Use non-greedy matching for path components to handle any directory structure
        # Use greedy matching for path segments and ensure whitespace
        # Simplify to focus on test file and name structure
        # Use greedy matching for test path and explicit whitespace
        passed_pattern = re.compile(r'(?:\[.*?\]\s+)?(gammapy/.+\.py::[\w:]+)\s+PASSED.*', re.IGNORECASE)
        skipped_pattern = re.compile(r'(?:\[.*?\]\s+)?(gammapy/.+\.py::[\w:]+)\s+SKIPPED.*', re.IGNORECASE)
        failed_pattern = re.compile(r'FAILED\s+(gammapy/.+\.py::[\w:]+).*', re.IGNORECASE)
        # Extract test names based on status
        passed_tests.update(passed_pattern.findall(log))
        skipped_tests.update(skipped_pattern.findall(log))
        failed_tests.update(failed_pattern.findall(log))
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
