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
                """yarn install
###ACTION_DELIMITER###
yarn test
###ACTION_DELIMITER###
echo 'yarn test' > /home/mon-entreprise/test_commands.sh
###ACTION_DELIMITER###
bash /home/mon-entreprise/test_commands.sh
###ACTION_DELIMITER###
yarn test --verbose --json --color=never --continue
###ACTION_DELIMITER###
yarn test -- --verbose --reporter=json --color=never --no-fail-fast
###ACTION_DELIMITER###
echo 'yarn test -- --verbose --reporter=json --color=never --no-fail-fast' > /home/mon-entreprise/test_commands.sh
###ACTION_DELIMITER###
bash /home/mon-entreprise/test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn test -- --verbose --reporter=json --color=never --no-fail-fast

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
yarn test -- --verbose --reporter=json --color=never --no-fail-fast

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
yarn test -- --verbose --reporter=json --color=never --no-fail-fast

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
RUN git clone https://github.com/betagouv/mon-entreprise.git /home/mon-entreprise

WORKDIR /home/mon-entreprise
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("betagouv", "mon_entreprise_3824_to_2903")
class MON_ENTREPRISE_3824_TO_2903(Instance):
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

        # Strip ANSI escape codes (color/formatting)
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        cleaned_log = ansi_escape.sub("", log)
        # Pattern for passed tests: ✓ followed by test name (before '(' or '[')
        passed_pattern = re.compile(r"✓\s+(.+?)\s+[\(\[]")
        # Pattern for failed tests: FAIL followed by test file (with .test. or .spec.)
        failed_pattern = re.compile(
            r"FAIL\s+(.+?\.test\.(ts|js|tsx)|.+?\.spec\.(ts|js|tsx))\s+[\(\[]"
        )
        # Pattern for skipped tests: Ignore leading characters before ↓, capture test file
        skipped_pattern = re.compile(
            r"^.*↓\s+(.+?\.test\.(ts|js|tsx|jsx)|.+?\.spec\.(ts|js|tsx|jsx))\s+[\(\[]"
        )
        # Pattern for stderr/failed nested tests (extract test files only)
        stderr_pattern = re.compile(
            r">(\s*.+?\.test\.(ts|js|tsx|jsx)|.+?\.spec\.(ts|js|tsx|jsx))[^>]*$"
        )
        # Extract passed tests
        for match in passed_pattern.finditer(cleaned_log):
            test_name = match.group(1).strip()
            passed_tests.add(test_name)
        # Extract failed tests from FAIL lines
        for match in failed_pattern.finditer(cleaned_log):
            test_name = match.group(1).strip()
            failed_tests.add(test_name)
        # Extract failed tests from stderr/nested lines
        for line in cleaned_log.split("\n"):
            if "stderr" in line:
                stderr_match = stderr_pattern.search(line)
                if stderr_match:
                    test_name = stderr_match.group(1).strip()
                    failed_tests.add(test_name)
        # Extract skipped tests
        for match in skipped_pattern.finditer(cleaned_log):
            test_name = match.group(1).strip()
            # Remove leading non-alphanumeric characters
            test_name = re.sub(r"^[^a-zA-Z0-9_/]+", "", test_name)
            skipped_tests.add(test_name)
        # Additional check for 'skipped' keyword in test counts (restricted to test files)
        for line in cleaned_log.split("\n"):
            if "skipped" in line:
                skip_match = re.search(
                    r"^.*(.+?\.test\.(ts|js|tsx|jsx)|.+?\.spec\.(ts|js|tsx|jsx))\s+\(\d+ tests.*\d+ skipped",
                    line,
                )
                if skip_match:
                    test_name = skip_match.group(1).strip()
                    # Remove leading non-alphanumeric characters
                    test_name = re.sub(r"^[^a-zA-Z0-9_/]+", "", test_name)
                    skipped_tests.add(test_name)
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
