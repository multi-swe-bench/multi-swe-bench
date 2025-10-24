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
                """ls -la
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
npm run test -- --verbose
###ACTION_DELIMITER###

###ACTION_DELIMITER###
npm list jsdom
###ACTION_DELIMITER###
npm install jsdom@16.7.0 --save-dev
###ACTION_DELIMITER###
npm install jsdom@16.7.0 --save-dev --legacy-peer-deps
###ACTION_DELIMITER###
npm run test -- --verbose
###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i '/window.TransitionEvent/a window.TextEncoder = require("util").TextEncoder;\nwindow.TextDecoder = require("util").TextDecoder;' tests/setup.js
###ACTION_DELIMITER###
npm run test -- --verbose
###ACTION_DELIMITER###

###ACTION_DELIMITER###
npm install web-streams-polyfill --save-dev --legacy-peer-deps
###ACTION_DELIMITER###
sed -i '/window.TransitionEvent/a const { ReadableStream } = require("web-streams-polyfill");\nwindow.ReadableStream = ReadableStream;' tests/setup.js
###ACTION_DELIMITER###
npm run test -- --verbose
###ACTION_DELIMITER###
sed -i '/window.ReadableStream/a const { MessagePort } = require("worker_threads");\nwindow.MessagePort = MessagePort;' tests/setup.js
###ACTION_DELIMITER###
npm run test -- --verbose
###ACTION_DELIMITER###
npm install cheerio@1.0.0-rc.3 --save-dev --legacy-peer-deps
###ACTION_DELIMITER###
npm run test -- --verbose
###ACTION_DELIMITER###
echo 'npm run test -- --verbose' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npm run test -- --verbose

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
npm run test -- --verbose

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
npm run test -- --verbose

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

# Choose an appropriate base image based on the project's requirements - replace node:18-bullseye with actual base image
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
RUN git clone https://github.com/ant-design/ant-design.git /home/ant-design

WORKDIR /home/ant-design
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ant-design", "ant_design_31042_to_30655")
class ANT_DESIGN_31042_TO_30655(Instance):
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
        # Parse test results from summary and individual lines
        # Match test suite results (e.g., 'PASS components/form/__tests__/type.test.tsx')
        pass_pattern = re.compile(r'(?:\[\s*\d+\s*\]\s+)?PASS(?:ED)?:?\s+([\w\/\-\.]+\.(?:test|spec)\.(?:js|ts|tsx|jsx))', re.IGNORECASE)  # Use non-capturing groups for test type and extension  # Target test file paths  # Use \S+ for flexible test name capture  # Optional line number prefix  # Match line number prefix  # Simplified to match any PASS line  # Allow extra text between line number and PASS
        fail_pattern = re.compile(r'(?:\[\s*\d+\s*\]\s+)?FAIL(?:ED)?:?\s+([\w\/\-\.]+\.(?:test|spec)\.(?:js|ts|tsx|jsx))', re.IGNORECASE)  # Target test file paths  # Use \S+ for flexible test name capture  # Optional line number prefix  # Match line number prefix  # Simplified to match any FAIL line  # Case-insensitive match
        # Extract passed tests
        passed_tests.update(pass_pattern.findall(log))
        # Extract failed tests
        failed_tests.update(fail_pattern.findall(log))
        # Extract skipped tests from individual lines (e.g., 'SKIPPED components/test/test.tsx')
        skip_pattern = re.compile(r'(?:\[\s*\d+\s*\]\s+)?(?:SKIP|SKIPPED):?\s+([\w\/\-\.]+\.(?:test|spec)\.(?:js|ts|tsx|jsx))', re.IGNORECASE)  # Match test file paths  # Include slashes for file paths  # Flexible capture for skipped test names  # Target test file paths for skipped tests  # Flexible capture for skipped test names  # Handle SKIP or SKIPPED  # Target test file paths  # Optional line number prefix and flexible capture  # Simplified to match any SKIPPED line  # Allow optional colon after SKIPPED
        skipped_tests.update(skip_pattern.findall(log))
        # Extract skipped tests from summary if individual lines are not available
        skip_summary = re.search(r'Tests:\s+\d+ failed,\s+(\d+) skipped', log)
        if skip_summary and not skipped_tests:
            # If no individual skipped tests are found, log a warning (task requires names, so this is a fallback)
            import warnings
            warnings.warn(f"Skipped tests count: {skip_summary.group(1)}, but no test names were found in the log.")
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
