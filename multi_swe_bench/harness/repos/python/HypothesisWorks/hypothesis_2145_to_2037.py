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
        return "python:3.11-slim"
    
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
ls requirements
###ACTION_DELIMITER###
cat requirements/test.txt
###ACTION_DELIMITER###
cat pytest.ini
###ACTION_DELIMITER###
cat requirements/test.in
###ACTION_DELIMITER###
pip install pip-tools
###ACTION_DELIMITER###
pip-compile --output-file=requirements/test.txt requirements/test.in
###ACTION_DELIMITER###
pip install -r requirements/test.in
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
ls hypothesis-python
###ACTION_DELIMITER###
cd hypothesis-python && pip install -e .
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install python-dateutil pytz dpcontracts lark-parser numpy pandas
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pytest -v --ignore=tests/py3/test_asyncio.py
###ACTION_DELIMITER###
echo 'cd hypothesis-python && pytest -v --ignore=tests/py3/test_asyncio.py' > /home/hypothesis/test_commands.sh && chmod +x /home/hypothesis/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
cd hypothesis-python && pytest -v --ignore=tests/py3/test_asyncio.py

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
cd hypothesis-python && pytest -v --ignore=tests/py3/test_asyncio.py

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
cd hypothesis-python && pytest -v --ignore=tests/py3/test_asyncio.py

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
FROM python:3.11-slim

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
RUN git clone https://github.com/HypothesisWorks/hypothesis.git /home/hypothesis

WORKDIR /home/hypothesis
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("HypothesisWorks", "hypothesis_2145_to_2037")
class HYPOTHESIS_2145_TO_2037(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        # Regex pattern to match test lines with leading numbers and trailing percentages
        # Regex pattern to match both test_name+status and status+test_name formats
        # More permissive regex to capture test names with .py:: and any non-whitespace characters
        # Allow any leading characters before the line number to handle unexpected prefixes
        # Anchor to start of line to match test lines with leading line numbers
        # Include .* at the end to match trailing content (e.g., percentages, error messages)
        # Allow any leading content before the line number to handle timestamps or other prefixes
        # Split into two simpler patterns for better matching
        # Allow any leading content before line number
        # Make regex case-insensitive to handle varying status casing
        # Remove leading .* to match line number at start of stripped line
        # Use non-greedy matching and allow trailing content for flexibility
        # Add ^ anchor to match line start after stripping
        # Use [^\s]+ to capture non-whitespace characters for test name and status
        # Add .* to ignore trailing content after status or test name
        # Allow any leading content (e.g., ANSI codes) before line number
        # Ensure line starts with line number after stripping
        # Allow leading content before line number to handle timestamps/ANSI codes
        # Remove leading .* to match stripped lines starting with line number
        # Allow any leading content before line number to handle timestamps/ANSI codes
        # Simplify to match stripped lines with explicit test name patterns
        # Use [^\s]+ to capture any non-whitespace test name
        # Require at least one space in expected whitespace areas
        # Allow leading content before line number
        # Use \s* to allow zero or more spaces around line number
        # Anchor to start of line and remove leading .*
        # Remove ^ anchor to handle leading characters before line number
        # Capture test names with .py:: format
        # Allow any leading content before line number
        # Remove leading .* to match from line number
        # Allow leading content before line number
        # Anchor to start of line and remove leading .*
        # Remove ^ anchor to match line number anywhere in the line
        # Focus on test name (.py::) and status, ignoring line number
        pattern_test_status = re.compile(r'([^\s]+\.py::[^\s]+)\s+(PASSED|FAILED|SKIPPED).*', re.IGNORECASE)
        pattern_status_test = re.compile(r'(PASSED|FAILED|SKIPPED)\s+([^\s]+\.py::[^\s]+).*', re.IGNORECASE)
        for line in log.split('\n'):
            line = line.strip()
            # Check for test_name followed by status
            match = pattern_test_status.search(line)
            if match:
                test_name = match.group(1)
                status = match.group(2).upper()
            else:
                # Check for status followed by test_name
                match = pattern_status_test.search(line)
                if match:
                    test_name = match.group(2)
                    status = match.group(1).upper()
                else:
                    continue
            # Add to the appropriate set
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
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
