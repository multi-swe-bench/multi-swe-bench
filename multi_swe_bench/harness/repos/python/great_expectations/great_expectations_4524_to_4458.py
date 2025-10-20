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
        return "python:3.7-slim"
    
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
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo 'pytest -v' > /home/great_expectations/test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider' > /home/great_expectations/test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install jinja2==3.0.3
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y locales && echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen && locale-gen en_US.UTF-8 && export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8
###ACTION_DELIMITER###
LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 bash test_commands.sh
###ACTION_DELIMITER###
pip install pyarrow==3.0.0
###ACTION_DELIMITER###
LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=short -p no:cacheprovider' > /home/great_expectations/test_commands.sh
###ACTION_DELIMITER###
LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 bash test_commands.sh
###ACTION_DELIMITER###
pip install 'lxml[html_clean]'
###ACTION_DELIMITER###
LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 bash test_commands.sh
###ACTION_DELIMITER###
pip install ipykernel && python -m ipykernel install --user
###ACTION_DELIMITER###
LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v --no-header -rA --tb=short -p no:cacheprovider

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
pytest -v --no-header -rA --tb=short -p no:cacheprovider

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
pytest -v --no-header -rA --tb=short -p no:cacheprovider

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

# Choose an appropriate base image based on the project's requirements - replace python:3.7-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.7-slim

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
RUN git clone https://github.com/great-expectations/great_expectations.git /home/great_expectations

WORKDIR /home/great_expectations
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("great-expectations", "great_expectations_4524_to_4458")
class GREAT_EXPECTATIONS_4524_TO_4458(Instance):
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
        test_status = {}  # Track status of each test to avoid conflicts
        # Parse SKIPPED tests: test name followed by SKIPPED and percentage
        skipped_pattern = re.compile(r'^(tests/.*?)\s+SKIPPED\s+\[\s*\d+%\]', re.MULTILINE)
        for match in skipped_pattern.finditer(log):
            test_name = match.group(1).strip()
            test_status[test_name] = 'skipped'
        # Parse FAILED tests: FAILED followed by test name
        failed_pattern = re.compile(r'^FAILED\s+(tests/.*?)(?=\s|$)', re.MULTILINE)
        for match in failed_pattern.finditer(log):
            test_name = match.group(1).strip()
            test_status[test_name] = 'failed'
        # Parse PASSED tests: test name followed by percentage (not skipped/failed)
        passed_pattern = re.compile(r'^(tests/.*?)\s+PASSED\s+\[\s*\d+%\]', re.MULTILINE)
        for match in passed_pattern.finditer(log):
            test_name = match.group(1).strip()
            if test_name not in test_status:
                test_status[test_name] = 'passed'
        # Populate the test sets from the status dictionary
        for test, status in test_status.items():
            if status == 'passed':
                passed_tests.add(test)
            elif status == 'failed':
                failed_tests.add(test)
            elif status == 'skipped':
                skipped_tests.add(test)
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
