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
apt-get update
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn test-ui --verbose
yarn cypress-run' > test_commands.sh
###ACTION_DELIMITER###
sed -i '3s/$/ --reporter json/' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn test --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn test-ui --ci --verbose --maxWorkers=1' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn test-ui --verbose --watchAll=false --forceExit --maxWorkers=1' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
# Start server in background
yarn start &
# Wait for server to be ready
wait-on http-get://0.0.0.0:8401
# Run tests with verbose output
yarn test-ui --verbose --watchAll=false --ci --maxWorkers=2
# Stop server
pkill -f "react-scripts start" || true
pkill -f "nodemon ./scripts/proxy.js" || true' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn test-ui --verbose --watchAll=false --ci --maxWorkers=1 --forceExit' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn test-ui --verbose --watchAll=false --ci --runInBand --forceExit' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn test-ui --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn test-ui --verbose --ci --forceExit' > test_commands.sh
###ACTION_DELIMITER###
apt-get install -y build-essential
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn test-ui --verbose --ci --maxWorkers=2 --forceExit' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
CI=true yarn test-ui --verbose --watchAll=false' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
# Start server in background
yarn start &
# Wait for server to be ready
yarn show-ready
# Run tests with verbose output
yarn test-ui --verbose
# Stop server
pkill -f "react-scripts start" || true
pkill -f "nodemon ./scripts/proxy.js" || true' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn test-ui --verbose --ci --maxWorkers=1 --no-cache --forceExit' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
CI=true yarn test-ui --verbose --watchAll=false' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
CI=true yarn test-ui --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
CI=true yarn test-ui --verbose --runInBand --forceExit --ci' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
CI=true yarn test-ui --verbose --forceExit' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
CI=true yarn test-ui --verbose --forceExit --maxWorkers=1' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
CI=true yarn test-ui --verbose --ci --maxWorkers=1 --no-cache --forceExit' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
CI=true yarn test-ui --verbose --maxWorkers=1 --forceExit' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
CI=true yarn test-ui --verbose --maxWorkers=1 --forceExit' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
CI=true yarn test-ui --verbose' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
CI=true yarn test-ui --verbose --maxWorkers=1 --forceExit' > test_commands.sh && chmod +x test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
CI=true yarn test-ui --verbose --maxWorkers=1 --forceExit

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
#!/bin/bash
CI=true yarn test-ui --verbose --maxWorkers=1 --forceExit

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
#!/bin/bash
CI=true yarn test-ui --verbose --maxWorkers=1 --forceExit

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
RUN git clone https://github.com/canonical/maas-ui.git /home/maas-ui

WORKDIR /home/maas-ui
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("canonical", "maas_ui_4111_to_1899")
class MAAS_UI_4111_TO_1899(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re

        # Track nested describe blocks and test statuses
        current_describes = []
        # Regex patterns for test cases and describe blocks
        test_case_pattern = re.compile(
            r"^\s{2,}(✓|✕|○)\s+(.*?)\s*\(\d+ ms\)$"
        )  # Matches indented test cases
        describe_block_pattern = re.compile(
            r"^\s{2,}(.*)$"
        )  # Matches indented describe blocks
        for line in log.split("\n"):
            line = line.rstrip()  # Remove trailing whitespace
            # Check if the line is a test case
            test_match = test_case_pattern.match(line)
            if test_match:
                status_symbol, test_name = test_match.groups()
                test_name = test_name.strip()
                # Combine describe blocks and test name for full test identifier
                full_test_name = " ".join(current_describes + [test_name])
                # Categorize based on status symbol
                if status_symbol == "✓":
                    passed_tests.add(full_test_name)
                elif status_symbol == "✕":
                    failed_tests.add(full_test_name)
                elif status_symbol == "○":
                    skipped_tests.add(full_test_name)
                continue
            # Check if the line is a describe block (update current_describes)
            describe_match = describe_block_pattern.match(line)
            if describe_match:
                describe_text = describe_match.group(1).strip()
                # Determine indentation level (assuming 2 spaces per level)
                indent_level = len(line) - len(line.lstrip(" "))
                level = indent_level // 2
                # Update the current_describes list to reflect nested structure
                current_describes = current_describes[: level - 1] + [describe_text]
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
