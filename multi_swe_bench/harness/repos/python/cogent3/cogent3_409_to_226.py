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
        return "ubuntu:latest"
    
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
                """cat README.md
###ACTION_DELIMITER###
ls
###ACTION_DELIMITER###
python --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.8 python3-pip
###ACTION_DELIMITER###
pip3 install numpy
###ACTION_DELIMITER###
python3.8 -m venv venv
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.8 python3.8-venv
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.8 python3.8-venv
###ACTION_DELIMITER###
python3.8 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
sed -i 's/license=\["BSD"\]/license="BSD"/' setup.py
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
apt-get install -y python3.8-dev
###ACTION_DELIMITER###
pip install --upgrade pip setuptools && pip install -e .
###ACTION_DELIMITER###
echo 'pytest -v -rA tests/ --ignore=test_mpi.py' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
pytest -v -rA tests/ --ignore=test_mpi.py' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.21.6 && echo -e 'source venv/bin/activate
cd tests
pytest -v -rA --ignore=test_mpi.py' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.24.4 && pip install -e . && bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.23.5 && pip install -e . && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
source venv/bin/activate
cd tests
pytest -v -rA --ignore=test_mpi.py

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
source venv/bin/activate
cd tests
pytest -v -rA --ignore=test_mpi.py

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
source venv/bin/activate
cd tests
pytest -v -rA --ignore=test_mpi.py

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:latest with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:latest

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
RUN git clone https://github.com/cogent3/cogent3.git /home/cogent3

WORKDIR /home/cogent3
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("cogent3", "cogent3_409_to_226")
class COGENT3_409_TO_226(Instance):
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
        # Regex patterns for test statuses
        passed_pattern = re.compile(r'(?:PASSED\s+([\w\/]+\.py::[\w:]+)|([\w\/]+\.py::[\w:]+)\s+PASSED)')
        failed_pattern = re.compile(r'FAILED\s+([\w\/]+\.py::[\w:]+)')
        skipped_pattern = re.compile(r'SKIPPED\s+\[\d+\]\s+([\w\/]+\.py:\d+)')
        # Extract passed tests
        for match in passed_pattern.findall(log):
            test_name = match[0] if match[0] else match[1]
            passed_tests.add(test_name)
        # Extract failed tests
        for match in failed_pattern.findall(log):
            failed_tests.add(match)
        # Extract skipped tests
        for match in skipped_pattern.findall(log):
            skipped_tests.add(match)
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
