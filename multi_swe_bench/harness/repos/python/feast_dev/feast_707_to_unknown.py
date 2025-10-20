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
                """apt-get update && apt-get install -y openjdk-11-jdk maven python3 python3-pip python3-dev golang-go protobuf-compiler
###ACTION_DELIMITER###
make install-python
###ACTION_DELIMITER###
python3 -m venv venv && source venv/bin/activate && make install-python
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv && source venv/bin/activate && make install-python
###ACTION_DELIMITER###
sed -i 's/pandas==0.*/pandas>=1.3.0/' sdk/python/requirements-ci.txt
###ACTION_DELIMITER###
source venv/bin/activate && make install-python
###ACTION_DELIMITER###
sed -i 's/pandas>=1.3.0/pandas>=2.0.0/' sdk/python/requirements-ci.txt
###ACTION_DELIMITER###
source venv/bin/activate && make install-python
###ACTION_DELIMITER###
sed -i 's/pandavro==1.5.*/pandavro>=1.8.0/' sdk/python/requirements-ci.txt
###ACTION_DELIMITER###
source venv/bin/activate && make install-python
###ACTION_DELIMITER###
sed -i 's/pandas>=2.0.0/pandas>=2.1.0/' sdk/python/requirements-ci.txt
###ACTION_DELIMITER###
sed -i 's/pandas>=2.1.0/pandas>=2.2.0/' sdk/python/requirements-ci.txt
###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i -e 's/pandas==0.*/pandas>=2.2.0/' -e 's/pandavro==1.5.*/pandavro>=1.8.0/' sdk/python/setup.py
###ACTION_DELIMITER###
source venv/bin/activate && make install-python
###ACTION_DELIMITER###
sed -i -e 's/"pandas>=2.2.0/"pandas>=2.2.0",/' -e 's/"pandavro>=1.8.0/"pandavro>=1.8.0",/' sdk/python/setup.py
###ACTION_DELIMITER###
source venv/bin/activate && make install-python
###ACTION_DELIMITER###
sed -i 's/fastavro>=0.22.11,<0.23/fastavro>=1.5.1,<2.0.0/' sdk/python/setup.py
###ACTION_DELIMITER###
source venv/bin/activate && make install-python
###ACTION_DELIMITER###
apt-get update && apt-get install -y cmake
###ACTION_DELIMITER###
source venv/bin/activate && make install-python
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy && make install-python
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3-numpy
###ACTION_DELIMITER###
sed -i 's/pyarrow<0.16.0,>=0.15.1/pyarrow>=10.0.0/' sdk/python/setup.py && source venv/bin/activate && CMAKE_ARGS="-DPYTHON_EXECUTABLE=$(which python3)" make install-python
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-11-jdk maven
###ACTION_DELIMITER###
source venv/bin/activate && make test
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.23.5
###ACTION_DELIMITER###
echo -e 'import numpy as np
np.float = float' > sdk/python/tests/conftest.py
###ACTION_DELIMITER###
source venv/bin/activate && make test-python
###ACTION_DELIMITER###
source venv/bin/activate && pip install pytest==7.0.0
###ACTION_DELIMITER###
source venv/bin/activate && make test-python
###ACTION_DELIMITER###
echo 'make test' > /home/feast/test_commands.sh && chmod +x /home/feast/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
make test

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
make test

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
make test

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
RUN git clone https://github.com/feast-dev/feast.git /home/feast

WORKDIR /home/feast
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("feast-dev", "feast_707_to_unknown")
class FEAST_707_TO_UNKNOWN(Instance):
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
        # Regex patterns to match test lines with leading line numbers
        # Pattern 1: [line_num] test_name ... (color code)STATUS(color code)...
        pattern1 = re.compile(r'^(.+?)\s+\x1b\[[0-9;]*m(PASSED|FAILED|SKIPPED)\x1b\[[0-9;]*m.*$')
        # Pattern 2: [line_num] STATUS test_name ...
        pattern2 = re.compile(r'^(?:\[\s*\d+\]\s*)?(PASSED|FAILED|SKIPPED)\s+(.+)$')
        for line in log.split('\n'):
            line = line.strip()
            match1 = pattern1.match(line)
            if match1:
                test_name = match1.group(1).strip()
                status = match1.group(2)
            else:
                match2 = pattern2.match(line)
                if match2:
                    status = match2.group(1)
                    test_name = match2.group(2).strip()
                else:
                    continue  # No match, skip to next line
            # Add test name to the appropriate set
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
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
