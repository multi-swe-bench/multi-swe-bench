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
        return "node:18-bullseye"
    
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
                """ls -la
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
yarn install:all
###ACTION_DELIMITER###
yarn --cwd app
###ACTION_DELIMITER###
yarn
###ACTION_DELIMITER###
git clone https://github.com/LiskHQ/Numeral-js.git && cd Numeral-js && git checkout 195af9768f998c4e4acde3ec86388b17c7c0254b
###ACTION_DELIMITER###
cd /home/lisk-desktop/Numeral-js && git log --oneline -n 10
###ACTION_DELIMITER###
cd /home/lisk-desktop && sed -i 's|#195af9768f998c4e4acde3ec86388b17c7c0254b|#3673d48|g' package.json
###ACTION_DELIMITER###
sed -i 's|git+https://github.com/LiskHQ/Numeral-js.git|git+https://github.com/LiskHQ/Numeral-js.git#3673d48|g' /home/lisk-desktop/package.json
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo 'yarn test -- --verbose' > /home/lisk-desktop/test_commands.sh
###ACTION_DELIMITER###
bash /home/lisk-desktop/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn test -- --verbose

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
yarn test -- --verbose

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
yarn test -- --verbose

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
FROM node:18-bullseye

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
RUN git clone https://github.com/LiskHQ/lisk-desktop.git /home/lisk-desktop

WORKDIR /home/lisk-desktop
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("LiskHQ", "lisk_desktop_5366_to_5324")
class LISK_DESKTOP_5366_TO_5324(Instance):
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
        test_status: dict[str, str] = {}  # Track latest status of each test
        import re
        import json
        test_case_pattern = re.compile(r'^\s*([✓✕○−-])\s+(.*?)(?:\s+\(\d+ ms\))?$')
        lines = log.split('\n')
        current_groups = []
        for line in lines:
            # Check if the line is a test case
            test_match = test_case_pattern.match(line)
            if test_match:
                symbol = test_match.group(1)
                test_name = test_match.group(2)
                indent = len(line) - len(line.lstrip())
                depth = indent // 2
                # Construct full test name from current groups and test name
                if len(current_groups) >= depth - 1:
                    full_test_name = ' › '.join(current_groups[:depth-1] + [test_name])
                else:
                    full_test_name = ' › '.join(current_groups + [test_name])
                # Categorize based on symbol
                if symbol == '✓':
                    test_status[full_test_name] = 'passed'
                elif symbol == '✕':
                    test_status[full_test_name] = 'failed'
                elif symbol == '−':
                    test_status[full_test_name] = 'skipped'
                elif symbol == '○':
                    test_status[full_test_name] = 'skipped'
                continue
            # Check if the line is a group header
            stripped_line = line.strip()
            if not stripped_line:
                continue  # Skip empty lines
            if stripped_line.startswith('●'):
                continue  # Skip error lines
            # Skip code lines, stack traces, etc.
            if any(pattern in stripped_line for pattern in ("|", ">", "at ")):
                continue
            # Determine indentation depth
            indent = len(line) - len(line.lstrip())
            depth = indent // 2
            if depth == 0:
                continue  # Not a group header (too shallow)
            # Update current groups
            group_name = stripped_line
            if len(current_groups) < depth:
                current_groups.append(group_name)
            else:
                current_groups = current_groups[:depth-1] + [group_name]
        # Populate results from test_status
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
