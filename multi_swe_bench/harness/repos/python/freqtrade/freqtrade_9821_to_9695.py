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
        return "python:3.10-slim-bullseye"

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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y build-essential wget
###ACTION_DELIMITER###
wget https://downloads.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz && tar -xzf ta-lib-0.4.0-src.tar.gz && cd ta-lib && ./configure --prefix=/usr && make && make install && ldconfig
###ACTION_DELIMITER###
cd ..
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
pip install TA-Lib --global-option=build_ext --global-option="-L/usr/lib" --global-option="-I/usr/include"
###ACTION_DELIMITER###
apt-get install -y cmake
###ACTION_DELIMITER###
pip install TA-Lib --global-option=build_ext --global-option="-L/usr/lib" --global-option="-I/usr/include"
###ACTION_DELIMITER###
apt-get install -y ninja-build
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
CFLAGS="-Wno-incompatible-pointer-types" pip install TA-Lib --global-option=build_ext --global-option="-L/usr/lib" --global-option="-I/usr/include"
###ACTION_DELIMITER###
apt-get install -y autoconf automake libtool
###ACTION_DELIMITER###
apt-get install -y patchelf
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
export CFLAGS="-Wno-incompatible-pointer-types" && pip install TA-Lib==0.4.28
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install numpy==1.21.6 && export CFLAGS="-Wno-incompatible-pointer-types" && pip install TA-Lib==0.4.28
###ACTION_DELIMITER###
export CFLAGS="-Wno-incompatible-pointer-types" && pip install TA-Lib==0.4.19
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
export CFLAGS="-I/usr/include -L/usr/lib -Wno-incompatible-pointer-types -DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION" && pip install TA-Lib==0.4.28
###ACTION_DELIMITER###
sed -i 's/TA-Lib==0.4.28/TA-Lib==0.4.19/' requirements.txt && pip install -r requirements.txt
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider ./tests' > /home/freqtrade/test_commands.sh
###ACTION_DELIMITER###
bash /home/freqtrade/test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v --no-header -rA --tb=no -p no:cacheprovider ./tests

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider ./tests

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider ./tests

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
FROM python:3.10-slim-bullseye

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
RUN git clone https://github.com/freqtrade/freqtrade.git /home/freqtrade

WORKDIR /home/freqtrade
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("freqtrade", "freqtrade_9821_to_9695")
class FREQTRADE_9821_TO_9695(Instance):
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

        # Implement the log parsing logic here
        lines = log.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Check for PASSED tests
            if "PASSED" in line:
                # Match test name before PASSED (e.g., 'test_name PASSED [0%]')
                match = re.match(r"^(.*?)\s+PASSED\s+\[.*\]$", line)
                if match:
                    test_name = match.group(1).strip()
                    passed_tests.add(test_name)
                else:
                    # Match PASSED before test name (e.g., 'PASSED test_name')
                    match = re.match(r"^PASSED\s+(.*?)$", line)
                    if match:
                        test_name = match.group(1).strip()
                        passed_tests.add(test_name)
            # Check for FAILED tests
            elif "FAILED" in line:
                # Match test name before FAILED (e.g., 'test_name FAILED [0%]')
                match = re.match(r"^(.*?)\s+FAILED\s+\[.*\]$", line)
                if match:
                    test_name = match.group(1).strip()
                    failed_tests.add(test_name)
                else:
                    # Match FAILED before test name (e.g., 'FAILED test_name - error')
                    match = re.match(r"^FAILED\s+(.*?)(\s+-.*)?$", line)
                    if match:
                        test_name = match.group(1).strip()
                        failed_tests.add(test_name)
            # Check for SKIPPED tests
            elif "SKIPPED" in line:
                # Match test name before SKIPPED (e.g., 'test_name SKIPPED [1]')
                match = re.match(r"^(.*?)\s+SKIPPED\s+\[.*\]$", line)
                if match:
                    test_name = match.group(1).strip()
                    skipped_tests.add(test_name)
                else:
                    # Match SKIPPED before test name (e.g., 'SKIPPED [1] test_name:251: ...')
                    match = re.match(r"^SKIPPED\s+\[\d+\]\s+(.*?)(:\d+:\s.*)?$", line)
                    if match:
                        test_name = match.group(1).strip()
                        skipped_tests.add(test_name)
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
