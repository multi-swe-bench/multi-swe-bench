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
                """ls
###ACTION_DELIMITER###
python get-poetry.py
###ACTION_DELIMITER###
pip install poetry
###ACTION_DELIMITER###
poetry install
###ACTION_DELIMITER###
pip list | grep cleo
###ACTION_DELIMITER###
pip install 'cleo<2.0.0'
###ACTION_DELIMITER###
pip uninstall -y poetry && pip install poetry==1.1.0
###ACTION_DELIMITER###
poetry install
###ACTION_DELIMITER###
python -m poetry install
###ACTION_DELIMITER###
pip install cleo==1.0.0a4
###ACTION_DELIMITER###
pip uninstall -y poetry && pip install poetry==1.2.0a0
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
poetry run pytest tests/ -v
###ACTION_DELIMITER###
pip install --force-reinstall poetry-core==1.9.1
###ACTION_DELIMITER###
pip install --no-cache-dir --force-reinstall poetry-core==1.0.0
###ACTION_DELIMITER###
pip install --force-reinstall poetry-core==1.4.0
###ACTION_DELIMITER###
pip install -e . && poetry run pytest tests/ -v
###ACTION_DELIMITER###
pip install --force-reinstall poetry-core==1.0.0
###ACTION_DELIMITER###
pip install --force-reinstall poetry-core==1.0.0
###ACTION_DELIMITER###
pip install --force-reinstall poetry-core==1.4.0
###ACTION_DELIMITER###
pip uninstall -y poetry poetry-core cleo && pip install -e . && poetry run pytest tests/ -v
###ACTION_DELIMITER###
pip install --force-reinstall --no-cache-dir poetry-core==1.0.0 && poetry install && poetry run pytest tests/ -v
###ACTION_DELIMITER###
poetry run pip install --upgrade setuptools
###ACTION_DELIMITER###
rm -rf /root/.cache/pypoetry/virtualenvs/poetry-* && poetry install && poetry run pytest tests/ -v
###ACTION_DELIMITER###
poetry run pip install --upgrade virtualenv && poetry run pytest tests/ -v
###ACTION_DELIMITER###
poetry run pip install --upgrade setuptools && poetry run pytest tests/ -v
###ACTION_DELIMITER###
poetry run pip install setuptools==57.5.0 && poetry run pytest tests/ -v
###ACTION_DELIMITER###
echo 'poetry run pytest tests/ -v' > /home/poetry/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
poetry run pytest tests/ -v

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
poetry run pytest tests/ -v

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
poetry run pytest tests/ -v

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
RUN git clone https://github.com/python-poetry/poetry.git /home/poetry

WORKDIR /home/poetry
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("python-poetry", "poetry_3660_to_1935")
class POETRY_3660_TO_1935(Instance):
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
        # Extract passed tests from execution lines (e.g., "tests/...::test_name PASSED")
        passed_pattern = re.compile(r"^(tests/[\w/-]+\.py::[\w\[\]_\-.,]+)\s+PASSED", re.MULTILINE)
        passed_matches = passed_pattern.findall(log)
        passed_tests.update(passed_matches)
        # Extract failed tests from summary (e.g., "FAILED tests/...::test_name")
        failed_pattern = re.compile(r"^FAILED\s+(tests/[\w/-]+\.py::[\w\[\]_\-.,]+)", re.MULTILINE)
        failed_matches = failed_pattern.findall(log)
        failed_tests.update(failed_matches)
        # Extract skipped tests from execution lines (e.g., "tests/...::test_name SKIPPED")
        skipped_pattern = re.compile(r"^(tests/[\w/-]+\.py::[\w\[\]_\-.,]+)\s+SKIPPED", re.MULTILINE)
        skipped_matches = skipped_pattern.findall(log)
        skipped_tests.update(skipped_matches)
        # Extract skipped tests from summary (e.g., "SKIPPED tests/...::test_name")
        skipped_summary_pattern = re.compile(r"^SKIPPED\s+(tests/[\w/-]+\.py::[\w\[\]_\-.,]+)", re.MULTILINE)
        skipped_summary_matches = skipped_summary_pattern.findall(log)
        skipped_tests.update(skipped_summary_matches)
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
