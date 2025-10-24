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
echo 'yarn test --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo 'yarn test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'NODE_OPTIONS=--openssl-legacy-provider yarn test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libnss3
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libxrandr2
###ACTION_DELIMITER###
apt-get update && apt-get install -y libnss3 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libpango-1.0-0 libx11-xcb1 libxcb-dri3-0 libxcomposite1 libxdamage1 libxfixes3
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
NODE_OPTIONS=--openssl-legacy-provider yarn test -- --verbose

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
NODE_OPTIONS=--openssl-legacy-provider yarn test -- --verbose

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
NODE_OPTIONS=--openssl-legacy-provider yarn test -- --verbose

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
RUN git clone https://github.com/Semantic-Org/Semantic-UI-React.git /home/Semantic-UI-React

WORKDIR /home/Semantic-UI-React
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Semantic-Org", "Semantic_UI_React_4030_to_2499")
class SEMANTIC_UI_REACT_4030_TO_2499(Instance):
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
        import json

        lines = log.split("\n")
        stack: list[tuple[str, int]] = []
        for line in lines:
            # Extract content after line number
            content = line
            # Remove ANSI escape codes (color codes)
            content = re.sub(r"\x1b\[[0-9;]*m", "", content)
            # Calculate indent level (number of leading spaces)
            indent_level = len(content) - len(content.lstrip(" "))
            # Check if it's a test line (has status symbol)
            test_match = re.search(r"\s*([✔✓√✖⚠])\s+(.*)", content)
            if test_match:
                status = test_match.group(1)
                test_desc = test_match.group(2).strip()
                # Get current group from stack
                current_group = " ".join([g[0] for g in stack]) if stack else ""
                test_name = (
                    f"{current_group} {test_desc}".strip()
                    if current_group
                    else test_desc
                )
                # Determine status
                if status == "✔":
                    passed_tests.add(test_name)
                elif status == "✖":
                    failed_tests.add(test_name)
                elif status == "⚠":
                    # Handle slow tests if needed; for now, skip
                    pass
                else:
                    # Unknown status
                    pass
            else:
                # It's a group line
                group_text = content.strip()
                if not group_text:
                    continue  # Skip empty lines
                # Skip non-test group lines (contains log keywords)
                non_test_keywords = {
                    "ERROR",
                    "INFO",
                    "WARN",
                    "yarn",
                    "node",
                    "Compiled",
                    "Built",
                    "Starting",
                    "Finished",
                    "Time:",
                    "Entrypoint",
                    "Browserslist",
                    "Error from chokidar",
                }
                if any(keyword in group_text for keyword in non_test_keywords):
                    continue
                # Pop stack until we find a group with indent_level < current indent_level
                while stack and stack[-1][1] >= indent_level:
                    stack.pop()
                stack.append((group_text, indent_level))
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
