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
                """ls -la
###ACTION_DELIMITER###

###ACTION_DELIMITER###
pip install hatch
###ACTION_DELIMITER###
hatch run test:unit -v
###ACTION_DELIMITER###
pip install spacy
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip install spacy
###ACTION_DELIMITER###
echo 'hatch run test:unit -v' > /home/haystack/test_commands.sh
###ACTION_DELIMITER###
bash /home/haystack/test_commands.sh
###ACTION_DELIMITER###
hatch run test:pip install spacy
###ACTION_DELIMITER###
bash /home/haystack/test_commands.sh
###ACTION_DELIMITER###
hatch run test:python -m spacy download en_core_web_sm
###ACTION_DELIMITER###
bash /home/haystack/test_commands.sh
###ACTION_DELIMITER###
hatch run test:python -m spacy download en_core_web_sm --force"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
hatch run test:unit -v

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
hatch run test:unit -v

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
hatch run test:unit -v

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


@Instance.register("deepset-ai", "haystack_9562_to_8868")
class HAYSTACK_9562_TO_8868(Instance):
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
        import json
        # Regex patterns to match test lines and statuses
        test_status_pattern = re.compile(r'^\s*(e2e/[^\s]+\.py::[^\s]+|test/[^\s]+\.py::[^\s]+)\s+(PASSED|FAILED|SKIPPED)\s+\[\s*\d+%?\s*\]')
        test_name_pattern = re.compile(r'^\s*(e2e/[^\s]+\.py::[^\s]+|test/[^\s]+\.py::[^\s]+)\s*$')
        status_line_pattern = re.compile(r'^\s*(PASSED|FAILED|SKIPPED)\s+\[\s*\d+%?\s*\]')
        summary_pattern = re.compile(r'^\s*(PASSED|FAILED|SKIPPED)\s+(e2e/[^\s]+\.py::[^\s]+|test/[^\s]+\.py::[^\s]+)\s*$')
        current_test = None
        for line in log.split('\n'):
            # Check for test with status on the same line
            match = test_status_pattern.search(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
                current_test = None
                continue
            # Check for summary lines (status followed by test name)
            match = summary_pattern.search(line)
            if match:
                status = match.group(1)
                test_name = match.group(2)
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
                current_test = None
                continue
            # Check for test name without status
            match = test_name_pattern.search(line)
            if match:
                current_test = match.group(1)
                continue
            # Check for status line if current_test is set
            if current_test:
                match = status_line_pattern.search(line)
                if match:
                    status = match.group(1)
                    if status == 'PASSED':
                        passed_tests.add(current_test)
                    elif status == 'FAILED':
                        failed_tests.add(current_test)
                    elif status == 'SKIPPED':
                        skipped_tests.add(current_test)
                    current_test = None
                    continue
        # TODO: Implement the log parsing logic here
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
