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
        return "python:3.11-slim"
    
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
                """ls /home/randovania
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.12 python3.12-dev -t bookworm-backports
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bookworm-backports main' > /etc/apt/sources.list.d/bookworm-backports.list
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.12 python3.12-dev -t bookworm-backports
###ACTION_DELIMITER###
apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget liblzma-dev
###ACTION_DELIMITER###
apt-cache search python3.12 -t bookworm-backports
###ACTION_DELIMITER###
wget https://www.python.org/ftp/python/3.12.7/Python-3.12.7.tgz
###ACTION_DELIMITER###
tar -xzf Python-3.12.7.tgz
###ACTION_DELIMITER###
cd Python-3.12.7 && ./configure --enable-optimizations
###ACTION_DELIMITER###
make -j 4
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
cd /home/randovania
###ACTION_DELIMITER###
pip3.12 install -r requirements.txt
###ACTION_DELIMITER###
pip3.12 install -e .
###ACTION_DELIMITER###
echo 'python3.12 -m pytest -v -rA --tb=short --no-header -p no:cacheprovider test/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libsqlite3-dev
###ACTION_DELIMITER###
cd Python-3.12.7 && make clean && ./configure --enable-optimizations && make -j 4 && make install
###ACTION_DELIMITER###
python3.12 -c 'import sqlite3; print("sqlite3 module imported successfully")'
###ACTION_DELIMITER###
cd /home/randovania && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libglib2.0-0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libgl1-mesa-glx
###ACTION_DELIMITER###
apt-get install -y libegl1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libxkbcommon0
###ACTION_DELIMITER###
ldconfig
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libdbus-1-3
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
python3.12 setup.py build_ui
###ACTION_DELIMITER###
pip3.12 install setuptools
###ACTION_DELIMITER###
python3.12 setup.py build_ui
###ACTION_DELIMITER###
pip3.12 install pyside6-tools && python3.12 setup.py build_ui
###ACTION_DELIMITER###
pip3.12 install pyqt-distutils && python3.12 setup.py build_ui
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y xvfb && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
echo 'QT_QPA_PLATFORM=offscreen xvfb-run -a python3.12 -m pytest -v -rA --tb=short --no-header -p no:cacheprovider test/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libbz2-dev && cd Python-3.12.7 && make clean && ./configure --enable-optimizations && make -j 4 && make install && cd /home/randovania && bash test_commands.sh
###ACTION_DELIMITER###
wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && dpkg -i packages-microsoft-prod.deb && apt-get update && apt-get install -y dotnet-runtime-6.0 && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
QT_QPA_PLATFORM=offscreen xvfb-run -a python3.12 -m pytest -v -rA --tb=short --no-header -p no:cacheprovider test/

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
QT_QPA_PLATFORM=offscreen xvfb-run -a python3.12 -m pytest -v -rA --tb=short --no-header -p no:cacheprovider test/

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
QT_QPA_PLATFORM=offscreen xvfb-run -a python3.12 -m pytest -v -rA --tb=short --no-header -p no:cacheprovider test/

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
FROM python:3.11-slim

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
RUN git clone https://github.com/randovania/randovania.git /home/randovania

WORKDIR /home/randovania
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("randovania", "randovania_8037_to_6351")
class RANDOVANIA_8037_TO_6351(Instance):
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
        # Split log into lines
        lines = log.split('\n')
        # Regex patterns for each status
        passed_pattern = re.compile(r'(test/.*?) PASSED|PASSED (test/.*)')
        skipped_pattern = re.compile(r'SKIPPED \[\d+\] (test/.*?):')
        failed_pattern = re.compile(r'FAILED (test/.*?)(?: - |$)')
        for line in lines:
            # Check for PASSED tests
            passed_match = passed_pattern.search(line)
            if passed_match:
                test_name = passed_match.group(1) or passed_match.group(2)
                if test_name:
                    passed_tests.add(test_name.strip())
                continue
            # Check for SKIPPED tests
            skipped_match = skipped_pattern.search(line)
            if skipped_match:
                test_name = skipped_match.group(1).strip()
                skipped_tests.add(test_name)
                continue
            # Check for FAILED tests
            failed_match = failed_pattern.search(line)
            if failed_match:
                test_name = failed_match.group(1).strip()
                failed_tests.add(test_name)
                continue
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
