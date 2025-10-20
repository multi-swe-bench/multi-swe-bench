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
        return "node:20.12.2"
    
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
                """ls
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
npm install -g yarn@^1.22.22
###ACTION_DELIMITER###
npm install -g yarn@^1.22.22 --force
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo -e '#!/bin/bash

# Run unit tests with verbose output
yarn test:unit --verbose

# Run iOS E2E tests with verbose output
yarn test:e2e:ios:debug:run --verbose

# Run Android E2E tests with verbose output
yarn test:e2e:android:debug:run --verbose' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
yarn setup:e2e
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e

# Start Metro server in background
yarn watch:clean &
METRO_PID=$!

# Run unit tests with verbose output
yarn test:unit --verbose

# Run iOS E2E tests with verbose output
yarn test:e2e:ios:debug:run --verbose

# Run Android E2E tests with verbose output
yarn test:e2e:android:debug:run --verbose

# Stop Metro server
kill $METRO_PID' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e

# Start Metro server in background
yarn watch:clean &
METRO_PID=$!

# Run unit tests with verbose output
yarn test:unit --verbose

# Build iOS E2E app
yarn test:e2e:ios:debug:build

# Run iOS E2E tests with verbose output
yarn test:e2e:ios:debug:run --verbose

# Build Android E2E app
yarn test:e2e:android:debug:build

# Run Android E2E tests with verbose output
yarn test:e2e:android:debug:run --verbose

# Stop Metro server
kill $METRO_PID' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e

# Start Metro server in background
yarn watch:clean &
METRO_PID=$!

# Run unit tests with verbose output
yarn test:unit --verbose

# Build iOS E2E app
yarn test:e2e:ios:debug:build

# Run iOS E2E tests with verbose output
yarn test:e2e:ios:debug:run --verbose

# Build Android E2E app
yarn test:e2e:android:debug:build

# Run Android E2E tests with verbose output
yarn test:e2e:android:debug:run --verbose

# Stop Metro server
kill $METRO_PID

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
#!/bin/bash
set -e

# Start Metro server in background
yarn watch:clean &
METRO_PID=$!

# Run unit tests with verbose output
yarn test:unit --verbose

# Build iOS E2E app
yarn test:e2e:ios:debug:build

# Run iOS E2E tests with verbose output
yarn test:e2e:ios:debug:run --verbose

# Build Android E2E app
yarn test:e2e:android:debug:build

# Run Android E2E tests with verbose output
yarn test:e2e:android:debug:run --verbose

# Stop Metro server
kill $METRO_PID

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
#!/bin/bash
set -e

# Start Metro server in background
yarn watch:clean &
METRO_PID=$!

# Run unit tests with verbose output
yarn test:unit --verbose

# Build iOS E2E app
yarn test:e2e:ios:debug:build

# Run iOS E2E tests with verbose output
yarn test:e2e:ios:debug:run --verbose

# Build Android E2E app
yarn test:e2e:android:debug:build

# Run Android E2E tests with verbose output
yarn test:e2e:android:debug:run --verbose

# Stop Metro server
kill $METRO_PID

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
FROM node:20.12.2

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
RUN git clone https://github.com/MetaMask/metamask-mobile.git /home/metamask-mobile

WORKDIR /home/metamask-mobile
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("MetaMask", "metamask_mobile_11262_to_9409")
class METAMASK_MOBILE_11262_TO_9409(Instance):
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
        # Parse passed test suites and individual tests (optional line number prefix and indentation)
        # Capture passed test suites (e.g., 'PASS app/components/UI/Stake/utils/value/value.test.ts')
        suite_passed_pattern = re.compile(r'^(?:\[\s*\d+\]\s*)?PASS\s+(.*?)\s*$', re.MULTILINE)
        passed_tests.update(suite_passed_pattern.findall(log))
        # Capture individual passed tests (e.g., '    ✓ handles different input formats...')
        test_passed_pattern = re.compile(r'^(?:\[\s*\d+\]\s*)?\s*✓\s+(.*?)(?:\s+\(\d+ ms\))?$', re.MULTILINE)
        passed_tests.update(test_passed_pattern.findall(log))
        # Parse failed test suites and individual tests using regex (optional line number prefix)
        # Capture failed test suites (e.g., 'FAIL app/reducers/fiatOrders/index.test.ts' or '[  123] FAIL ...')
        suite_failed_pattern = re.compile(r'^(?:\[\s*\d+\]\s*)?FAIL\s+([^\s]+)\s*', re.MULTILINE)
        failed_tests.update(suite_failed_pattern.findall(log))
        # Capture individual failed tests (e.g., '✕ should only get owned collectibles' or '[  123]     ✕ ...')
        test_failed_pattern = re.compile(r'^(?:\[\s*\d+\]\s*)?✕\s+([^\(]+?)\s*(?:\(\d+ ms\))?$', re.MULTILINE)
        failed_tests.update(test_failed_pattern.findall(log))
        # Parse skipped tests (optional line number prefix; adjust keyword if needed)
        skipped_pattern = re.compile(r'^(?:\[\s*\d+\]\s*)?SKIPPED\s+(.*?)\s+\(\d+ ms\)$', re.MULTILINE)
        skipped_tests.update(skipped_pattern.findall(log))
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
