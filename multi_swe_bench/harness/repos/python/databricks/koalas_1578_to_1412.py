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
                """ls
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.7 python3.7-venv python3.7-pip
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.7 python3.7-venv python3.7-pip
###ACTION_DELIMITER###
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.7 get-pip.py
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.7 get-pip.py
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
###ACTION_DELIMITER###
wget https://www.python.org/ftp/python/3.7.17/Python-3.7.17.tgz
###ACTION_DELIMITER###
tar xzf Python-3.7.17.tgz
###ACTION_DELIMITER###
cd Python-3.7.17 && ./configure --enable-optimizations
###ACTION_DELIMITER###
make -j 4
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
cd ..
###ACTION_DELIMITER###
python3.7 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
pip install 'pyspark>=2.4.0'
###ACTION_DELIMITER###
echo 'venv/bin/pytest -v -rA' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libsqlite3-dev
###ACTION_DELIMITER###
cd Python-3.7.17 && make clean && ./configure --enable-optimizations && make -j 4 && make install
###ACTION_DELIMITER###
cd ..
###ACTION_DELIMITER###
rm -rf venv
###ACTION_DELIMITER###
python3.7 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo 'venv/bin/pytest -v -rA' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libbz2-dev
###ACTION_DELIMITER###
cd Python-3.7.17 && make clean && ./configure --enable-optimizations && make -j 4 && make install
###ACTION_DELIMITER###
cd ..
###ACTION_DELIMITER###
rm -rf venv && python3.7 -m venv venv && source venv/bin/activate && pip install -r requirements-dev.txt && pip install 'pyspark>=2.4.0' && echo 'venv/bin/pytest -v -rA' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-11-jdk && export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64 && source venv/bin/activate && bash test_commands.sh
###ACTION_DELIMITER###
echo $JAVA_HOME && java -version && python -c 'import _sqlite3; import bz2; print("Python modules OK")' && venv/bin/pytest tests/ -v -rA --ignore=tests/gui/
###ACTION_DELIMITER###
find . -name 'test_*.py'
###ACTION_DELIMITER###
echo 'venv/bin/pytest databricks/koalas/tests/ -v -rA' > test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
venv/bin/pytest databricks/koalas/tests/ -v -rA

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
venv/bin/pytest databricks/koalas/tests/ -v -rA

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
venv/bin/pytest databricks/koalas/tests/ -v -rA

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
RUN git clone https://github.com/databricks/koalas.git /home/koalas

WORKDIR /home/koalas
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("databricks", "koalas_1578_to_1412")
class KOALAS_1578_TO_1412(Instance):
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
        # Regex patterns to match test statuses
        # Pattern 1: Matches lines like "databricks/...::test_name PASSED [  0%]"
        passed_pattern = re.compile(r'^(.+?)\s+PASSED\s+\[\s*\d+%\s*\]$', re.MULTILINE)
        # Pattern 2: Matches lines like "FAILED databricks/...::test_name"
        failed_pattern = re.compile(r'^FAILED\s+([^\s-]+)\s*', re.MULTILINE)
        # Pattern 3: Matches lines with "SKIPPED" (if present in logs)
        skipped_pattern = re.compile(r'^(.+?)\s+SKIPPED\s+\[\s*\d+%\s*\]$', re.MULTILINE)
        # Extract test names from log
        passed_tests.update(passed_pattern.findall(log))
        failed_tests.update(failed_pattern.findall(log))
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
