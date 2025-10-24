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
        return "ubuntu:22.04"

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
                """apt-get update && apt-get install -y libgl1-mesa-glx libxcb-xinerama0 libxcb-randr0 libxcb-xfixes0 libxcb-shape0 libxcb-render-util0 libxcb-render0 libxcb-shm0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-xkb1 libxkbcommon-x11-0 libxkbcommon0 curl
###ACTION_DELIMITER###
curl -LsSf https://astral.sh/uv/install.sh | sh
###ACTION_DELIMITER###
source $HOME/.local/bin/env
###ACTION_DELIMITER###
uv sync --all-extras
###ACTION_DELIMITER###
echo 'ERT_PYTEST_ARGS="--verbose" uv run just check-all' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y parallel
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libegl1-mesa
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libfontconfig1
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
ERT_PYTEST_ARGS="--verbose" uv run just check-all

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
ERT_PYTEST_ARGS="--verbose" uv run just check-all

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
ERT_PYTEST_ARGS="--verbose" uv run just check-all

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
FROM ubuntu:22.04

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
RUN git clone https://github.com/equinor/ert.git /home/ert

WORKDIR /home/ert
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("equinor", "ert_10361_to_10179")
class ERT_10361_TO_10179(Instance):
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
        test_status = {}  # Tracks latest status for each test (key: test name, value: 'passed'/'failed'/'skipped')
        # Original sets replaced with a dictionary to avoid overlapping entries
        import re

        # Refined patterns to handle parameters, line numbers, and metadata
        # Enhanced patterns to capture full test names with parameters and handle varied metadata
        # Updated patterns to handle leading line numbers and full test name structure
        # Flexible patterns to handle varied log formats (detailed, summary, line numbers)
        test_pattern = re.compile(
            r"((tests|src)/[\w/.-]+\.py::[\w_]+(?:\[[^\]]*\])?|(tests|src)/[\w/.-]+\.py:\d+)\s+(PASSED|FAILED|SKIPPED)"
        )
        status_pattern = re.compile(
            r"(?:\[\d+\]\s*\[(?:gw\d+)\]\s*\[\s*\d+%\]\s*)?(PASSED|FAILED|SKIPPED)\s+(?:\[\d+\]\s*)?((?:tests|src)/[\w/.-]+\.py::[\w_]+(?:\[[^\]]*\])?|(?:tests|src)/[\w/.-]+\.py:\d+)"
        )
        # Extract tests where status is after the test name
        for match in test_pattern.findall(log):
            test_name, _, _, status = match
            # Validate test name format
            if not (
                test_name.startswith(("tests/", "src/"))
                and (".py::" in test_name or ".py:" in test_name)
            ):
                continue
            normalized_status = status.lower()
            if normalized_status in ["passed", "failed", "skipped"]:
                test_status[test_name] = normalized_status
        # Extract tests where status is before the test name
        for match in status_pattern.findall(log):
            status, test_name = match
            normalized_status = status.lower()
            if normalized_status in ["passed", "failed", "skipped"]:
                test_status[test_name] = normalized_status
        # Generate final sets from the status dictionary
        passed_tests = {
            test for test, status in test_status.items() if status == "passed"
        }
        failed_tests = {
            test for test, status in test_status.items() if status == "failed"
        }
        skipped_tests = {
            test for test, status in test_status.items() if status == "skipped"
        }
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
