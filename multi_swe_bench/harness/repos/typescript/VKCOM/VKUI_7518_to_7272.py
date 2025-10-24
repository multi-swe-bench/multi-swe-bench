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
corepack enable
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
yarn install --frozen-lockfile
###ACTION_DELIMITER###
yarn --version
###ACTION_DELIMITER###
node --version
###ACTION_DELIMITER###
corepack prepare
###ACTION_DELIMITER###
yarn install --verbose
###ACTION_DELIMITER###
npm config set registry https://registry.npm.taobao.org
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo 'yarn test --verbose' > test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn test --verbose

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

# Choose an appropriate base image based on the project's requirements - replace node:20-bookworm with actual base image
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
RUN git clone https://github.com/VKCOM/VKUI.git /home/VKUI

WORKDIR /home/VKUI
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("VKCOM", "VKUI_7518_to_7272")
class VKUI_7518_TO_7272(Instance):
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

        current_suite = ""
        for line in log.split("\n"):
            # Extract content after the line number prefix
            content_match = re.match(r"^\[\s*\d+\]\s*(.*)$", line)
            content = content_match.group(1) if content_match else line
            # Update current test suite if the line is a suite name (indented with 2 spaces)
            suite_match = re.match(r"^\s{2}(\S.*?)\s*$", content)
            if suite_match:
                current_suite = suite_match.group(1)
                continue
            # Check for passed tests (indented with 4 spaces, ✓)
            passed_match = re.match(r"^\s{4}✓\s+(.*?)\s+\(\d+\s*ms\)$", content)
            if passed_match:
                test_case = passed_match.group(1)
                full_test_name = (
                    f"{current_suite} {test_case}" if current_suite else test_case
                )
                passed_tests.add(full_test_name)
                continue
            # Check for failed tests (indented with 4 spaces, x)
            failed_match = re.match(r"^\s{4,}[✕x]\s+(.*?)\s+\(\d+\s*ms\)$", content)
            if failed_match:
                test_case = failed_match.group(1)
                full_test_name = (
                    f"{current_suite} {test_case}" if current_suite else test_case
                )
                failed_tests.add(full_test_name)
                continue
            # Check for skipped tests (indented with 4 spaces, s or SKIPPED)
            skipped_match = re.match(
                r"^\s{4}(?:s|SKIPPED)\s+(.*?)\s+\(\d+\s*ms\)$", content
            )
            if skipped_match:
                test_case = skipped_match.group(1)
                full_test_name = (
                    f"{current_suite} {test_case}" if current_suite else test_case
                )
                skipped_tests.add(full_test_name)
                continue
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
