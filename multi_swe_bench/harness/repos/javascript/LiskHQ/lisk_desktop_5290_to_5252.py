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
yarn install:all
###ACTION_DELIMITER###
yarn
###ACTION_DELIMITER###
git clone https://github.com/LiskHQ/Numeral-js.git temp-numeral-js
###ACTION_DELIMITER###
cd temp-numeral-js && git rev-parse --verify 195af9768f998c4e4acde3ec86388b17c7c0254b
###ACTION_DELIMITER###
cd /home/lisk-desktop
###ACTION_DELIMITER###
sed -i 's|"numeral": "git+https://github.com/LiskHQ/Numeral-js.git"|"numeral": "git+https://github.com/LiskHQ/Numeral-js.git#195af9768f998c4e4acde3ec86388b17c7c0254b"|g' package.json
###ACTION_DELIMITER###
yarn install:all
###ACTION_DELIMITER###
yarn add file:./temp-numeral-js && yarn install:all
###ACTION_DELIMITER###
sed -i '/"numeral":/d' package.json && yarn add file:./temp-numeral-js && yarn install:all
###ACTION_DELIMITER###
sed -i 's|"numeral": "git+https://github.com/LiskHQ/Numeral-js.git"|"numeral": "git+https://github.com/LiskHQ/Numeral-js.git#195af9768f998c4e4acde3ec86388b17c7c0254b"|g' package.json && yarn cache clean && yarn install
###ACTION_DELIMITER###
echo 'yarn test --verbose' > test_commands.sh && echo 'yarn cypress:run --reporter spec' >> test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn test --verbose
yarn cypress:run --reporter spec

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
yarn test --verbose
yarn cypress:run --reporter spec

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
yarn test --verbose
yarn cypress:run --reporter spec

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


@Instance.register("LiskHQ", "lisk_desktop_5290_to_5252")
class LISK_DESKTOP_5290_TO_5252(Instance):
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

        # Track test hierarchy and statuses
        hierarchy = []
        test_case_pattern = re.compile(r"^(\s*)([✓✕○])\s+(.*?)\s+\(\d+ ms\)$")
        pass_fail_pattern = re.compile(
            r"^(PASS|FAIL)\s+(.*?)(?:\s+\(\d+\.\d+ s\))?$"
        )  # Extract file path from PASS/FAIL lines (with or without time)
        for line in log.split("\n"):
            # Update hierarchy based on indentation
            indent_match = re.match(r"^(\s*)", line)
            if indent_match:
                indent = len(indent_match.group(1))
                # Pop hierarchy items with greater/equal indent
                while hierarchy and hierarchy[-1][1] >= indent:
                    hierarchy.pop()
                # Extract suite/case name (non-test lines)
                if not test_case_pattern.match(line):
                    stripped_line = line.strip().rstrip(":")
                    # Skip stack traces, errors, and irrelevant lines
                    if stripped_line.startswith(
                        ("at ", "Error:", "Your system is missing", "info", "warning")
                    ):
                        continue
                    # Extract file path from PASS/FAIL lines
                    pass_fail_match = pass_fail_pattern.match(stripped_line)
                    if pass_fail_match:
                        name = pass_fail_match.group(
                            2
                        )  # Use file path as top-level name
                    else:
                        name = stripped_line
                    if name and not line.strip().startswith(("✓", "✕", "○")):
                        hierarchy.append((name, indent))
            # Match test cases
            case_match = test_case_pattern.match(line)
            if case_match:
                indent, status, desc = case_match.groups()
                full_name = " ".join([h[0] for h in hierarchy] + [desc])
                if status == "✓":
                    passed_tests.add(full_name)
                elif status == "✕":
                    failed_tests.add(full_name)
                elif status == "○":
                    skipped_tests.add(full_name)
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
