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
yarn ci-check:tests
###ACTION_DELIMITER###
apt-get update && apt-get install -y libatk1.0-0 libatk-bridge2.0-0 libcups2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2
###ACTION_DELIMITER###
yarn ci-check:tests
###ACTION_DELIMITER###
apt-get update && apt-get install -y libnss3 libnspr4
###ACTION_DELIMITER###
yarn playwright install-deps
###ACTION_DELIMITER###
yarn ci-check:tests
###ACTION_DELIMITER###
yarn build:packages
###ACTION_DELIMITER###
echo 'yarn ci-check:tests' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn ci-check:tests

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
yarn ci-check:tests

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
yarn ci-check:tests

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

# Choose an appropriate base image based on the project's requirements - replace node:20 with actual base image
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
RUN git clone https://github.com/carbon-design-system/ibm-products.git /home/ibm-products

WORKDIR /home/ibm-products
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("carbon-design-system", "ibm_products_7830_to_7681")
class IBM_PRODUCTS_7830_TO_7681(Instance):
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
        # Remove ANSI escape codes from the log content
        clean_log = re.sub(r'\x1b\[[0-9;]*m', '', log)
        lines = clean_log.split('\n')
        # Regex pattern to match test status lines (PASS/FAIL/SKIPPED)
        # Match ibm-products and web-components with PASS/FAIL/SKIPPED status
        # Adjusted pattern to capture SKIPPED tests and handle varying whitespace
        # Case-insensitive and handles optional parentheses after status
        test_pattern = re.compile(r'(?i)@carbon/(?:ibm-products|ibm-products-web-components):\s+(PASS|FAIL|SKIPPED)\s+(?:\(.*?\)\s+)?(.*?)(?:\s+\(|\s*$)')
        # Capture skipped tests from summary lines (extract count, but names may require additional logic)
        summary_skipped_pattern = re.compile(r'Tests:\s+.*?(\d+)\s+skipped')
        # Match failed tests from error messages (test name in group 1)
        error_pattern = re.compile(r'@carbon/(?:ibm-products|ibm-products-web-components):.*?\((src/.*?\.test\.(?:js|ts)):\d+:\d+\)')
        # Match skipped tests from individual lines (if present)
        skipped_test_pattern = re.compile(r'@carbon/(?:ibm-products|ibm-products-web-components):\s+SKIPPED\s+(.*?)(?:\s+\(|\s*$)')
        for line in lines:
            # Extract tests from status lines (PASS/FAIL/SKIPPED)
            test_match = test_pattern.search(line)
            if test_match:
                status = test_match.group(1).upper()
                test_name = test_match.group(2).strip()
                if status == 'PASS':
                    passed_tests.add(test_name)
                elif status == 'FAIL':
                    failed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
            # Extract skipped tests from individual lines
            skipped_match = skipped_test_pattern.search(line)
            if skipped_match:
                test_name = skipped_match.group(1).strip()
                skipped_tests.add(test_name)
            # Extract failed tests from error messages
            error_match = error_pattern.search(line)
            if error_match:
                test_name = error_match.group(1).strip()
                failed_tests.add(test_name)
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
