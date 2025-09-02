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
pip install -r requirements/devel.txt
###ACTION_DELIMITER###
pip install -r requirements/test.txt
###ACTION_DELIMITER###
pytest thunder/tests -v
###ACTION_DELIMITER###
pip install looseversion
###ACTION_DELIMITER###
pytest thunder/tests -v
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.10
###ACTION_DELIMITER###
python3.10 --version
###ACTION_DELIMITER###
apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
###ACTION_DELIMITER###
wget https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tgz && tar -xzf Python-3.10.12.tgz && cd Python-3.10.12 && ./configure --enable-optimizations && make -j $(nproc) && make altinstall
###ACTION_DELIMITER###
python3.10 --version
###ACTION_DELIMITER###
cd ..
###ACTION_DELIMITER###
pip3.10 install -e .
###ACTION_DELIMITER###
pip3.10 install -r requirements/test.txt
###ACTION_DELIMITER###
python3.10 -m pytest thunder/tests -v
###ACTION_DELIMITER###
apt-get install -y libsqlite3-dev
###ACTION_DELIMITER###
cd Python-3.10.12 && make && make altinstall
###ACTION_DELIMITER###
python3.10 -c 'import sqlite3; print("sqlite3 module loaded successfully")'
###ACTION_DELIMITER###
cd ..
###ACTION_DELIMITER###
python3.10 -m pytest thunder/tests -v
###ACTION_DELIMITER###
THUNDER_DRIVER=nvfuser python3.10 -m pytest thunder/tests -v
###ACTION_DELIMITER###
pip3.10 install --pre 'nvfuser-cu121[torch]' --extra-index-url https://pypi.nvidia.com
###ACTION_DELIMITER###
THUNDER_DRIVER=nvfuser python3.10 -c 'import thunder; print("Active drivers:", thunder.active_drivers())'
###ACTION_DELIMITER###
THUNDER_DRIVER=nvfuser python3.10 -c 'import torch; import thunder; def foo(a, b): return a + b; jfoo = thunder.jit(foo); print(jfoo(torch.tensor(1), torch.tensor(2)))'
###ACTION_DELIMITER###
echo -e 'import torch
import thunder
def foo(a, b):
    return a + b
jfoo = thunder.jit(foo)
print(jfoo(torch.tensor(1), torch.tensor(2)))' > test_driver.py && THUNDER_DRIVER=nvfuser python3.10 test_driver.py
###ACTION_DELIMITER###
echo 'THUNDER_DRIVER=nvfuser pytest thunder/tests -v' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
THUNDER_DRIVER=nvfuser pytest thunder/tests -v

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
THUNDER_DRIVER=nvfuser pytest thunder/tests -v

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn  /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
THUNDER_DRIVER=nvfuser pytest thunder/tests -v

""".format(
                    pr=self.pr
                ),
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
RUN git clone https://github.com/Lightning-AI/lightning-thunder.git /home/lightning-thunder

WORKDIR /home/lightning-thunder
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Lightning-AI", "lightning_thunder_802_to_577")
class LIGHTNING_THUNDER_802_TO_577(Instance):
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
        # Remove ANSI color codes (handles complex codes like \x1b[31m, \x1b[0m)
        log_clean = re.sub(r'\x1b\[[0-9;]*m', '', log)
        # Pattern to match test execution lines (timestamp + test name + status)
        exec_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] (.*?) (PASSED|FAILED|SKIPPED|XFAIL|XPASSED)'
        # Pattern to match summary lines (flexible capture)
        summary_pattern = r'\[\d+\]\s+.*?(FAILED|XFAIL)\s+(thunder/.*?)\s+-'
        # Extract from execution lines
        exec_matches = re.findall(exec_pattern, log_clean)
        # Extract from summary lines
        summary_matches = re.findall(summary_pattern, log_clean)
        for test_name, status in exec_matches:
            test_name = test_name.strip()
            status = status.strip()
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ['FAILED', 'XFAIL']:
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
            elif status == 'XPASSED':
                passed_tests.add(test_name)
        # Handle summary lines (e.g., failed tests not captured in execution lines)
        for status, test_name in summary_matches:
            test_name = test_name.strip()
            if status in ['FAILED', 'XFAIL']:
                failed_tests.add(test_name)
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
