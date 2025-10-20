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
                """node -v
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && source ~/.nvm/nvm.sh && nvm install 12 && nvm use 12
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
lerna run test --parallel -- --verbose
###ACTION_DELIMITER###
npx lerna run test --parallel -- --verbose
###ACTION_DELIMITER###
npm install -g yarn && yarn install --legacy-peer-deps
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && yarn install --legacy-peer-deps
###ACTION_DELIMITER###
yarn lerna run test --parallel -- --verbose
###ACTION_DELIMITER###
npx lerna run test --parallel -- --verbose
###ACTION_DELIMITER###
yarn build
###ACTION_DELIMITER###
npx lerna run test --parallel -- --verbose
###ACTION_DELIMITER###
echo 'npx lerna run test --parallel -- --verbose' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npx lerna run test --parallel -- --verbose

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
npx lerna run test --parallel -- --verbose

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
npx lerna run test --parallel -- --verbose

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
RUN git clone https://github.com/Royal-Navy/design-system.git /home/design-system

WORKDIR /home/design-system
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Royal-Navy", "design_system_1014_to_unknown")
class DESIGN_SYSTEM_1014_TO_UNKNOWN(Instance):
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
        passed_tests = set() # Tests that passed successfully
        failed_tests = set() # Tests that failed
        skipped_tests = set() # Tests that were skipped
        import re
        # Track test context (describe blocks) and parse results
        context_stack = []
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        # Regex patterns for test suites, lines, and describe blocks
        suite_pattern = re.compile(r'^(PASS|FAIL|SKIPPED) (.*)$')
        test_line_pattern = re.compile(r'^(\s*)(✓|✕|○) (.*?) (?:\(\d+ ms\))?$')
        describe_block_pattern = re.compile(r'^(\s*)(.*?)\s*$')
        for line in log.split('\n'):
            # Remove package prefixes (e.g., 'royalnavy.io: ')
            line = re.sub(r'^\[\s*\d+\]\s*', '', line)  # Remove line numbers
            line = re.sub(r'^[^:]+: ', '', line).rstrip('\r')  # Remove package prefixes
            line = re.sub(r'\(\d+\)\s*\.\.\.\s*[{}[\]()\d\s,.]+', '', line)  # Remove log artifacts
            # Capture test suite path and reset context stack
            suite_match = suite_pattern.match(line)
            if suite_match:
                context_stack = []  # Reset context for new suite
                continue
            # Capture test results with full context
            test_match = test_line_pattern.match(line)
            if test_match:
                indent = len(test_match.group(1))
                status = test_match.group(2)
                test_desc = test_match.group(3).strip()
                # Determine context level from indentation (6 spaces for tests → level 3)
                context_level = indent // 2
                full_context = ' '.join(context_stack[:context_level])
                full_test_name = f'{full_context} {test_desc}'.strip()
                if status == '✓':
                    passed_tests.add(full_test_name)
                elif status == '✕':
                    failed_tests.add(full_test_name)
                elif status == '○':
                    skipped_tests.add(full_test_name)
            # Update context stack with describe blocks (indented sections)
            describe_match = describe_block_pattern.match(line)
            if describe_match:
                indent = len(describe_match.group(1))
                desc = describe_match.group(2).strip()
                if desc:
                    # Adjust stack based on indentation level (2 spaces per level)
                    level = indent // 2
                    context_stack = context_stack[:level] + [desc]
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
