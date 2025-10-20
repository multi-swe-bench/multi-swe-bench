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
        return "node:18"
    
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
                """cat package.json
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential python3
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
npm install node-sass@8.0.0 --legacy-peer-deps
###ACTION_DELIMITER###
echo 'NODE_OPTIONS=--openssl-legacy-provider npm test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y firefox
###ACTION_DELIMITER###
apt-get update && apt-get install -y firefox-esr
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
NODE_OPTIONS=--openssl-legacy-provider npm test -- --verbose

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
NODE_OPTIONS=--openssl-legacy-provider npm test -- --verbose

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
NODE_OPTIONS=--openssl-legacy-provider npm test -- --verbose

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
FROM node:18

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
RUN git clone https://github.com/Hacker0x01/react-datepicker.git /home/react-datepicker

WORKDIR /home/react-datepicker
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Hacker0x01", "react_datepicker_2996_to_1656")
class REACT_DATEPICKER_2996_TO_1656(Instance):
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
        # Parse log lines to extract test names and statuses
        hierarchy = []
        # Regex patterns to match test lines and section headers
        test_pattern = re.compile(r'^( +)([✖✔]) (.*)$')
        section_pattern = re.compile(r'^( +)(.*?)$')
        for line in log.split('\n'):
            # Process test lines (✔/✖)
            test_match = test_pattern.match(line)
            if test_match:
                spaces, symbol, test_title = test_match.groups()
                level = len(spaces) // 2
                # Combine hierarchy (parent sections) with test title
                full_test_name = ' '.join(hierarchy[:level-1]) + ' ' + test_title if level > 0 else test_title
                full_test_name = full_test_name.strip()
                if symbol == '✔':
                    passed_tests.add(full_test_name)
                elif symbol == '✖':
                    failed_tests.add(full_test_name)
                continue
            # Process section headers (nested descriptions)
            section_match = section_pattern.match(line)
            if section_match:
                spaces, section_name = section_match.groups()
                section_name = section_name.strip()
                if not section_name or '✖' in line or '✔' in line:
                    continue
                level = len(spaces) // 2
                if level == 0:
                    continue
                # Update hierarchy to match current section level
                while len(hierarchy) >= level:
                    hierarchy.pop()
                hierarchy.append(section_name)
                continue
        # Handle skipped tests if patterns are identified (add logic as needed)
        # Example: skipped_pattern = re.compile(r'^( +)SKIPPED (.*)$')
        # ...
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
