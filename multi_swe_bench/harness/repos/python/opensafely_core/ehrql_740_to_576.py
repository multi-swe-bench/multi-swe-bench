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
        return "python:3.9-slim"

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
                """ls
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.9-dev gcc libssl-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential python3-dev libssl-dev
###ACTION_DELIMITER###
just devenv
###ACTION_DELIMITER###
wget https://github.com/casey/just/releases/download/1.42.4/just-1.42.4-x86_64-unknown-linux-musl.tar.gz && tar -xzf just-1.42.4-x86_64-unknown-linux-musl.tar.gz && chmod +x just && mv just /usr/local/bin/
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
wget https://github.com/casey/just/releases/download/1.42.4/just-1.42.4-x86_64-unknown-linux-musl.tar.gz && tar -xzf just-1.42.4-x86_64-unknown-linux-musl.tar.gz && chmod +x just && mv just /usr/local/bin/
###ACTION_DELIMITER###
just --version
###ACTION_DELIMITER###
just devenv
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
PYTHON_VERSION=python3 just devenv
###ACTION_DELIMITER###
PYTHON_VERSION=python3 just test-all -v -k 'not docker'
###ACTION_DELIMITER###
PYTHON_VERSION=python3 just test-all -v --ignore=tests/docker
###ACTION_DELIMITER###
PYTHON_VERSION=python3 just test-no-spark -v -k 'not mssql'
###ACTION_DELIMITER###
PYTHON_VERSION=python3 just test -v -k 'not spark and not mssql'
###ACTION_DELIMITER###
PYTHON_VERSION=python3 just test -v --ignore=tests/spark --ignore=tests/mssql
###ACTION_DELIMITER###
echo 'PYTHON_VERSION=python3 EHRQL_BACKEND=in_memory just test -v --ignore=tests/docker --ignore=tests/spark --ignore=tests/mssql' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'PYTHON_VERSION=python3 EHRQL_BACKEND=in_memory just test-unit -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
PYTHON_VERSION=python3 EHRQL_BACKEND=in_memory just test-unit -v

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
PYTHON_VERSION=python3 EHRQL_BACKEND=in_memory just test-unit -v

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
PYTHON_VERSION=python3 EHRQL_BACKEND=in_memory just test-unit -v

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.9-slim

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
RUN git clone https://github.com/opensafely-core/ehrql.git /home/ehrql

WORKDIR /home/ehrql
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("opensafely-core", "ehrql_740_to_576")
class EHRQL_740_TO_576(Instance):
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

        # Regex patterns to match test lines and summaries
        # Pattern 1: Individual test lines (e.g., [ 12] tests/... TEST_NAME STATUS ...)
        pattern_test_line = r"(tests/.*?)\s+(PASSED|FAILED|SKIPPED)"
        # Pattern 2: Failed test summaries (e.g., [ 439] FAILED tests/...)
        pattern_failed_summary = r"FAILED\s+(tests/.*?)"
        # Extract tests from individual lines (PASSED/FAILED/SKIPPED)
        test_matches = re.findall(pattern_test_line, log, re.MULTILINE)
        for test_name, status in test_matches:
            if status == "PASSED":
                passed_tests.add(test_name.strip())
            elif status == "FAILED":
                failed_tests.add(test_name.strip())
            elif status == "SKIPPED":
                skipped_tests.add(test_name.strip())
        # Extract failed tests from summary lines
        failed_summary_matches = re.findall(pattern_failed_summary, log, re.MULTILINE)
        for test_name in failed_summary_matches:
            failed_tests.add(test_name.strip())
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
