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
pip install -e .[dev]
###ACTION_DELIMITER###
sed -i 's/license=\["BSD"\]/license="BSD-3"/' setup.py
###ACTION_DELIMITER###
pip install -e .[dev]
###ACTION_DELIMITER###
echo 'pytest -v --ignore=test_mpi.py tests/' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'cd tests && pytest -v --ignore=test_mpi.py' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYTHONPATH="${PYTHONPATH}:/home/cogent3/src"
cd tests && pytest -v --ignore=test_mpi.py' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
python -c 'import cogent3; print(cogent3.__version__)'
###ACTION_DELIMITER###
pip install numpy==1.26.0
###ACTION_DELIMITER###
python -c 'import cogent3; print(cogent3.__version__)'
###ACTION_DELIMITER###
pip install numba==0.55.0
###ACTION_DELIMITER###
pip install pandas==1.5.3
###ACTION_DELIMITER###
python -c 'import cogent3; print(cogent3.__version__)'
###ACTION_DELIMITER###
pip install --force-reinstall numba==0.55.0
###ACTION_DELIMITER###
pip install numba==0.56.0
###ACTION_DELIMITER###
python -c 'from numba import jitclass; print("jitclass imported successfully")'
###ACTION_DELIMITER###
pip uninstall -y numba llvmlite && pip install numba==0.56.0
###ACTION_DELIMITER###
pip install numba==0.54.0
###ACTION_DELIMITER###
pip install --no-cache-dir numba==0.54.0
###ACTION_DELIMITER###
pip uninstall -y numba llvmlite && pip install numba==0.53.0
###ACTION_DELIMITER###
python -c 'import numba; print("jitclass" in dir(numba))'
###ACTION_DELIMITER###
pip uninstall -y numba llvmlite && pip install numba==0.49.0
###ACTION_DELIMITER###
apt-get update && apt-get install -y llvm llvm-dev
###ACTION_DELIMITER###
pip install numba==0.53.0
###ACTION_DELIMITER###
export LLVM_CONFIG=llvm-config-14 && pip uninstall -y numba llvmlite && pip install numba==0.56.0 llvmlite==0.39.0
###ACTION_DELIMITER###
python -c 'from numba.experimental import jitclass; print("jitclass found in numba.experimental")'
###ACTION_DELIMITER###
sed -i '/jitclass,/d' src/cogent3/align/pairwise_pogs_numba.py && sed -i '14a from numba.experimental import jitclass' src/cogent3/align/pairwise_pogs_numba.py
###ACTION_DELIMITER###
python -c 'import cogent3; print(cogent3.__version__)'
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
export PYTHONPATH="${PYTHONPATH}:/home/cogent3/src"
cd tests && pytest -v --ignore=test_mpi.py

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
export PYTHONPATH="${PYTHONPATH}:/home/cogent3/src"
cd tests && pytest -v --ignore=test_mpi.py

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
export PYTHONPATH="${PYTHONPATH}:/home/cogent3/src"
cd tests && pytest -v --ignore=test_mpi.py

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
RUN git clone https://github.com/cogent3/cogent3.git /home/cogent3

WORKDIR /home/cogent3
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("cogent3", "cogent3_703_to_669")
class COGENT3_703_TO_669(Instance):
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
        import json
        # Extract test cases using regular expressions
        # Pattern for passed tests: matches test file path followed by PASSED
        passed_pattern = re.compile(r'([\w\/-]+\.py::[\w]+(?:::[\w]+)*) PASSED')
        passed_tests.update(passed_pattern.findall(log))
        # Pattern for failed tests: matches FAILED followed by test file path
        failed_pattern = re.compile(r'FAILED ([\w\/-]+\.py::[\w]+(?:::[\w]+)*)')
        failed_tests.update(failed_pattern.findall(log))
        # Pattern for skipped tests: matches SKIPPED followed by test file path
        skipped_pattern = re.compile(r'([\w\/-]+\.py::[\w]+(?:::[\w]+)*)\s+SKIPPED')
        skipped_tests.update(skipped_pattern.findall(log))
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
