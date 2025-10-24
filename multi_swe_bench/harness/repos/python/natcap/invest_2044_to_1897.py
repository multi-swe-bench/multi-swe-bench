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
        return "python:3.10-slim"

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
apt-get update && apt-get install -y git-lfs
###ACTION_DELIMITER###
make fetch
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make fetch
###ACTION_DELIMITER###
pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgdal-dev
###ACTION_DELIMITER###
pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
pip install GDAL==3.6.2 && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y g++
###ACTION_DELIMITER###
pip install GDAL==3.6.2 && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip uninstall -y GDAL && pip install GDAL==3.6.2
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
pip uninstall -y GDAL && pip install GDAL==3.6.2 --no-binary :all:
###ACTION_DELIMITER###
pip uninstall -y GDAL && pip install numpy && pip install GDAL==3.6.2 --no-binary :all:
###ACTION_DELIMITER###
pip uninstall -y GDAL && pip install GDAL==3.6.2 --no-binary :all: -v
###ACTION_DELIMITER###
pip install --upgrade pip && pip uninstall -y GDAL && pip install numpy && pip install GDAL==3.6.2 --no-binary :all:
###ACTION_DELIMITER###
pip uninstall -y GDAL && pip install GDAL==3.6.2 --no-binary :all: --global-option=build_ext --global-option="-I$(python -c 'import numpy; print(numpy.get_include())')"
###ACTION_DELIMITER###
pip uninstall -y GDAL && pip cache purge && pip install GDAL==3.6.2 --no-binary :all: --global-option=build_ext --global-option="-I$(python -c 'import numpy; print(numpy.get_include())')"
###ACTION_DELIMITER###
pip uninstall -y GDAL && pip install GDAL==3.6.2 --no-binary :all: --global-option=build_ext --global-option="-I$(python -c 'import numpy; print(numpy.get_include())')" --global-option="-I/usr/include/gdal"
###ACTION_DELIMITER###
python -c 'from osgeo import gdal_array; print("Successfully imported gdal_array")'
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
echo 'make test' > /home/invest/test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
make test

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
make test

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
make test

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
FROM python:3.10-slim

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
RUN git clone https://github.com/natcap/invest.git /home/invest

WORKDIR /home/invest
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("natcap", "invest_2044_to_1897")
class INVEST_2044_TO_1897(Instance):
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

        # Regex pattern to match test cases with their status
        # Regex pattern to match test cases with line numbers and status in either order
        # Match lines with line numbers, test name, and status (either order)
        # Match test-first lines (test name followed by status) with flexible line start
        test_first_pattern = re.compile(
            r"^(tests/[^\s]+)\s+(PASSED|FAILED|SKIPPED)", re.MULTILINE
        )
        # Match status-first lines (status followed by test name) with flexible line start
        status_first_pattern = re.compile(
            r"^\[\s*\d+\s*\]\s+(PASSED|FAILED|SKIPPED)\s+(tests/[^\s]+)", re.MULTILINE
        )
        # Process test-first matches
        for test_name, status in test_first_pattern.findall(log):
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status == "FAILED":
                failed_tests.add(test_name)
            elif status == "SKIPPED":
                skipped_tests.add(test_name)
        # Process status-first matches
        for status, test_name in status_first_pattern.findall(log):
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status == "FAILED":
                failed_tests.add(test_name)
            elif status == "SKIPPED":
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
