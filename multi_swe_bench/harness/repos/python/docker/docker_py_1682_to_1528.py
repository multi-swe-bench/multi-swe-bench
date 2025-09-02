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
        return "python:3.10-slim"
    
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
                """cat test-requirements.txt
###ACTION_DELIMITER###
pip install py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls
###ACTION_DELIMITER###
cat requirements.txt
###ACTION_DELIMITER###
cat pytest.ini
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip list
###ACTION_DELIMITER###
pip install -r test-requirements.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip show pytest
###ACTION_DELIMITER###

###ACTION_DELIMITER###
echo $PATH
###ACTION_DELIMITER###
find / -name pytest 2>/dev/null
###ACTION_DELIMITER###
python -m pytest -v
###ACTION_DELIMITER###
pip install --upgrade pytest
###ACTION_DELIMITER###
python -m pytest -v
###ACTION_DELIMITER###
pip install --upgrade coverage
###ACTION_DELIMITER###
pip install --upgrade pytest-cov
###ACTION_DELIMITER###
python -m pytest -v
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
python -m pytest -v
###ACTION_DELIMITER###
pip install urllib3==1.26.15
###ACTION_DELIMITER###
pip install --upgrade requests==2.25.1
###ACTION_DELIMITER###
python -m pytest -v
###ACTION_DELIMITER###
echo 'import pytest
from py.path import ensuretemp
pytest.ensuretemp = ensuretemp' > conftest.py
###ACTION_DELIMITER###
python -m pytest -v
###ACTION_DELIMITER###
echo 'import pytest
from py.path.local import ensuretemp
pytest.ensuretemp = ensuretemp' > conftest.py
###ACTION_DELIMITER###
echo 'import pytest
from py.path import local
pytest.ensuretemp = local.ensuretemp' > conftest.py
###ACTION_DELIMITER###
echo 'import sys
from py.path.local import ensuretemp

if "py" not in sys.modules:
    sys.modules["py"] = type(sys)("py")
py = sys.modules["py"]

if "py.test" not in sys.modules:
    sys.modules["py.test"] = type(sys)("py.test")
py_test = sys.modules["py.test"]

py_test.ensuretemp = ensuretemp' > conftest.py
###ACTION_DELIMITER###
python -m pytest -v
###ACTION_DELIMITER###
pip install --force-reinstall py && echo 'import pytest
from py.path import ensuretemp
pytest.ensuretemp = ensuretemp' > conftest.py
###ACTION_DELIMITER###
pip uninstall -y py && pip install py && echo 'import pytest
from py.path import ensuretemp
pytest.ensuretemp = ensuretemp' > conftest.py
###ACTION_DELIMITER###
ls /usr/local/lib/python3.10/site-packages/py
###ACTION_DELIMITER###
pip install --upgrade py && echo 'import pytest
from py import path
pytest.ensuretemp = path.local.ensuretemp' > conftest.py
###ACTION_DELIMITER###
pip install --upgrade py==1.12.0 && echo 'import pytest
from py import path
pytest.ensuretemp = path.ensuretemp' > conftest.py
###ACTION_DELIMITER###
pip install --force-reinstall py && echo 'import sys
from py.path import local

if "py" not in sys.modules:
    sys.modules["py"] = type(sys)("py")
py = sys.modules["py"]

if "py.test" not in sys.modules:
    sys.modules["py.test"] = type(sys)("py.test")
py_test = sys.modules["py.test"]

py_test.ensuretemp = local.ensuretemp' > conftest.py
###ACTION_DELIMITER###
pip install --no-binary :all: py && echo 'import sys
from py.path import ensuretemp

if "py" not in sys.modules:
    sys.modules["py"] = type(sys)("py")
py = sys.modules["py"]

if "py.test" not in sys.modules:
    sys.modules["py.test"] = type(sys)("py.test")
py_test = sys.modules["py.test"]

py_test.ensuretemp = ensuretemp' > conftest.py
###ACTION_DELIMITER###
echo 'import sys
import tempfile

if "py" not in sys.modules:
    sys.modules["py"] = type(sys)("py")
py = sys.modules["py"]

if "py.test" not in sys.modules:
    sys.modules["py.test"] = type(sys)("py.test")
py_test = sys.modules["py.test"]

def ensuretemp(*args, **kwargs):
    return tempfile.TemporaryDirectory(*args, **kwargs)

py_test.ensuretemp = ensuretemp' > conftest.py
###ACTION_DELIMITER###
python -m pytest -v
###ACTION_DELIMITER###
echo 'python -m pytest -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python -m pytest -v

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
python -m pytest -v

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
python -m pytest -v

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
FROM python:3.10-slim

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
RUN git clone https://github.com/docker/docker-py.git /home/docker-py

WORKDIR /home/docker-py
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("docker", "docker_py_1682_to_1528")
class DOCKER_PY_1682_TO_1528(Instance):
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
        # Capture passed tests from lines with "PASSED"
        passed_pattern = re.compile(r'(tests/[^\s]+\.py::[^\s]+)\s+PASSED', re.MULTILINE)
        passed_matches = passed_pattern.findall(log)
        passed_tests.update(passed_matches)
        # Capture failed tests (ERROR, FAILED, XFAIL)
        failed_patterns = [
            # Match detailed lines with ERROR or FAILED
            re.compile(r'(tests/[^\s]+\.py::[^\s]+)\s+(ERROR|FAILED)', re.MULTILINE),
            # Match summary lines with XFAIL
            re.compile(r'XFAIL\s+(tests/[^\s]+\.py::[^\s]+)', re.MULTILINE)
        ]
        for pattern in failed_patterns:
            matches = pattern.findall(log)
            for match in matches:
                test_name = match[0] if isinstance(match, tuple) else match
                failed_tests.add(test_name)
        # Capture skipped tests from lines with "SKIPPED"
        skipped_pattern = re.compile(r'(tests/[^\s]+\.py::[^\s]+)\s+SKIPPED', re.MULTILINE)
        skipped_matches = skipped_pattern.findall(log)
        skipped_tests.update(skipped_matches)
        # Resolve conflicts: ensure tests are only in one category
        # Remove tests from skipped if they are in failed
        skipped_tests = skipped_tests - failed_tests
        # Remove tests from passed if they are in failed or skipped
        passed_tests = passed_tests - failed_tests - skipped_tests
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
