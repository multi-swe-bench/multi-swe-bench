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
apt-get update
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
###ACTION_DELIMITER###
apt-get install nodejs -y
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo 'c8 mocha --reporter spec' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'yarn test -- --reporter spec' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
yarn build
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'c8 mocha --loader ts-node/esm --loader ./build/coffee-esm.mjs --loader ./build/hera-esm.mjs --loader ./dist/esm.mjs --reporter spec test' > test_commands.sh
###ACTION_DELIMITER###
echo 'NODE_OPTIONS="--experimental-loader ts-node/esm --experimental-loader ./build/coffee-esm.mjs --experimental-loader ./build/hera-esm.mjs --experimental-loader ./dist/esm.mjs" c8 mocha --reporter spec test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'yarn test -- --reporter spec' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'NODE_OPTIONS="--import ./build/coffee-esm.mjs --import ./build/hera-esm.mjs --import ./dist/esm.mjs" yarn test -- --reporter spec' > test_commands.sh
###ACTION_DELIMITER###
echo 'NODE_OPTIONS="--import ./build/coffee-esm.mjs --import ./build/hera-esm.mjs --import ./dist/esm.mjs" yarn test -- --reporter spec --extension hera' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'ts-node --esm node_modules/mocha/bin/mocha --loader ./build/coffee-esm.mjs --loader ./build/hera-esm.mjs --loader ./dist/esm.mjs --reporter spec test' > test_commands.sh
###ACTION_DELIMITER###
echo 'NODE_OPTIONS="--experimental-loader ts-node/esm --experimental-loader ./build/coffee-esm.mjs --experimental-loader ./build/hera-esm.mjs --experimental-loader ./dist/esm.mjs" yarn test -- --reporter spec' > test_commands.sh
###ACTION_DELIMITER###
echo 'NODE_OPTIONS="--import ts-node/esm --import ./build/coffee-esm.mjs --import ./build/hera-esm.mjs --import ./dist/esm.mjs" yarn test -- --reporter spec --extension ts' > test_commands.sh
###ACTION_DELIMITER###
echo 'NODE_OPTIONS="--import ts-node/esm --import ./build/coffee-esm.mjs --import ./build/hera-esm.mjs --import ./dist/esm.mjs" yarn test -- --reporter spec --extension ts,civet,coffee,hera' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
NODE_OPTIONS="--import ts-node/esm --import ./build/coffee-esm.mjs --import ./build/hera-esm.mjs --import ./dist/esm.mjs" yarn test -- --reporter spec --extension ts,civet,coffee,hera

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
NODE_OPTIONS="--import ts-node/esm --import ./build/coffee-esm.mjs --import ./build/hera-esm.mjs --import ./dist/esm.mjs" yarn test -- --reporter spec --extension ts,civet,coffee,hera

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
NODE_OPTIONS="--import ts-node/esm --import ./build/coffee-esm.mjs --import ./build/hera-esm.mjs --import ./dist/esm.mjs" yarn test -- --reporter spec --extension ts,civet,coffee,hera

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
RUN git clone https://github.com/DanielXMoore/Civet.git /home/Civet

WORKDIR /home/Civet
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("DanielXMoore", "Civet_654_to_479")
class CIVET_654_TO_479(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re
        import json
        # Track nested sections and extract full test names
        sections = []
        for line in log.split('\n'):
            # Reset sections on summary lines
            if re.search(r'(passing|pending|failing)', line):
                sections = []
            # Update sections based on indentation (2 spaces per level)
            section_match = re.match(r'^(\s+)([a-zA-Z].*)$', line)
            if section_match:
                indent = len(section_match.group(1))
                section_name = section_match.group(2).strip()
                level = indent // 2
                sections = sections[:level] + [section_name]
            # Capture tests with status symbols or text indicators
            # Check for passed tests (✔)
            passed_match = re.match(r'^\s+✔\s+(.*)$', line)
            if passed_match:
                test_name = passed_match.group(1).strip()
                full_test_name = test_name
                passed_tests.add(full_test_name)
            # Check for failed tests (symbol: x)
            failed_match = re.match(r'^\s+\d+\)\s+(.*?)(?=:|$)', line)
            if failed_match:
                test_name = failed_match.group(1).strip()
                full_test_name = test_name
                failed_tests.add(full_test_name)
            # Check for failed tests in summary (error exit code)
            if 'error Command failed with exit code 1' in line:
                # Fallback: Assume 1 failed test if exit code 1 and no failed tests captured
                if not failed_tests:
                    failed_tests.add('Unknown failed test')
            # Check for skipped tests (text: pending)
            skipped_match = re.search(r'pending[:\s]+(.*)$', line, re.IGNORECASE)
            if skipped_match:
                test_name = skipped_match.group(1).strip()
                full_test_name = test_name
                skipped_tests.add(full_test_name)
        # Handle pending tests (skipped) from summary lines
        pending_match = re.search(r'(\d+) pending', log)
        if pending_match and not skipped_tests:
            pending_count = int(pending_match.group(1))
            # Add generic pending test names if individual tests aren't captured
            skipped_tests = {f'Pending test {i+1}' for i in range(pending_count)}
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
