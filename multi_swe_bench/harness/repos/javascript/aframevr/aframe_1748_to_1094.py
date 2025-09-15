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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y firefox-esr chromium-browser
###ACTION_DELIMITER###
apt-get install -y firefox-esr chromium
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
npm test -- --browsers ChromeHeadless,FirefoxHeadless --single-run
###ACTION_DELIMITER###
apt-get install -y xvfb
###ACTION_DELIMITER###
xvfb-run npm test -- --browsers Chrome,firefox_latest --single-run
###ACTION_DELIMITER###
xvfb-run npm test -- --browsers Chromium,Firefox --single-run --verbose
###ACTION_DELIMITER###
echo 'xvfb-run npm test -- --browsers Firefox --single-run --verbose' > /home/aframe/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
xvfb-run npm test -- --browsers Firefox --single-run --verbose

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
xvfb-run npm test -- --browsers Firefox --single-run --verbose

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
xvfb-run npm test -- --browsers Firefox --single-run --verbose

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

# Choose an appropriate base image based on the project's requirements - replace node:18-bullseye with actual base image
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
RUN git clone https://github.com/aframevr/aframe.git /home/aframe

WORKDIR /home/aframe
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("aframevr", "aframe_1748_to_1094")
class AFRAME_1748_TO_1094(Instance):
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
        import json
        # Helper function to strip ANSI escape codes
        def strip_ansi(s):
            return re.sub(r'\x1b\[[0-9;]*m', '', s)
        # Strip ANSI codes from the log
        stripped_log = strip_ansi(log)
        lines = stripped_log.split('\n')
        current_hierarchy = []
        for line in lines:
            # Strip line number prefix (e.g., [   1] )
            line = re.sub(r'^\[\s*\d+\]\s*', '', line)
            leading_spaces = len(line) - len(line.lstrip(' '))
            content = line.lstrip(' ')
            # Skip lines with log warnings/errors
            if 'WARN' in content or 'ERROR' in content:
                continue
            if '✔' in content:
                # Extract test description
                test_desc = content.split('✔', 1)[1].strip()
                # Skip summary phrases
                if 'tests completed' in test_desc or 'tests failed' in test_desc:
                    continue
                # Combine with current hierarchy
                full_test_name = '.'.join(current_hierarchy + [test_desc])
                passed_tests.add(full_test_name)
            elif '✖' in content:
                test_desc = content.split('✖', 1)[1].strip()
                # Skip summary phrases
                if 'tests failed' in test_desc:
                    continue
                full_test_name = '.'.join(current_hierarchy + [test_desc])
                failed_tests.add(full_test_name)
            else:
                # Check if it's a section line (not a test)
                # Ignore empty lines
                if not content:
                    continue
                # Skip log lines, section headers, header commands, and summary timings
                if content.startswith(('Firefox', 'LOG:', 'INFO', 'WARN', 'ERROR', '15 09 2025', 'START:', 'SUMMARY:', '>')) or 'Finished in' in content:
                    continue
                # Skip error messages and summary phrases
                if 'Expected' in content or 'AssertionError' in content or 'tests completed' in content or 'tests failed' in content:
                    continue
                # Handle FAILED TESTS section by resetting hierarchy
                if content == 'FAILED TESTS:':
                    current_hierarchy = []
                    continue
                # Determine hierarchy level (assuming 2 spaces per level)
                level = leading_spaces // 2
                # Update current hierarchy
                if level == 0:
                    current_hierarchy = [content]
                else:
                    # Truncate to (level - 1) and append the new section
                    current_hierarchy = current_hierarchy[:level-1] + [content]
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
