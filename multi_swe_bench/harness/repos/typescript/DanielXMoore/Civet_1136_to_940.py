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
                """ls -la node_modules/.bin | grep c8
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
###ACTION_DELIMITER###
apt-get install -y nodejs
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo 'bash ./build/test.sh' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls node_modules/.bin | grep c8
###ACTION_DELIMITER###
echo 'yarn test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
tsc --noEmit
###ACTION_DELIMITER###
ls node_modules/.bin | grep tsc
###ACTION_DELIMITER###
echo -e 'export PATH="./node_modules/.bin:$PATH"
bash ./build/test.sh' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
tsc --noEmit
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash -x test_commands.sh
###ACTION_DELIMITER###
./node_modules/.bin/tsc --noEmit"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
export PATH="./node_modules/.bin:$PATH"
bash ./build/test.sh

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
export PATH="./node_modules/.bin:$PATH"
bash ./build/test.sh

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
export PATH="./node_modules/.bin:$PATH"
bash ./build/test.sh

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


@Instance.register("DanielXMoore", "Civet_1136_to_940")
class CIVET_1136_TO_940(Instance):
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
        passed_tests = set[str]() # Tests that passed successfully
        failed_tests = set[str]() # Tests that failed
        skipped_tests = set[str]() # Tests that were skipped
        import re
        # Prioritize summary counts for total test numbers
        # Extract individual test cases from log entries
        # Adjust patterns to match actual test status indicators in the log
        # Extract summary counts first
        summary_passed_pattern = re.compile(r'(\d+) passing', re.MULTILINE)
        summary_passed = summary_passed_pattern.findall(log)
        summary_skipped_pattern = re.compile(r'(\d+) pending', re.MULTILINE)
        summary_skipped = summary_skipped_pattern.findall(log)
        summary_failed_pattern = re.compile(r'(\d+) failing', re.MULTILINE)
        summary_failed = summary_failed_pattern.findall(log)
        # Extract test names from symbolic output and error contexts
        # Symbolic blocks (e.g., '.' for passed, ',' for skipped, '!' for failed)
        symbolic_pattern = re.compile(r'([.,!])', re.MULTILINE)
        symbolic_matches = symbolic_pattern.findall(log)
        # Map symbols to test statuses (simplified example)
        test_index = 0
        for symbol in symbolic_matches:
            test_name = f'test_{test_index + 1}'
            if symbol == '.':
                passed_tests.add(test_name)
            elif symbol == '!':
                failed_tests.add(test_name)
            elif symbol == ',':
                skipped_tests.add(test_name)
            test_index += 1
        # Extract explicit test names from error messages
        error_test_pattern = re.compile(r'Error in test (.+?):', re.MULTILINE)
        error_tests = error_test_pattern.findall(log)
        failed_tests.update(error_tests)
        # Remove failed tests from passed set
        passed_tests -= failed_tests
        # Use summary counts if available, else symbolic blocks
        total_passed = int(summary_passed[0]) if summary_passed else 0
        total_skipped = int(summary_skipped[0]) if summary_skipped else 0
        total_failed = int(summary_failed[0]) if summary_failed else 0
        # Generate generic test names for unmatched tests
        passed_generic_count = max(0, total_passed - len(passed_tests))
        passed_tests = passed_tests.union({f'test_{i+1}' for i in range(passed_generic_count)})
        failed_generic_count = max(0, total_failed - len(failed_tests))
        failed_tests = failed_tests.union({f'failed_test_{i+1}' for i in range(failed_generic_count)})
        skipped_generic_count = max(0, total_skipped - len(skipped_tests))
        skipped_tests = skipped_tests.union({f'skipped_test_{i+1}' for i in range(skipped_generic_count)})
        # Validate summary counts against explicit tests
        if summary_passed:
            expected_passed = int(summary_passed[0])
            if len(passed_tests) != expected_passed:
                print(f"Warning: Combined passed tests ({len(passed_tests)}) do not match summary ({expected_passed})")
        if summary_skipped:
            expected_skipped = int(summary_skipped[0])
            if len(skipped_tests) != expected_skipped:
                print(f"Warning: Combined skipped tests ({len(skipped_tests)}) do not match summary ({expected_skipped})")
        if summary_failed:
            expected_failed = int(summary_failed[0])
            if len(failed_tests) != expected_failed:
                print(f"Warning: Combined failed tests ({len(failed_tests)}) do not match summary ({expected_failed})")
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
