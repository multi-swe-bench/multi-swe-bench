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
                """ls -la
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
###ACTION_DELIMITER###
bash /tmp/miniconda.sh -b -p /home/miniconda3
###ACTION_DELIMITER###
export PATH=/home/miniconda3/bin:$PATH
###ACTION_DELIMITER###
/home/miniconda3/bin/python setup.py develop
###ACTION_DELIMITER###
conda create -n conda-dev python=3.7 -y
###ACTION_DELIMITER###
wget https://repo.anaconda.com/miniconda/Miniconda3-py37_4.12.0-Linux-x86_64.sh -O /tmp/miniconda.sh
###ACTION_DELIMITER###
bash /tmp/miniconda.sh -b -p /home/miniconda3-py37
###ACTION_DELIMITER###
export PATH=/home/miniconda3-py37/bin:$PATH
###ACTION_DELIMITER###
/home/miniconda3-py37/bin/python setup.py develop
###ACTION_DELIMITER###
conda install -y pytest pytest-cov
###ACTION_DELIMITER###
/home/miniconda3-py37/bin/pip install cytoolz
###ACTION_DELIMITER###
sed -i '467s/^\(\s*\)f\.__name__ for f in reversed(\(.*\)),$/\1(f.__name__ for f in reversed(\2)),/' /home/conda/conda/_vendor/toolz/functoolz.py
###ACTION_DELIMITER###
conda --version
###ACTION_DELIMITER###
/home/miniconda3-py37/bin/pip install pytest pytest-cov
###ACTION_DELIMITER###
/home/miniconda3-py37/bin/pytest -v
###ACTION_DELIMITER###
/home/miniconda3-py37/bin/pip install responses
###ACTION_DELIMITER###
sed -i '12a \    timeout: tests with a timeout' setup.cfg
###ACTION_DELIMITER###
/home/miniconda3-py37/bin/pytest -v
###ACTION_DELIMITER###
/home/miniconda3-py37/bin/pip install mock anaconda-client
###ACTION_DELIMITER###
echo '/home/miniconda3-py37/bin/pytest -v' > /home/conda/test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
/home/miniconda3-py37/bin/pytest -v

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
/home/miniconda3-py37/bin/pytest -v

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
/home/miniconda3-py37/bin/pytest -v

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
RUN git clone https://github.com/conda/conda.git /home/conda

WORKDIR /home/conda
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("conda", "conda_3629_to_3326")
class CONDA_3629_TO_3326(Instance):
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
        # Extract all valid test names (e.g., tests/module.py::TestClass::test_method or tests/module.py::test_function[param])
        all_tests = set(re.findall(r'tests/[\w/]+\.py::[\w:]+(?:\[\w+\])?', log))
        # Extract skipped tests (full name up to SKIPPED)
        skipped_matches = re.findall(r'^(tests/\S+) SKIPPED', log, re.MULTILINE)
        skipped_tests.update(skipped_matches)
        # Extract failed tests (full name after FAILED)
        failed_matches = re.findall(r'^FAILED (tests/\S+)', log, re.MULTILINE)
        failed_tests.update(failed_matches)
        # Calculate passed tests as all tests not skipped or failed
        passed_tests = all_tests - skipped_tests - failed_tests
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
