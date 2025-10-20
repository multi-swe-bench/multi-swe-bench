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
        return "node:20"
    
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
corepack prepare yarn@4.7.0 --activate
###ACTION_DELIMITER###
yarn install --no-optional
###ACTION_DELIMITER###
yarn install --immutable
###ACTION_DELIMITER###
yarn test
###ACTION_DELIMITER###
echo 'yarn test --verbose' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn test --verbose

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
yarn test --verbose

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
yarn test --verbose

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
FROM node:20

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


@Instance.register("VKCOM", "VKUI_8325_to_8268")
class VKUI_8325_TO_8268(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        current_suite_parts = []
        lines = log.split('\n')
        for line in lines:
            leading_spaces = len(line) - len(line.lstrip(' '))
            stripped_line = line.strip()
            if not stripped_line:
                continue
            # Check for suite header (0 leading spaces, starts with [num])
            if leading_spaces == 0 and re.match(r'^\[\s*\d+\]', stripped_line):
                current_suite_parts = []
                continue
            # Main suite (2 leading spaces)
            if leading_spaces == 2:
                current_suite_parts = [stripped_line]
                continue
            # Level 2 (4 leading spaces): sub-suite or test case under main suite
            if leading_spaces == 4:
                if stripped_line.startswith(('✓', '✕', '○', 'x')):
                    symbol = stripped_line[0]
                    test_name_part = stripped_line[1:].split('(')[0].strip()
                    full_test_name = ' '.join(current_suite_parts) + ' ' + test_name_part
                    if symbol in ('✓',):
                        passed_tests.add(full_test_name)
                    elif symbol in ('✕', 'x'):
                        failed_tests.add(full_test_name)
                    elif symbol in ('○',):
                        skipped_tests.add(full_test_name)
                else:
                    current_suite_parts.append(stripped_line)
                continue
            # Level 3 (6 leading spaces): test case under sub-suite
            if leading_spaces == 6:
                if stripped_line.startswith(('✓', '✕', '○', 'x')):
                    symbol = stripped_line[0]
                    test_name_part = stripped_line[1:].split('(')[0].strip()
                    full_test_name = ' '.join(current_suite_parts) + ' ' + test_name_part
                    if symbol in ('✓',):
                        passed_tests.add(full_test_name)
                    elif symbol in ('✕', 'x'):
                        failed_tests.add(full_test_name)
                    elif symbol in ('○',):
                        skipped_tests.add(full_test_name)
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
