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
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
###ACTION_DELIMITER###
nvm install
###ACTION_DELIMITER###
npm ci
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###

###ACTION_DELIMITER###

###ACTION_DELIMITER###
npm config get registry
###ACTION_DELIMITER###
yarn config get registry
###ACTION_DELIMITER###
yarn config set @liskhq:registry https://registry.npmjs.org
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
grep -r 'npm.lisk.com' yarn.lock
###ACTION_DELIMITER###
sed -i 's|https://npm.lisk.com|https://registry.npmjs.org|g' yarn.lock
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
npm view @liskhq/lisk-client versions
###ACTION_DELIMITER###
yarn add @liskhq/lisk-client@6.0.0
###ACTION_DELIMITER###
nvm install 18 && nvm use 18
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
npm view @liskhq/lisk-api-client versions
###ACTION_DELIMITER###
yarn add @liskhq/lisk-api-client@6.0.0
###ACTION_DELIMITER###
yarn add @liskhq/lisk-api-client@6.0.0
###ACTION_DELIMITER###
sed -i 's/"@liskhq\/lisk-client": "6.0.0-alpha.21"/"@liskhq\/lisk-client": "6.0.0"/g' package.json
###ACTION_DELIMITER###
sed -i 's|"@liskhq/lisk-client": "6.0.0-alpha.21"|"@liskhq/lisk-client": "6.0.0"|g' package.json
###ACTION_DELIMITER###
grep '@liskhq/lisk-client' package.json
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
yarn test -- --verbose
###ACTION_DELIMITER###
echo 'yarn test -- --verbose' > test_commands.sh""",
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
RUN git clone https://github.com/LiskHQ/lisk-mobile.git /home/lisk-mobile

WORKDIR /home/lisk-mobile
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("LiskHQ", "lisk_mobile_1786_to_1780")
class LISK_MOBILE_1786_TO_1780(Instance):
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
        passed_tests: set[str] = set()
        failed_tests: set[str] = set()
        skipped_tests: set[str] = set()
        import re

        current_hierarchy: list[str] = []
        lines = log.split("\n")
        for line in lines:
            # Check if the line is a test case
            test_match = re.match(r"^\s*([✓✕○−-])\s+(.*?)(?:\s+\(\d+ ms\))?$", line)
            if test_match:
                symbol = test_match.group(1)
                test_name = test_match.group(2)
                # Calculate leading spaces to determine hierarchy level
                leading_spaces = len(line) - len(line.lstrip(" "))
                level = leading_spaces // 2
                # Construct full test name from hierarchy and test name
                if current_hierarchy:
                    full_test_name = " › ".join(current_hierarchy) + " › " + test_name
                else:
                    full_test_name = test_name
                # Classify based on symbol
                if symbol == "✓":
                    passed_tests.add(full_test_name)
                elif symbol == "✕":
                    failed_tests.add(full_test_name)
                elif symbol == "○":
                    skipped_tests.add(full_test_name)
                elif symbol == "−":
                    skipped_tests.add(full_test_name)
                elif symbol == "-":
                    skipped_tests.add(full_test_name)
                continue
            # Check if the line is a describe block (ignore error messages)
            if line.lstrip().startswith("●"):
                continue
            describe_match = re.match(r"^\s*([^\s].*?)\s*$", line)
            if describe_match:
                describe_name = describe_match.group(1)
                leading_spaces = len(line) - len(line.lstrip(" "))
                level = leading_spaces // 2
                # Update the current hierarchy to the current level
                current_hierarchy = current_hierarchy[: level - 1] + [describe_name]
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
