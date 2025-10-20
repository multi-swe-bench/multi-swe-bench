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
cat Makefile
###ACTION_DELIMITER###
cat build.sh
###ACTION_DELIMITER###
./build.sh test
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
./build.sh test
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
./build.sh test
###ACTION_DELIMITER###
apt-get install -y libssl-dev zlib1g-dev libsqlite3-dev
###ACTION_DELIMITER###
./build.sh test
###ACTION_DELIMITER###
TOOL_HASH=$(/root/.cache/hypothesis-build-runtimes/python-versions//3.8.13/bin/python tooling/scripts/tool-hash.py < requirements/tools.txt) && source /tmp/.hypothesis-runtimes/virtualenvs/build-$TOOL_HASH/bin/activate && pip install --upgrade pip<24.1 && pip install -r requirements/tools.txt
###ACTION_DELIMITER###
TOOL_HASH=$(/root/.cache/hypothesis-build-runtimes/python-versions/3.8.13/bin/python tooling/scripts/tool-hash.py < requirements/tools.txt) && source /tmp/.hypothesis-runtimes/virtualenvs/build-$TOOL_HASH/bin/activate && pip install --upgrade "pip<24.1" && pip install -r requirements/tools.txt
###ACTION_DELIMITER###
./build.sh test
###ACTION_DELIMITER###
./build.sh check-py38
###ACTION_DELIMITER###
source /tmp/.hypothesis-runtimes/virtualenvs/build-74845f2a92/bin/activate && pip install setuptools==65.0.0
###ACTION_DELIMITER###
./build.sh check-py38
###ACTION_DELIMITER###
echo 'pytest -v -W ignore::DeprecationWarning ./hypothesis-python/tests' > /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
bash /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
echo -e 'source /tmp/.hypothesis-runtimes/virtualenvs/build-74845f2a92/bin/activate
pytest -v -W ignore::DeprecationWarning ./hypothesis-python/tests' > /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
echo -e 'source /tmp/.hypothesis-runtimes/virtualenvs/build-74845f2a92/bin/activate
cd /home/hypothesis/hypothesis-python
pip install -e .
pytest -v -W ignore::DeprecationWarning tests' > /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
bash /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
echo -e 'source /tmp/.hypothesis-runtimes/virtualenvs/build-74845f2a92/bin/activate
cd /home/hypothesis/hypothesis-python
pip install -e .
pip install numpy
pytest -v -W ignore::DeprecationWarning tests' > /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
echo -e 'source /tmp/.hypothesis-runtimes/virtualenvs/build-74845f2a92/bin/activate
cd /home/hypothesis/hypothesis-python
pip install -e .[array_api]
pip install array-api-compat
pytest -v -W ignore::DeprecationWarning tests' > /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
bash /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
echo -e 'source /tmp/.hypothesis-runtimes/virtualenvs/build-74845f2a92/bin/activate
cd /home/hypothesis/hypothesis-python
pip install -e .
pip install numpy array-api-compat
pytest -v -W ignore::DeprecationWarning tests' > /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
echo -e 'source /tmp/.hypothesis-runtimes/virtualenvs/build-74845f2a92/bin/activate
cd /home/hypothesis/hypothesis-python
pip install -e .
pip install numpy array-api-compat
pytest -v -W ignore::DeprecationWarning --ignore=tests/array_api tests' > /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
bash /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
echo -e 'source /tmp/.hypothesis-runtimes/virtualenvs/build-74845f2a92/bin/activate
cd /home/hypothesis/hypothesis-python
pip install -e .
pip install numpy array-api-compat pandas fakeredis
pytest -v -W ignore::DeprecationWarning --ignore=tests/array_api tests' > /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
bash /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libbz2-dev
###ACTION_DELIMITER###
./build.sh check-py38 && echo -e 'source /tmp/.hypothesis-runtimes/virtualenvs/build-74845f2a92/bin/activate
cd /home/hypothesis/hypothesis-python
pip install -e .
pip install numpy array-api-compat pandas fakeredis redis
pytest -v -W ignore::DeprecationWarning --ignore=tests/array_api tests' > /home/hypothesis/test_commands.sh && bash /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
echo -e 'source /tmp/.hypothesis-runtimes/virtualenvs/build-74845f2a92/bin/activate
cd /home/hypothesis/hypothesis-python
pip install -e .
pip install numpy array-api-compat pandas fakeredis redis
pytest -v -W ignore::DeprecationWarning:mypy_extensions --ignore=tests/array_api tests' > /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
echo -e 'source /tmp/.hypothesis-runtimes/virtualenvs/build-74845f2a92/bin/activate
cd /home/hypothesis/hypothesis-python
pip install -e .
pip install numpy array-api-compat pandas fakeredis redis
pytest -v -W "ignore::DeprecationWarning:mypy_extensions" --ignore=tests/array_api tests' > /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
bash /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
./tooling/scripts/ensure-python.sh 3.8.13 && echo -e 'source /tmp/.hypothesis-runtimes/virtualenvs/build-74845f2a92/bin/activate
cd /home/hypothesis/hypothesis-python
pip install -e .
pip install numpy array-api-compat pandas fakeredis redis
pytest -v -W "ignore::DeprecationWarning:mypy_extensions" --ignore=tests/array_api tests' > /home/hypothesis/test_commands.sh && bash /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
rm -rf /root/.cache/hypothesis-build-runtimes/python-versions/3.8.13 && ./tooling/scripts/ensure-python.sh 3.8.13 && echo -e 'source /tmp/.hypothesis-runtimes/virtualenvs/build-74845f2a92/bin/activate
cd /home/hypothesis/hypothesis-python
pip install -e .
pip install numpy array-api-compat pandas fakeredis redis
pytest -v -W "ignore::DeprecationWarning:mypy_extensions" --ignore=tests/array_api tests' > /home/hypothesis/test_commands.sh && bash /home/hypothesis/test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libffi-dev && rm -rf /root/.cache/hypothesis-build-runtimes/python-versions/3.8.13 && ./tooling/scripts/ensure-python.sh 3.8.13 && echo -e 'source /tmp/.hypothesis-runtimes/virtualenvs/build-74845f2a92/bin/activate
cd /home/hypothesis/hypothesis-python
pip install -e .
pip install numpy array-api-compat pandas fakeredis redis
pytest -v -W "ignore::DeprecationWarning:mypy_extensions" --ignore=tests/array_api tests' > /home/hypothesis/test_commands.sh && bash /home/hypothesis/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
source /tmp/.hypothesis-runtimes/virtualenvs/build-74845f2a92/bin/activate
cd /home/hypothesis/hypothesis-python
pip install -e .
pip install numpy array-api-compat pandas fakeredis redis
pytest -v -W "ignore::DeprecationWarning:mypy_extensions" --ignore=tests/array_api tests

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
source /tmp/.hypothesis-runtimes/virtualenvs/build-74845f2a92/bin/activate
cd /home/hypothesis/hypothesis-python
pip install -e .
pip install numpy array-api-compat pandas fakeredis redis
pytest -v -W "ignore::DeprecationWarning:mypy_extensions" --ignore=tests/array_api tests

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
source /tmp/.hypothesis-runtimes/virtualenvs/build-74845f2a92/bin/activate
cd /home/hypothesis/hypothesis-python
pip install -e .
pip install numpy array-api-compat pandas fakeredis redis
pytest -v -W "ignore::DeprecationWarning:mypy_extensions" --ignore=tests/array_api tests

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
RUN git clone https://github.com/HypothesisWorks/hypothesis.git /home/hypothesis

WORKDIR /home/hypothesis
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("HypothesisWorks", "hypothesis_3323_to_3310")
class HYPOTHESIS_3323_TO_3310(Instance):
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
        # Pattern for individual test lines with percentage
        pattern1 = re.compile(r'^(.+?)\s+(PASSED|FAILED|SKIPPED)\s+\[\s*\d+%\]$')
        # Pattern for summary lines (e.g., "FAILED test_name")
        pattern2 = re.compile(r'^(FAILED|SKIPPED|PASSED) (.+)$')
        for line in log.split('\n'):
            line = line.strip()
            # Check pattern1
            match = pattern1.match(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
            else:
                # Check pattern2
                match = pattern2.match(line)
                if match:
                    status = match.group(1)
                    test_name = match.group(2)
                else:
                    continue  # No match
            # Process status
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
