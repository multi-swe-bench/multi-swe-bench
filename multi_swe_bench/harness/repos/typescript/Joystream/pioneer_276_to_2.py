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
        return "node:18.18.0"

    def image_prefix(self) -> str:
        return "envagent"

    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:
        repo_name = self.pr.repo
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
echo 'yarn test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn test -- --verbose

""".replace("[[REPO_NAME]]", repo_name),
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

""".replace("[[REPO_NAME]]", repo_name),
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

""".replace("[[REPO_NAME]]", repo_name),
            ),
        ]

    def dockerfile(self) -> str:
        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        dockerfile_content = """
# This is a template for creating a Dockerfile to test patches
# LLM should fill in the appropriate values based on the context

# Choose an appropriate base image based on the project's requirements - replace node:18.18.0 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:18.18.0

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
RUN git clone https://github.com/Joystream/pioneer.git /home/pioneer

WORKDIR /home/pioneer
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Joystream", "pioneer_276_to_2")
class PIONEER_276_TO_2(Instance):
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

        return "bash /home/run.sh"

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

        test_case_pattern = re.compile(
            r"^\s*([✓✕○])\s+(.*?)(?: \(\d+ ms\))?$"
        )  # More flexible matching for test cases
        suite_pattern = re.compile(
            r"^(PASS|FAIL)\s+([^(]+)"
        )  # Capture suite name up to '('
        # Example: Matches 'test/utils/Comparator.test.ts' from 'PASS test/utils/Comparator.test.ts (5.406 s)'
        # Example: Matches 'test/utils/Comparator.test.ts' from both 'PASS test/utils/Comparator.test.ts (5.406 s)' and 'PASS test/utils/sortAccounts.test.ts'
        # Example: Matches 'PASS test/utils/Comparator.test.ts' from both 'PASS test/utils/Comparator.test.ts (5.406 s)' and 'PASS test/utils/sortAccounts.test.ts'
        current_context = []
        for line in log.split("\n"):
            line = line.rstrip("\r")
            # Split line by '|' to ignore timestamp prefix
            parts = line.split("|", 1)
            if len(parts) < 2:
                continue
            content = parts[1]  # Preserve leading spaces for indentation
            leading_spaces = len(re.match(r"^\s*", content).group(0))
            indent_level = leading_spaces // 2  # Assume 2 spaces per indent level
            stripped_content = content.strip()
            # Extract test suite name from PASS/FAIL lines
            suite_match = suite_pattern.match(stripped_content)
            if suite_match:
                suite_name = suite_match.group(2).strip()
                current_context = [suite_name]
                continue
            # Skip error lines
            if stripped_content.startswith("●"):
                continue
            # Identify test cases (✓/✕/○)
            test_match = test_case_pattern.match(content)
            if test_match:
                status, test_desc = test_match.group(1), test_match.group(2).strip()
                full_test = " ".join(current_context + [test_desc])
                if status == "✓":
                    passed_tests.add(full_test)
                elif status == "✕":
                    failed_tests.add(full_test)
                elif status == "○":
                    skipped_tests.add(full_test)
            else:
                # Update nested context (e.g., test groups like 'Comparator' or 'By string')
                if stripped_content:
                    current_context = current_context[:indent_level] + [
                        stripped_content
                    ]
        parsed_results = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
        }

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
