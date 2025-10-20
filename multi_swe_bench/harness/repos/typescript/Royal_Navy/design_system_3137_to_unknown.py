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
        return "node:20-bookworm"
    
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
                """yarn install --ignore-engines
###ACTION_DELIMITER###
yarn test
###ACTION_DELIMITER###
YARN_IGNORE_ENGINES=true yarn test
###ACTION_DELIMITER###
ls -l packages/design-tokens/src
###ACTION_DELIMITER###
cd packages/design-tokens && yarn build
###ACTION_DELIMITER###
cd /home/design-system && yarn build
###ACTION_DELIMITER###
YARN_IGNORE_ENGINES=true yarn build
###ACTION_DELIMITER###
YARN_IGNORE_ENGINES=true yarn test
###ACTION_DELIMITER###
echo 'YARN_IGNORE_ENGINES=true yarn test' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
YARN_IGNORE_ENGINES=true yarn test

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
YARN_IGNORE_ENGINES=true yarn test

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
YARN_IGNORE_ENGINES=true yarn test

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
FROM node:20-bookworm

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
RUN git clone https://github.com/Royal-Navy/design-system.git /home/design-system

WORKDIR /home/design-system
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Royal-Navy", "design_system_3137_to_unknown")
class DESIGN_SYSTEM_3137_TO_UNKNOWN(Instance):
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
        # Preprocess lines to remove log prefixes (line numbers and package names)
        # Remove line numbers in brackets
        line_number_prefix = re.compile(r'^\[\s*\d+\]\s*(.*)$')
        lines = [line_number_prefix.sub(r'\1', line) for line in log.split('\n')]
        # Remove package prefixes
        package_prefix = re.compile(r'^@defencedigital/[^:]+:\s*(.*)$')
        lines = [package_prefix.sub(r'\1', line) for line in lines]
        # Strip ANSI escape codes
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        lines = [ansi_escape.sub('', line) for line in lines]
        context = []
        current_indent = 0
        last_it_test = None
        # Regex patterns (adjusted for preprocessed lines)
        test_suite_pattern = re.compile(r'^(PASS|FAIL)\s+.*$')
        context_line_pattern = re.compile(r'^(\s*)(.*)')
        passed_test_pattern = re.compile(r'^\s*✓\s+(.*?)\s*\(\d+\s*ms\)$')
        failed_test_pattern = re.compile(r'^\s*[✕×x]\s+(.*?)\s*\(\d+ ms\)?$')
        failed_test_it_pattern = re.compile(r"\b(?:it|test)\(['\"](.*?)['\"]\)", re.IGNORECASE)
        error_line_pattern = re.compile(r'^(\s*>\s*\d+\s+.*|\s*at\s+Object\.<anonymous>\s+\(.*\))$')
        skipped_test_pattern = re.compile(r'^\s*(○|skipped|SKIPPED)\s+(.*?)\s*\(\d+ ms\)?$', re.IGNORECASE)
        for line in lines:
            if not line.strip():
                continue
            # Check if it's a test suite line (PASS/FAIL)
            if test_suite_pattern.match(line):
                context = []
                current_indent = 0
                continue
            # Check if it's a passed test line
            passed_match = passed_test_pattern.match(line)
            if passed_match:
                test_desc = passed_match.group(1)
                full_test_name = ' '.join(context + [test_desc])
                passed_tests.add(full_test_name)
                continue
            # Check if it's a failed test line
            failed_match = failed_test_pattern.match(line)
            if failed_match:
                test_desc = failed_match.group(1)
                full_test_name = ' '.join(context + [test_desc])
                failed_tests.add(full_test_name)
                continue
            # Check if it's a skipped test line
            skipped_match = skipped_test_pattern.match(line)
            if skipped_match:
                test_desc = skipped_match.group(2)
                full_test_name = ' '.join(context + [test_desc])
                skipped_tests.add(full_test_name)
                continue
            # Check for 'it' blocks (potential failed tests)
            failed_it_match = failed_test_it_pattern.search(line)
            if failed_it_match:
                last_it_test = failed_it_match.group(1)
                continue
            # Check if it's a context line (indented, no ✓/✕)
            context_match = context_line_pattern.match(line)
            if context_match:
                spaces = context_match.group(1)
                desc = context_match.group(2)
                indent_level = len(spaces)
                # Update context based on indentation
                if indent_level > current_indent:
                    context.append(desc)
                    current_indent = indent_level
                elif indent_level < current_indent:
                    # Pop until indent_level is less than current_indent
                    while context and indent_level < current_indent:
                        context.pop()
                        current_indent -= 2  # assuming 2 spaces per indent
                    # Add new desc if not empty
                    if desc:
                        context.append(desc)
                        current_indent = indent_level
                else:
                    # Same indent level, replace last context
                    if context:
                        context.pop()
                    context.append(desc)
                continue
            # Check for error lines indicating failed tests
            if error_line_pattern.match(line) and last_it_test:
                failed_tests.add(last_it_test)
                last_it_test = None
                continue
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
