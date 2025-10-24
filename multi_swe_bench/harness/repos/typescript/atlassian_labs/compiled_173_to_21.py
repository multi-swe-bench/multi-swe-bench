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
        return "node:14-bullseye"

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
cat .nvmrc
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
###ACTION_DELIMITER###
nvm install 12.10.0
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo 'yarn test -- --verbose' > test_commands.sh
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

# Choose an appropriate base image based on the project's requirements - replace node:14-bullseye with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:14-bullseye

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
RUN git clone https://github.com/atlassian-labs/compiled.git /home/compiled

WORKDIR /home/compiled
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("atlassian-labs", "compiled_173_to_21")
class COMPILED_173_TO_21(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        suite_stack = []
        current_test_name = None
        import re

        # Define regex patterns with flexible matching
        passed_pattern = re.compile(
            r"✓\s+(.*)", re.UNICODE
        )  # Capture everything after ✓
        skipped_pattern = re.compile(
            r"○ skipped\s+(.*)", re.UNICODE
        )  # Capture everything after ○ skipped
        test_name_pattern = re.compile(
            r'^\s*(?:\[\s*\d+\s*\]\s*)?(?:it|test)\(\s*["\'](.*?)["\']\s*\)', re.UNICODE
        )
        failed_pattern = re.compile(
            r"^\s*(?:\[\s*\d+\s*\]\s*)?(✗|✕|×|x|●|✖|✘)\s+(.*)|^\s*(?:\[\s*\d+\s*\]\s*)?at Object\.<anonymous>.*",
            re.UNICODE,
        )  # Capture failure symbols or error lines
        # Pattern for top-level PASS/FAIL suite lines (ignore line numbers)
        suite_pass_pattern = re.compile(
            r"^\s*\[\s*\d+\s*\]\s*PASS\s+(.*?)(?:\s+\(\d+ms\))?$", re.UNICODE
        )  # Greedy match for full suite name
        suite_fail_pattern = re.compile(
            r"^\s*\[\s*\d+\s*\]\s*FAIL\s+(.*?)(?:\s+\(\d+ms\))?$", re.UNICODE
        )  # Greedy match for full suite name
        # Pattern for indented suite lines (ignore line numbers, capture indentation)
        indented_suite_pattern = re.compile(
            r"^\s*\[\s*\d+\s*\]\s*(\s+)(.*)$", re.UNICODE
        )
        for line in log.split("\n"):
            line = line.rstrip()  # Remove trailing whitespace
            if not line:
                continue
            # Check for top-level PASS/FAIL suite lines (allow leading content)
            pass_suite_match = suite_pass_pattern.search(line)
            if pass_suite_match:
                suite_name = pass_suite_match.group(1)
                suite_stack = [suite_name]
                continue
            fail_suite_match = suite_fail_pattern.search(line)
            if fail_suite_match:
                suite_name = fail_suite_match.group(1)
                suite_stack = [suite_name]
                continue
            # Check for indented suite lines
            indented_suite_match = indented_suite_pattern.match(line)
            if indented_suite_match:
                spaces, suite_name = indented_suite_match.groups()
                indent_level = len(spaces) // 2  # Assuming 2 spaces per level
                # Adjust suite stack to current indent level
                while len(suite_stack) > indent_level:
                    suite_stack.pop()
                # Add current suite name if it's not empty
                if suite_name.strip():
                    suite_stack.append(suite_name.strip())
                continue
            # Check for test names in it/test blocks
            test_match = test_name_pattern.search(line)
            if test_match:
                current_test_name = test_match.group(1)
                continue
            # Check for passed tests
            passed_match = passed_pattern.search(line)
            if passed_match:
                test_name = passed_match.group(1).strip()
                full_test_name = (
                    " > ".join(suite_stack + [test_name]) if suite_stack else test_name
                )
                passed_tests.add(full_test_name)
                continue
            # Check for skipped tests
            skipped_match = skipped_pattern.search(line)
            if skipped_match:
                test_name = skipped_match.group(1).strip()
                full_test_name = (
                    " > ".join(suite_stack + [test_name]) if suite_stack else test_name
                )
                skipped_tests.add(full_test_name)
                continue
            # Check for failed tests
            failed_match = failed_pattern.search(line)
            if failed_match:
                test_name = (
                    failed_match.group(2).strip()
                    if failed_match.group(2)
                    else current_test_name
                )
                if test_name:
                    full_test_name = (
                        " > ".join(suite_stack + [test_name])
                        if suite_stack
                        else test_name
                    )
                    failed_tests.add(full_test_name)
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
