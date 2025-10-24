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
npm install
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2 python2.7 make g++
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 make g++
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
ln -s /usr/bin/python3 /usr/bin/python && npm install
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && source ~/.nvm/nvm.sh && nvm install 14 && nvm use 14
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian buster main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python2.7 && ln -sf /usr/bin/python2.7 /usr/bin/python
###ACTION_DELIMITER###
echo 'deb [trusted=yes] http://deb.debian.org/debian buster main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python2.7 && ln -sf /usr/bin/python2.7 /usr/bin/python
###ACTION_DELIMITER###
sed -i '/buster/d' /etc/apt/sources.list && echo 'deb [trusted=yes] http://deb.debian.org/debian buster main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python2.7 && ln -sf /usr/bin/python2.7 /usr/bin/python
###ACTION_DELIMITER###
sed -i '/buster/d' /etc/apt/sources.list && echo 'deb http://deb.debian.org/debian-oldstable buster main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python2.7 && ln -sf /usr/bin/python2.7 /usr/bin/python
###ACTION_DELIMITER###
sed -i '/buster/d' /etc/apt/sources.list && echo 'deb [trusted=yes] http://archive.debian.org/debian buster main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python2.7 && ln -sf /usr/bin/python2.7 /usr/bin/python
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
echo 'npm test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo 'npm test -- --watchAll=false --verbose' > test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npm test -- --watchAll=false --verbose

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
npm test -- --watchAll=false --verbose

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
npm test -- --watchAll=false --verbose

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
RUN git clone https://github.com/SwissDataScienceCenter/renku-ui.git /home/renku-ui

WORKDIR /home/renku-ui
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("SwissDataScienceCenter", "renku_ui_893_to_327")
class RENKU_UI_893_TO_327(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re

        # Pattern for passed tests: matches lines starting with whitespace, ✓, test name, optional (ms)
        pattern_passed = re.compile(r"^\s*✓\s*(.*?)\s*(\(\d+ms\))?\s*$", re.MULTILINE)
        passed_matches = pattern_passed.findall(log)
        for match in passed_matches:
            test_name = match[0].strip()
            if test_name:
                passed_tests.add(test_name)
        # Pattern for failed tests: matches lines starting with whitespace, ✕, test name, optional (ms)
        pattern_failed = re.compile(r"^\s*✕\s*(.*?)\s*(\(\d+ms\))?\s*$", re.MULTILINE)
        failed_matches = pattern_failed.findall(log)
        for match in failed_matches:
            test_name = match[0].strip()
            if test_name:
                failed_tests.add(test_name)
        # Skipped tests: no pattern found in sampled logs, so leave as empty set
        # If skipped tests are present, add pattern here
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
