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
                """ls -la
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip python-is-python3 openjdk-11-jdk maven build-essential
###ACTION_DELIMITER###
make install-python-ci-dependencies PYTHON=3
###ACTION_DELIMITER###
pip3 install piptools
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate && pip install piptools
###ACTION_DELIMITER###
source venv/bin/activate && pip install --upgrade pip
###ACTION_DELIMITER###
source venv/bin/activate && pip install piptools
###ACTION_DELIMITER###
source venv/bin/activate && pip install --index-url https://pypi.org/simple/ --trusted-host pypi.org --trusted-host files.pythonhosted.org piptools
###ACTION_DELIMITER###
source venv/bin/activate && pip install pip-tools
###ACTION_DELIMITER###
source venv/bin/activate && make install-python-ci-dependencies PYTHON=3
###ACTION_DELIMITER###
ls sdk/python/requirements
###ACTION_DELIMITER###
source venv/bin/activate && make lock-python-ci-dependencies PYTHON=3.12
###ACTION_DELIMITER###
apt-get install -y python3.10 python3.10-venv
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository universe && apt-get update && apt-get install -y python3.10 python3.10-venv
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.8 python3.8-venv
###ACTION_DELIMITER###
apt-get install -y python3.8 virtualenv && virtualenv -p python3.8 venv && source venv/bin/activate && pip install --upgrade pip && pip install piptools
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.8 && virtualenv -p python3.8 venv && source venv/bin/activate && pip install --upgrade pip && pip install piptools
###ACTION_DELIMITER###
apt-get install -y python3.8-distutils
###ACTION_DELIMITER###
source venv/bin/activate && pip install --upgrade pip && pip install piptools && pip-sync sdk/python/requirements/py3.8-ci-requirements.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip install pip-tools
###ACTION_DELIMITER###
source venv/bin/activate && make install-python-ci-dependencies PYTHON=3.8
###ACTION_DELIMITER###
apt-get install -y libsasl2-dev openjdk-8-jdk && source venv/bin/activate && pip install setuptools==58.0.0 && make install-python-ci-dependencies PYTHON=3.8
###ACTION_DELIMITER###
apt-get install -y libthrift-dev thrift && source venv/bin/activate && pip install setuptools==58.0.0 && make install-python-ci-dependencies PYTHON=3.8
###ACTION_DELIMITER###
apt-get install -y libthrift-dev thrift-compiler && source venv/bin/activate && pip install setuptools==58.0.0 && make install-python-ci-dependencies PYTHON=3.8
###ACTION_DELIMITER###
apt-get install -y libsasl2-dev && source venv/bin/activate && pip install thriftpy2 && make install-python-ci-dependencies PYTHON=3.8
###ACTION_DELIMITER###
apt-get install -y python3.8-dev && source venv/bin/activate && pip install thriftpy2 && make install-python-ci-dependencies PYTHON=3.8
###ACTION_DELIMITER###
apt-get install -y libevent-dev && source venv/bin/activate && pip install thriftpy2 && make install-python-ci-dependencies PYTHON=3.8
###ACTION_DELIMITER###
echo 'source venv/bin/activate && python -m pytest -v -n 8 sdk/python/tests' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'source venv/bin/activate && FEAST_IS_LOCAL_TEST=True python -m pytest -v -n 8 -k "not docker" --junitxml=test-results.xml sdk/python/tests' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
source venv/bin/activate && FEAST_IS_LOCAL_TEST=True python -m pytest -v -n 8 -k "not docker" --junitxml=test-results.xml sdk/python/tests

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
source venv/bin/activate && FEAST_IS_LOCAL_TEST=True python -m pytest -v -n 8 -k "not docker" --junitxml=test-results.xml sdk/python/tests

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
source venv/bin/activate && FEAST_IS_LOCAL_TEST=True python -m pytest -v -n 8 -k "not docker" --junitxml=test-results.xml sdk/python/tests

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


@Instance.register("feast-dev", "feast_3964_to_3925")
class FEAST_3964_TO_3925(Instance):
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
        # Regex patterns to match test results
        passed_pattern = re.compile(r".*?PASSED\s+((?:\w+/)*tests/.*?::.*?)\s*$", re.MULTILINE)
        failed_pattern = re.compile(r".*?FAILED\s+((?:\w+/)*tests/.*?::.*?)\s*$", re.MULTILINE)
        error_pattern = re.compile(r".*?ERROR\s+((?:\w+/)*tests/.*?::.*?)\s*$", re.MULTILINE)
        skipped_pattern = re.compile(r".*?SKIPPED\s+((?:\w+/)*tests/.*?::.*?)\s*$", re.MULTILINE)
        # Extract test names
        passed_tests.update(passed_pattern.findall(log))
        failed_tests.update(failed_pattern.findall(log))
        failed_tests.update(error_pattern.findall(log))
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
