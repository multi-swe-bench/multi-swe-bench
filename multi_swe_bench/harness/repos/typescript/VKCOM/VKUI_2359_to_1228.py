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
npm install -g yarn@1.22.18
###ACTION_DELIMITER###
npm install -g yarn@1.22.18 --force
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo -e 'yarn test:unit --verbose
yarn test:static' > test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn test:unit --verbose
yarn test:static

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
yarn test:unit --verbose
yarn test:static

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
yarn test:unit --verbose
yarn test:static

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
RUN git clone https://github.com/VKCOM/VKUI.git /home/VKUI

WORKDIR /home/VKUI
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("VKCOM", "VKUI_2359_to_1228")
class VKUI_2359_TO_1228(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re

        # Pattern for passed tests (individual test cases)
        passed_pattern = re.compile(r"✓\s+(.+?)\s*\(\d+\s*ms\)")
        # Track nested test groups
        current_group = []
        # Pattern for test groups (e.g., '  RangeSlider')
        group_pattern = re.compile(r"^(\s{2,})(\w.+?)\s*$")  # Capture indentation level
        # Pattern for skipped tests in summary
        skipped_summary_pattern = re.compile(r"Tests:\s+(\d+)\s+skipped")
        # Pattern for individual skipped tests
        skipped_pattern = re.compile(r"○\s+skipped\s+(.+)")
        # Pattern for failed test suites
        failed_pattern = re.compile(r"✕\s+(.+?)\s*\(\d+\s*ms\)")
        for line in log.split("\n"):
            # Update test group context
            group_match = group_pattern.search(line)
            if group_match:
                indent = group_match.group(1)
                depth = len(indent) // 2  # Assume 2 spaces per indent level
                group_name = group_match.group(2).strip()
                current_group = current_group[: depth - 1] + [group_name]
                continue
            # Check for summary skipped tests
            summary_skip_match = skipped_summary_pattern.search(line)
            if summary_skip_match:
                # Note: This captures count; adjust if individual skipped test names are needed
                skipped_tests.add(
                    f"{summary_skip_match.group(1)} skipped tests (summary)"
                )
                continue
            # Check for passed tests
            pass_match = passed_pattern.search(line)
            if pass_match:
                test_name = pass_match.group(1).strip()
                full_test_name = (
                    " > ".join(current_group + [test_name])
                    if current_group
                    else test_name
                )
                passed_tests.add(full_test_name)
            # Check for skipped tests
            skip_match = skipped_pattern.search(line)
            if skip_match:
                test_name = skip_match.group(1).strip()
                full_test_name = (
                    " > ".join(current_group + [test_name])
                    if current_group
                    else test_name
                )
                skipped_tests.add(full_test_name)
            # Check for failed tests
            fail_match = failed_pattern.search(line)
            if fail_match:
                test_name = fail_match.group(1).strip()
                full_test_name = (
                    " > ".join(current_group + [test_name])
                    if current_group
                    else test_name
                )
                failed_tests.add(full_test_name)
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
