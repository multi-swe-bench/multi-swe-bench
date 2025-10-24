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
yarn install
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
###ACTION_DELIMITER###
nvm install
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo 'lerna run --parallel test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'npx lerna run --parallel test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
npx lerna bootstrap
###ACTION_DELIMITER###
sed -i '6i  "useWorkspaces": true,' lerna.json
###ACTION_DELIMITER###
cat lerna.json
###ACTION_DELIMITER###
npx lerna bootstrap
###ACTION_DELIMITER###
npx lerna run build
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npx lerna run --parallel test -- --verbose

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
npx lerna run --parallel test -- --verbose

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
npx lerna run --parallel test -- --verbose

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
RUN git clone https://github.com/Royal-Navy/design-system.git /home/design-system

WORKDIR /home/design-system
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Royal-Navy", "design_system_1269_to_1024")
class DESIGN_SYSTEM_1269_TO_1024(Instance):
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

        # Parse log lines to extract test names and statuses
        line_re = re.compile(
            r"^(\s*)(.*)$"
        )  # Capture leading whitespace and content for all lines
        passed_re = re.compile(r"✓ (.*?) \(\d+ ms\)$")  # Matches passed test lines
        failed_re = re.compile(
            r"✕ (.*?) \(\d+ ms\)$"
        )  # Matches failed test lines (if '✕' is used)
        error_re = re.compile(
            r"^\s*>\s*\d+ \|.*$"
        )  # Matches error lines indicating failed tests
        skipped_re = re.compile(r"SKIPPED (.*)$")  # Matches skipped test lines
        context_stack = []
        for line in log.split("\n"):
            # Remove timestamp prefix (e.g., [123] ) and package name prefix (e.g., royalnavy.io: )
            cleaned_line = re.sub(r"^\[\d+\]\s*", "", line)
            cleaned_line = re.sub(r"^.*?:\s*", "", cleaned_line)
            match = line_re.match(cleaned_line)
            if not match:
                continue
            indent = match.group(1)
            content = match.group(2)
            level = len(indent) // 2  # Assume 2 spaces per indent level
            # Check for passed tests
            passed_match = passed_re.match(content)
            if passed_match:
                test_desc = passed_match.group(1)
                test_name = " ".join(context_stack + [test_desc])
                passed_tests.add(test_name)
                continue
            # Check for failed tests
            failed_match = failed_re.match(content)
            if failed_match:
                test_desc = failed_match.group(1)
                test_name = " ".join(context_stack + [test_desc])
                failed_tests.add(test_name)
                continue
            # Check for skipped tests
            skipped_match = skipped_re.match(content)
            if skipped_match:
                test_desc = skipped_match.group(1)
                test_name = " ".join(context_stack + [test_desc])
                skipped_tests.add(test_name)
                continue
            # Skip test suite lines (e.g., PASS, FAIL)
            test_suite_re = re.compile(r"^(PASS|FAIL|SKIPPED) .*$")
            if test_suite_re.match(content):
                # Check for error lines in test suite lines
                if error_re.match(line) and context_stack:
                    test_name = " ".join(context_stack)
                    failed_tests.add(test_name)
                continue
            # Update context stack based on indentation level
            while len(context_stack) > level:
                context_stack.pop()
            while len(context_stack) < level:
                context_stack.append("")
            if len(context_stack) == level:
                context_stack.append(content)
            else:
                context_stack[level] = content
            # Check for error lines indicating failed tests
            if error_re.match(line) and context_stack:
                test_name = " ".join(context_stack)
                failed_tests.add(test_name)
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
