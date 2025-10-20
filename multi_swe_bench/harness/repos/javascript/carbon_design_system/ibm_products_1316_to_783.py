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
                """ls -la
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && source $HOME/.nvm/nvm.sh && nvm install lts/fermium && nvm use lts/fermium
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo 'lerna run test --stream -- --ci --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'yarn lerna run test --stream -- --ci --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'yarn lerna run test --stream -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'yarn lerna run test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo './node_modules/.bin/lerna run test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo 'yarn test --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo 'yarn lerna run test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo 'yarn test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo './node_modules/.bin/lerna run test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo './node_modules/.bin/lerna run test -- -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo 'lerna exec -- jest --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo './node_modules/.bin/lerna exec -- jest --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo './node_modules/.bin/lerna run test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo './node_modules/.bin/lerna run test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo './node_modules/.bin/lerna exec -- ../node_modules/.bin/jest --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo './node_modules/.bin/lerna exec -- ../../node_modules/.bin/jest --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo 'yarn test --ci' > test_commands.sh
###ACTION_DELIMITER###
echo './node_modules/.bin/lerna run test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo 'PATH=$PWD/node_modules/.bin:$PATH ./node_modules/.bin/lerna run test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo './node_modules/.bin/lerna exec -- ../../node_modules/.bin/jest --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo './node_modules/.bin/lerna exec -- ../../node_modules/.bin/jest --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo './node_modules/.bin/lerna exec -- ../../node_modules/.bin/jest --verbose --passWithNoTests' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
./node_modules/.bin/lerna exec -- ../../node_modules/.bin/jest --verbose --passWithNoTests

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
./node_modules/.bin/lerna exec -- ../../node_modules/.bin/jest --verbose --passWithNoTests

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
./node_modules/.bin/lerna exec -- ../../node_modules/.bin/jest --verbose --passWithNoTests

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
RUN git clone https://github.com/carbon-design-system/ibm-products.git /home/ibm-products

WORKDIR /home/ibm-products
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("carbon-design-system", "ibm_products_1316_to_783")
class IBM_PRODUCTS_1316_TO_783(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        from collections import defaultdict
        # Track test context: suite, describe blocks, and current indentation
        test_context = []
        suite = ''
        indent_levels = defaultdict(int)
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        # Regex patterns
        suite_pattern = re.compile(r'^(PASS|FAIL) (src/.*\.(spec|test)\.js)')
        describe_pattern = re.compile(r'^(\s*)(\w+.*)$')  # Nested describe blocks
        test_pattern = re.compile(r'^(\s*)(✓|✕|-)\s*(.*?)\s*\(\d+ ms\)$')  # Tests with status
        for line in log.split('\n'):
            # Update suite context
            suite_match = suite_pattern.search(line)
            if suite_match:
                suite = suite_match.group(2)
                test_context = [suite]
                indent_levels = defaultdict(int)
                continue
            # Update describe blocks (track indentation)
            describe_match = describe_pattern.search(line)
            if describe_match and '✓' not in line and '✕' not in line:
                indent = len(describe_match.group(1))
                block = describe_match.group(2).strip()
                # Determine parent context based on indentation
                parent_level = max([l for l in indent_levels if l < indent], default=-1)
                if parent_level == -1:
                    test_context = [suite, block]
                else:
                    test_context = test_context[:indent_levels[parent_level]+1] + [block]
                indent_levels[indent] = len(test_context)-1
                continue
            # Match individual tests and categorize
            test_match = test_pattern.search(line)
            if test_match:
                status = test_match.group(2)
                test_name = test_match.group(3).strip()
                full_test_name = ' '.join(test_context + [test_name])
                if status == '✓':
                    passed_tests.add(full_test_name)
                elif status == '✕':
                    failed_tests.add(full_test_name)
                elif status == '-':  # Assume '-' for skipped (adjust if needed)
                    skipped_tests.add(full_test_name)
        # Handle skipped tests from summary (if no individual markers)
        skipped_summary = re.search(r'Tests:.*? (\d+) skipped', log)
        if skipped_summary and not skipped_tests:
            # Placeholder: If no individual skipped tests, mark them (adjust logic as needed)
            skipped_tests.add(f'Skipped {skipped_summary.group(1)} tests (see log summary)')
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
