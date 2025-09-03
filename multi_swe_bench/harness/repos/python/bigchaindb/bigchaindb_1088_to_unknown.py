import re

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
                """pip install -e .[dev]
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip install -e .[dev]
###ACTION_DELIMITER###
pip install line-profiler>=4.0.3
###ACTION_DELIMITER###
pip install -e .[dev]
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip uninstall -y pysha3 && pip install pysha3==1.0.2
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install cryptoconditions>=0.5.0
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install python-rapidjson>=0.0.8
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip uninstall -y cryptoconditions && pip install cryptoconditions==0.6.0
###ACTION_DELIMITER###
pip install cryptoconditions==0.7.3
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip uninstall -y cryptoconditions && pip install cryptoconditions==0.5.1
###ACTION_DELIMITER###
pip install PyNaCl==1.2.1 && pip install cryptoconditions==0.7.3
###ACTION_DELIMITER###
pip uninstall -y cryptoconditions && pip install cryptoconditions==0.6.0.dev1
###ACTION_DELIMITER###
apt-get update && apt-get install -y libsodium-dev && pip install cryptoconditions==0.5.0
###ACTION_DELIMITER###
pip install PyNaCl==1.4.0 && pip install cryptoconditions==0.8.1
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip uninstall -y cryptoconditions && pip install cryptoconditions==0.5.0
###ACTION_DELIMITER###
pip install cryptoconditions==0.5.0
###ACTION_DELIMITER###
pip install cryptoconditions==0.5.0 --no-deps
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install jsonschema~=2.5.1
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install rethinkdb~=2.3
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install rethinkdb==2.3.0
###ACTION_DELIMITER###
apt-get update && apt-get install -y rethinkdb && service rethinkdb start
###ACTION_DELIMITER###
wget -qO- https://download.rethinkdb.com/repository/raw/pubkey.gpg | apt-key add - && echo 'deb https://download.rethinkdb.com/repository/debian-bookworm bookworm main' > /etc/apt/sources.list.d/rethinkdb.list && apt-get update && apt-get install -y rethinkdb && service rethinkdb start
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget && wget -qO- https://download.rethinkdb.com/repository/raw/pubkey.gpg | gpg --dearmor -o /etc/apt/trusted.gpg.d/rethinkdb.gpg && echo 'deb https://download.rethinkdb.com/repository/debian-bookworm bookworm main' > /etc/apt/sources.list.d/rethinkdb.list && apt-get update && apt-get install -y rethinkdb && service rethinkdb start
###ACTION_DELIMITER###
rethinkdb --daemon
###ACTION_DELIMITER###

###ACTION_DELIMITER###
ps aux | grep rethinkdb
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install pymongo~=3.4
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider' > /home/bigchaindb/test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -n auto --no-header -rA --tb=no -p no:cacheprovider' > /home/bigchaindb/test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
pip install pytest-xdist
###ACTION_DELIMITER###
chmod +x /home/bigchaindb/test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v -n auto --no-header -rA --tb=no -p no:cacheprovider

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
pytest -v -n auto --no-header -rA --tb=no -p no:cacheprovider

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
pytest -v -n auto --no-header -rA --tb=no -p no:cacheprovider

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
RUN git clone https://github.com/bigchaindb/bigchaindb.git /home/bigchaindb

WORKDIR /home/bigchaindb
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("bigchaindb", "bigchaindb_1088_to_unknown")
class BIGCHAINDB_1088_TO_UNKNOWN(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        # Pattern to match test results (PASSED/FAILED/ERROR/SKIPPED)
        pattern = r'(PASSED|FAILED|ERROR|SKIPPED) (tests/.*?::.*?)( |$)'
        for line in log.split('\n'):
            match = re.search(pattern, line)
            if match:
                status = match.group(1)
                test_name = match.group(2)
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status in ['FAILED', 'ERROR']:
                    failed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
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
