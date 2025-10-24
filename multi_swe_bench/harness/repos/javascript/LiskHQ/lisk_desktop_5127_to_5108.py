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
        return "node:18"

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
                """yarn install
###ACTION_DELIMITER###
rm -rf node_modules yarn.lock && yarn install
###ACTION_DELIMITER###
sed -i 's/"**\/glob-parent": "5.1.2"/"**\/glob-parent": "5.1.2",/' package.json && sed -i '/"**\/glob-parent": "5.1.2",/a\    "**\/cheerio": "1.0.0-rc.12"' package.json
###ACTION_DELIMITER###
sed -i 's/"\*\*\/glob-parent": "5.1.2"/"\*\*\/glob-parent": "5.1.2",/' package.json && sed -i '/"\*\*\/glob-parent": "5.1.2",/a\    "\*\*\/cheerio": "1.0.0-rc.12"' package.json
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
apt-get update && apt-get install -y libusb-1.0-0-dev libudev-dev
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
 yarn test --verbose
 yarn cypress:run --verbose
 yarn cucumber:playwright:open --verbose' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
# Continue on errors to run all test suites
set +e
# Run Jest with JSON output for parseability
JEST_JUNIT_OUTPUT_NAME=jest-results.xml yarn test --verbose --reporters=default --reporters=jest-junit
# Run Cypress with verbose and JSON output
CYPRESS_RECORD_KEY=none yarn cypress:run --verbose --reporter json
# Run Playwright Cucumber with verbose output
yarn cucumber:playwright:open --verbose
# Exit with 0 to indicate script completion (test results are in logs)
exit 0' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set +e
# Run Jest with verbose and JUnit output
JEST_JUNIT_OUTPUT_NAME=jest-results.xml yarn test --verbose --reporters=default --reporters=jest-junit
# Run Cypress with JSON reporter for parseability
yarn cypress:run --reporter json
# Run Cucumber with pretty format for verbose logs
yarn cucumber:playwright:open --format pretty
exit 0' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set +e
# Run Jest with verbose and JUnit output
JEST_JUNIT_OUTPUT_NAME=jest-results.xml yarn test --verbose --reporters=default --reporters=jest-junit
# Run Cypress with JSON reporter for parseable output
yarn cypress:run --reporter json
# Run Cucumber with built-in progress formatter for verbose logs
yarn cucumber:playwright:open --format progress
exit 0' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set +e
# Start app server in background
yarn dev &
SERVER_PID=$!
# Wait for server to be ready (adjust port as needed)
while ! curl -s http://localhost:8080 > /dev/null; do sleep 2; done
# Run Jest tests
JEST_JUNIT_OUTPUT_NAME=jest-results.xml yarn test --verbose --reporters=default --reporters=jest-junit
# Run Cypress tests
CYPRESS_BASE_URL=http://localhost:8080 yarn cypress:run --reporter json
# Run Cucumber tests
CUCUMBER_BASE_URL=http://localhost:8080 yarn cucumber:playwright:open --format progress
# Stop server
kill $SERVER_PID
exit 0' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set +e
# Start app server in background
yarn dev &
SERVER_PID=$!
# Wait for server to be ready (adjust port as needed)
while ! curl -s http://localhost:8080 > /dev/null; do sleep 2; done
# Run Jest tests
JEST_JUNIT_OUTPUT_NAME=jest-results.xml yarn test --verbose --reporters=default --reporters=jest-junit
# Run Cypress tests
CYPRESS_BASE_URL=http://localhost:8080 yarn cypress:run --reporter json
# Run Cucumber tests
CUCUMBER_BASE_URL=http://localhost:8080 yarn cucumber:playwright:open --format progress
# Stop server
kill $SERVER_PID
exit 0

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
set +e
# Start app server in background
yarn dev &
SERVER_PID=$!
# Wait for server to be ready (adjust port as needed)
while ! curl -s http://localhost:8080 > /dev/null; do sleep 2; done
# Run Jest tests
JEST_JUNIT_OUTPUT_NAME=jest-results.xml yarn test --verbose --reporters=default --reporters=jest-junit
# Run Cypress tests
CYPRESS_BASE_URL=http://localhost:8080 yarn cypress:run --reporter json
# Run Cucumber tests
CUCUMBER_BASE_URL=http://localhost:8080 yarn cucumber:playwright:open --format progress
# Stop server
kill $SERVER_PID
exit 0

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
set +e
# Start app server in background
yarn dev &
SERVER_PID=$!
# Wait for server to be ready (adjust port as needed)
while ! curl -s http://localhost:8080 > /dev/null; do sleep 2; done
# Run Jest tests
JEST_JUNIT_OUTPUT_NAME=jest-results.xml yarn test --verbose --reporters=default --reporters=jest-junit
# Run Cypress tests
CYPRESS_BASE_URL=http://localhost:8080 yarn cypress:run --reporter json
# Run Cucumber tests
CUCUMBER_BASE_URL=http://localhost:8080 yarn cucumber:playwright:open --format progress
# Stop server
kill $SERVER_PID
exit 0

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

# Choose an appropriate base image based on the project's requirements - replace node:18 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:18

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
RUN git clone https://github.com/LiskHQ/lisk-desktop.git /home/lisk-desktop

WORKDIR /home/lisk-desktop
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("LiskHQ", "lisk_desktop_5127_to_5108")
class LISK_DESKTOP_5127_TO_5108(Instance):
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

        # Parse passed tests (✓ for Jest individual tests, exclude file paths)
        passed_pattern = re.compile(r"✓\s+([A-Z].+?)\s+\(\d+ ms\)")
        passed_tests.update(passed_pattern.findall(log))
        # Parse failed tests (✕ for Jest, failed scenarios for Cucumber, exclude file paths)
        failed_pattern = re.compile(
            r"(✕\s+([A-Z].+?)\s+\(\d+ ms\)|Scenario:\s+([A-Z].+?)\s+\(failed\))"
        )
        for match in failed_pattern.finditer(log):
            test_name = match.group(2) or match.group(3)
            if test_name:
                failed_tests.add(test_name.strip())
        # Parse skipped tests (○ for Jest, skipped scenarios for Cucumber)
        skipped_pattern = re.compile(
            r"(○\s+(.+?)\s+\(\d+ ms\)|Scenario:\s+(.+?)\s+\(skipped\))"
        )
        for match in skipped_pattern.finditer(log):
            test_name = match.group(2) or match.group(3)
            if test_name:
                skipped_tests.add(test_name.strip())
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
