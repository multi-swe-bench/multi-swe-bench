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
                """cat README.md
###ACTION_DELIMITER###
ls -la
###ACTION_DELIMITER###
cat pyproject.toml
###ACTION_DELIMITER###
cat requirements.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libgfortran5
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
pip install pdm
###ACTION_DELIMITER###
pdm install
###ACTION_DELIMITER###
echo 'pytest -v -rA --tb=short --color=yes --import-mode=importlib ./tests' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pdm run pytest -v -rA --tb=short --color=yes --import-mode=importlib ./tests' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pdm add bibtexparser && apt-get update && apt-get install -y openbabel && pdm add openbabel f90nml openff-toolkit
###ACTION_DELIMITER###
pdm add pyopenbabel f90nml && apt-get install -y packmol
###ACTION_DELIMITER###
apt-get install -y python3-openbabel packmol && pdm add f90nml
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'from pybtex.bibtex import *' > /home/pymatgen/.venv/lib/python3.9/site-packages/bibtex.py && pdm run pip install openbabel
###ACTION_DELIMITER###
echo 'from pybtex.bibtex.parser import Parser' > /home/pymatgen/.venv/lib/python3.9/site-packages/bibtex.py && pdm venv remove -y && pdm venv create --system-site-packages && pdm install
###ACTION_DELIMITER###
pdm venv list
###ACTION_DELIMITER###
pdm venv remove --in-project -y && pdm venv create --system-site-packages --in-project && pdm install
###ACTION_DELIMITER###
rm -rf .venv && pdm venv create --system-site-packages --in-project && pdm install
###ACTION_DELIMITER###
pdm venv create --venv-options="--system-site-packages" -n .venv && pdm install
###ACTION_DELIMITER###
rm -rf .venv && virtualenv --system-site-packages .venv && . .venv/bin/activate && pdm install
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pdm run pytest -v -rA --tb=short --color=yes --import-mode=importlib ./tests

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
pdm run pytest -v -rA --tb=short --color=yes --import-mode=importlib ./tests

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
pdm run pytest -v -rA --tb=short --color=yes --import-mode=importlib ./tests

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
RUN git clone https://github.com/materialsproject/pymatgen.git /home/pymatgen

WORKDIR /home/pymatgen
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("materialsproject", "pymatgen_3994_to_3819")
class PYMATGEN_3994_TO_3819(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        import json
        # Remove ANSI escape codes
        cleaned_log = re.sub(r'\x1b\[[0-9;]*m', '', log)
        # Extract passed tests
        passed_pattern = r'PASSED (.*)'
        passed_tests = set(re.findall(passed_pattern, cleaned_log))
        # Extract failed tests
        failed_pattern = r'FAILED (.*?) - '
        failed_tests = set(re.findall(failed_pattern, cleaned_log))
        # Extract skipped tests
        skipped_pattern = r'SKIPPED \[1\] (.*?): '
        skipped_tests = set(re.findall(skipped_pattern, cleaned_log))
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
