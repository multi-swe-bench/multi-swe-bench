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
npm install
###ACTION_DELIMITER###
apt-get update && apt-get install -y chromium
###ACTION_DELIMITER###
npm test -- --browsers ChromeHeadless --single-run
###ACTION_DELIMITER###
CHROME_BIN=/usr/bin/chromium npm test -- --browsers ChromeHeadless --single-run
###ACTION_DELIMITER###
CHROME_BIN=/usr/bin/chromium CHROME_FLAGS=--no-sandbox npm test -- --browsers ChromeHeadless --single-run
###ACTION_DELIMITER###
CHROME_BIN=/usr/bin/chromium CHROME_FLAGS='--no-sandbox' npm test -- --browsers ChromeHeadless --single-run
###ACTION_DELIMITER###
CHROME_BIN=/usr/bin/chromium npm test -- --browsers ChromeHeadless --single-run --chromeFlags=--no-sandbox
###ACTION_DELIMITER###
sed -i '/config.set({/a \  customLaunchers: {\n    ChromeHeadlessCustom: {\n      base: "ChromeHeadless",\n      flags: ["--no-sandbox"]\n    }\n  },\n  browsers: ["ChromeHeadlessCustom"],' karma.conf.js
###ACTION_DELIMITER###
CHROME_BIN=/usr/bin/chromium npm test -- --single-run
###ACTION_DELIMITER###
echo 'CHROME_BIN=/usr/bin/chromium npm test -- --single-run' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
CHROME_BIN=/usr/bin/chromium npm test -- --single-run

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
CHROME_BIN=/usr/bin/chromium npm test -- --single-run

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
CHROME_BIN=/usr/bin/chromium npm test -- --single-run

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
RUN git clone https://github.com/IgniteUI/ignite-ui.git /home/ignite-ui

WORKDIR /home/ignite-ui
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("IgniteUI", "ignite_ui_2144_to_2117")
class IGNITE_UI_2144_TO_2117(Instance):
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
        # Extract passed tests
        passed_pattern = re.compile(r'.*?\x1b\[32m✓ \x1b\[39m\s*(.*?)\s+\(\d+ms\)')
        passed_tests.update(passed_pattern.findall(log))
        # Extract failed tests
        failed_pattern = re.compile(r'.*?\x1b\[31m\d+\)\s+(.*?)(?=\n|$)', re.DOTALL)
        failed_tests.update(failed_pattern.findall(log))
        # Extract skipped tests
        skipped_pattern = re.compile(r'\x1b\[33m⚠\x1b\[39m\s+(.*?)\s+\(\d+ms\)')
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
