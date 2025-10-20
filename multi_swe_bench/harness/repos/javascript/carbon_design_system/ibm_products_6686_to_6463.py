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
                """yarn install
###ACTION_DELIMITER###
echo 'yarn ci-check:tests' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libatspi2.0-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libdrm2 libxkbcommon0 libasound2
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libcups2
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libx11-xcb1 libxcursor1 libgtk-3-0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
yarn playwright install-deps
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
"""
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
RUN git clone https://github.com/carbon-design-system/ibm-products.git /home/ibm-products

WORKDIR /home/ibm-products
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("carbon-design-system", "ibm_products_6686_to_6463")
class IBM_PRODUCTS_6686_TO_6463(Instance):
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
        # Remove ANSI escape codes
        clean_log = re.sub(r'\x1b\[[0-9;]*m', '', log)
        lines = clean_log.split('\n')
        # Patterns for test statuses
        pass_patterns = [
            re.compile(r'✓[:\s]+([^\s(]+)'),
            re.compile(r'([^\s(]+)[:\s]+✓'),
            re.compile(r'PASS[:\s]+([^\s(]+)'),
            re.compile(r'([^\s(]+)[:\s]+PASS'),
            re.compile(r'PASSED[:\s]+([^\s(]+)'),
            re.compile(r'([^\s(]+)[:\s]+PASSED')
        ]
        fail_patterns = [
            re.compile(r'✗[:\s]+([^\s(]+)'),
            re.compile(r'FAIL[:\s]+([^\s(]+)'),
            re.compile(r'FAILED[:\s]+([^\s(]+)'),
            re.compile(r'([^\s(]+)\s+\(failed\)')
        ]
        skip_patterns = [
            re.compile(r'(src/[^\s(]+).*?skipped', re.IGNORECASE),
            re.compile(r'skipped.*?(src/[^\s(]+)', re.IGNORECASE),
            re.compile(r'(src/[^\s(]+).*?skip', re.IGNORECASE),
            re.compile(r'skip.*?(src/[^\s(]+)', re.IGNORECASE)
        ]
        for line in lines:
            # Check for passed tests
            for pattern in pass_patterns:
                match = pattern.search(line)
                if match:
                    passed_tests.add(match.group(1).strip())
                    break
            else:
                # Check for failed tests
                for pattern in fail_patterns:
                    match = pattern.search(line)
                    if match:
                        failed_tests.add(match.group(1).strip())
                        break
                else:
                    # Check for skipped tests
                    for pattern in skip_patterns:
                        match = pattern.search(line)
                        if match:
                            skipped_tests.add(match.group(1).strip())
                            break
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
