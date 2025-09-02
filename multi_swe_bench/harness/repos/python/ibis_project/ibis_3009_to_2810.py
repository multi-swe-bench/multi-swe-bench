from __future__ import annotations

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
conda env list
###ACTION_DELIMITER###
ls -la /root/miniconda
###ACTION_DELIMITER###
ls -la
###ACTION_DELIMITER###
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
###ACTION_DELIMITER###
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda
###ACTION_DELIMITER###
source /root/miniconda/etc/profile.d/conda.sh
###ACTION_DELIMITER###
conda env create -f environment.yml
###ACTION_DELIMITER###
conda install -n base -c conda-forge mamba --yes
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main --channel https://repo.anaconda.com/pkgs/r --yes
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main --channel https://repo.anaconda.com/pkgs/r
###ACTION_DELIMITER###
conda install -n base -c conda-forge mamba --yes
###ACTION_DELIMITER###
mamba env create -f environment.yml
###ACTION_DELIMITER###
mamba env update -n base -f environment.yml --yes
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
pip install sqlalchemy
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
echo 'pytest -v ibis/tests' > /home/ibis/test_commands.sh
###ACTION_DELIMITER###
cat /home/ibis/test_commands.sh
###ACTION_DELIMITER###
bash /home/ibis/test_commands.sh
###ACTION_DELIMITER###
pip install ibis-sqlite
###ACTION_DELIMITER###
python -c 'import sqlite3; print("SQLite3 available")'
###ACTION_DELIMITER###
pip install 'sqlalchemy<2.0'
###ACTION_DELIMITER###
bash /home/ibis/test_commands.sh
###ACTION_DELIMITER###
pip install ibis-pandas ibis-sqlalchemy
###ACTION_DELIMITER###
pip install 'ibis[pandas,sqlalchemy]'
###ACTION_DELIMITER###
pip install .
###ACTION_DELIMITER###
echo -e 'python -c "import ibis.backends.sqlite; import ibis.backends.pandas" && pytest -v ibis/tests' > /home/ibis/test_commands.sh
###ACTION_DELIMITER###
bash /home/ibis/test_commands.sh
###ACTION_DELIMITER###
pytest -v ibis/tests/test_api.py::test_multiple_backends
###ACTION_DELIMITER###
pip install pytest-mock
###ACTION_DELIMITER###
pytest -v ibis/tests/test_api.py::test_multiple_backends
###ACTION_DELIMITER###
bash /home/ibis/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python -c "import ibis.backends.sqlite; import ibis.backends.pandas" && pytest -v ibis/tests

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
python -c "import ibis.backends.sqlite; import ibis.backends.pandas" && pytest -v ibis/tests

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
python -c "import ibis.backends.sqlite; import ibis.backends.pandas" && pytest -v ibis/tests

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
RUN git clone https://github.com/ibis-project/ibis.git /home/ibis

WORKDIR /home/ibis
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ibis-project", "ibis_3009_to_2810")
class IBIS_3009_TO_2810(Instance):
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
        # Implement the log parsing logic here
        # Regex patterns to match test execution lines and summary lines
        # Execution lines: e.g., [   9] ibis/tests/expr/test_analysis.py::test_rewrite_join_projection_without_other_ops PASSED [  0%]
        pattern_execution = r'^\s*(?:\[\s*\d+\s*\]\s*)?([\w\/\-\.]+\.py::[^\s]+)\s+(PASSED|FAILED|SKIPPED|XFAIL|XPASSED)\s+(?:\[\s*\d+\.?\d*%?\s*\])?'
        # Summary lines: e.g., FAILED ibis/tests/test_api.py::test_top_level_api - AssertionError...
        pattern_summary = r'^\s*(?:\[\s*\d+\s*\]\s*)?(FAILED|SKIPPED|XFAIL|XPASSED)\s+([\w\/\-\.]+\.py::[^\s]+)'  # Use multiline flag
        matches_execution = re.findall(pattern_execution, log, re.MULTILINE)
        matches_summary = re.findall(pattern_summary, log, re.MULTILINE)
        matches = matches_execution + [(test, status) for status, test in matches_summary]
        for test_name, status in matches:
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
            elif status == 'XFAIL':
                # XFAIL is expected failure, consider as skipped
                skipped_tests.add(test_name)
            elif status == 'XPASSED':
                # XPASSED is unexpected pass, consider as failed
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
