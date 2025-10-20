import re

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
yarn install
###ACTION_DELIMITER###
yarn test --verbose
###ACTION_DELIMITER###
echo 'yarn test -- --ci --verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn test -- --ci --verbose

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
yarn test -- --ci --verbose

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
yarn test -- --ci --verbose

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
RUN git clone https://github.com/canonical/maas-ui.git /home/maas-ui

WORKDIR /home/maas-ui
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("canonical", "maas_ui_4462_to_unknown")
class MAAS_UI_4462_TO_UNKNOWN(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        lines = log.split('\n')
        current_suite = None
        current_groups = []
        for line in lines:
            # Clean up line (remove line numbers like [   7] and trim whitespace)
            cleaned_line = re.sub(r'^\[\s*\d+\]\s*', '', line).rstrip()
            # Update current suite on PASS/FAIL
            if cleaned_line.startswith('PASS '):
                # Extract suite name without duration (e.g., remove '(21.495 s)')
                current_suite = re.sub(r' \(.*\)$', '', cleaned_line[5:].strip())
                current_groups = []
            elif cleaned_line.startswith('FAIL '):
                current_suite = re.sub(r' \(.*\)$', '', cleaned_line[5:].strip())
                current_groups = []
            # Track nested test groups (including indented groups) using indentation
            elif cleaned_line.strip() and not re.search(r'[✓✕●]', cleaned_line):
                # Calculate indentation level (assuming 2 spaces per level)
                indent_level = len(cleaned_line) - len(cleaned_line.lstrip())
                depth = indent_level // 2  # Adjust divisor if indentation is different
                # Truncate groups to current depth and add new group
                current_groups = current_groups[:depth]
                current_groups.append(cleaned_line.strip())
            # Capture passed tests (✓)
            elif '✓' in cleaned_line:
                if current_suite:
                    test_name = re.sub(r'✓\s*', '', cleaned_line)
                    test_name = re.sub(r'\s*\(\d+ ms\)$', '', test_name).strip()
                    group_part = ' - '.join(current_groups)
                    full_test = f"{current_suite} - {group_part} - {test_name}" if group_part else f"{current_suite} - {test_name}"
                    passed_tests.add(full_test)
            # Capture failed tests (✕, ●, or error traces)
            elif '✕' in cleaned_line or '●' in cleaned_line or 'error' in cleaned_line.lower():
                if current_suite:
                    # Handle explicit failure markers (✕ or ●)
                    if '✕' in cleaned_line:
                        test_name = re.sub(r'✕\s*', '', cleaned_line)
                        test_name = re.sub(r'\s*\(\d+ ms\)$', '', test_name).strip()
                    elif '●' in cleaned_line:
                        # Extract test name from Jest failure marker (e.g., "● group › test")
                        test_name = re.sub(r'●\s*', '', cleaned_line).strip()
                        test_name = re.sub(r'›', '-', test_name)  # Replace › with -
                    else:
                        # Extract test name from error trace (look for nearest 'it()' block)
                        test_match = re.search(r'it\("(.*?)"\)', cleaned_line)
                        test_name = test_match.group(1) if test_match else 'unknown_test'
                    group_part = ' - '.join(current_groups)
                    full_test = f"{current_suite} - {group_part} - {test_name}" if group_part else f"{current_suite} - {test_name}"
                    failed_tests.add(full_test)
            # Capture skipped tests (SKIP/SKIPPED or Jest's skipped marker)
            elif 'SKIP' in cleaned_line or 'SKIPPED' in cleaned_line or '○' in cleaned_line:
                test_name = re.sub(r'(SKIP|SKIPPED|○)\s*', '', cleaned_line).strip()
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
