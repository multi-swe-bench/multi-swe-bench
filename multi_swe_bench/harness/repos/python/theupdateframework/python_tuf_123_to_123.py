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
apt-get update && apt-get install -y build-essential libssl-dev
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
python -m unittest discover -s tests -v
###ACTION_DELIMITER###
ls tests
###ACTION_DELIMITER###
ls tests/unit
###ACTION_DELIMITER###
python -m unittest tests.unit.test_download -v
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2.7 python-pip
###ACTION_DELIMITER###
ls -la tests/unit
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python2.7 python-pip
###ACTION_DELIMITER###
apt-get install -y python2.7
###ACTION_DELIMITER###
apt-get install -y curl && curl -O https://bootstrap.pypa.io/pip/2.7/get-pip.py && python2.7 get-pip.py && pip2.7 install pycrypto>=2.6
###ACTION_DELIMITER###
apt-get install -y python2.7-dev
###ACTION_DELIMITER###
pip2.7 install pycrypto>=2.6
###ACTION_DELIMITER###
python2.7 -m unittest discover -s tests -v
###ACTION_DELIMITER###
touch tests/__init__.py tests/unit/__init__.py tests/integration/__init__.py
###ACTION_DELIMITER###
python2.7 -m unittest tests.unit.test_download -v
###ACTION_DELIMITER###
python2.7 -m unittest -v tests.unit.test_download
###ACTION_DELIMITER###
python2.7 tests/unit/simple_server.py & python2.7 -m unittest -v tests.unit.test_download
###ACTION_DELIMITER###
python2.7 tests/unit/simple_server.py
###ACTION_DELIMITER###
python2.7 tests/unit/simple_server.py > server.log 2>&1 & sleep 10; cat server.log; python2.7 -m unittest -v tests.unit.test_download; kill $!
###ACTION_DELIMITER###
python2.7 tests/unit/simple_server.py 30000 & sleep 5; python2.7 -m unittest -v tests.unit.test_download; kill $!
###ACTION_DELIMITER###
cd tests/unit && ln -s /usr/bin/python2.7 python && python2.7 -m unittest -v test_download && rm python
###ACTION_DELIMITER###
PYTHONPATH=/home/python-tuf python2.7 -m unittest -v test_download
###ACTION_DELIMITER###
python2.7 tests/unit/simple_server.py 30000 & sleep 5; PYTHONPATH=/home/python-tuf python2.7 -m unittest -v tests/unit/test_download; kill $!
###ACTION_DELIMITER###
python2.7 simple_server.py 30000 & sleep 5; PYTHONPATH=/home/python-tuf python2.7 -m unittest -v test_download; kill $!
###ACTION_DELIMITER###
ln -s /usr/bin/python2.7 python && PYTHONPATH=/home/python-tuf python2.7 -m unittest -v test_download && rm python
###ACTION_DELIMITER###
rm -f python; ln -s /usr/bin/python2.7 python; python2.7 simple_server.py 30000 & sleep 5; netstat -tulpn | grep 30000; PYTHONPATH=/home/python-tuf python2.7 -m unittest -v test_download; kill $!
###ACTION_DELIMITER###
rm -f python; ln -s /usr/bin/python2.7 python; PYTHONPATH=/home/python-tuf python2.7 -m unittest -v test_download; rm python
###ACTION_DELIMITER###
rm -f python; ln -s /usr/bin/python2.7 python; python2.7 simple_server.py 30000 > server.log 2>&1 & sleep 10; cat server.log; PYTHONPATH=/home/python-tuf python2.7 -m unittest -v test_download; kill $!
###ACTION_DELIMITER###
echo 'PYTHONPATH=/home/python-tuf python2.7 -m unittest discover -s tests -v' > /home/python-tuf/test_commands.sh && chmod +x /home/python-tuf/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
PYTHONPATH=/home/python-tuf python2.7 -m unittest discover -s tests -v

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
PYTHONPATH=/home/python-tuf python2.7 -m unittest discover -s tests -v

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
PYTHONPATH=/home/python-tuf python2.7 -m unittest discover -s tests -v

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
RUN git clone https://github.com/theupdateframework/python-tuf.git /home/python-tuf

WORKDIR /home/python-tuf
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("theupdateframework", "python_tuf_123_to_123")
class PYTHON_TUF_123_TO_123(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re
        # Regex patterns to match test lines
        # Pattern 1: [ 136] test_name (class) ... ok/ERROR/skipped
        line_pattern = re.compile(r"^\s*([\w_.]+)\s+\(.*?\)\s+\.\.\.\s+(ok|ERROR|skipped)")
        # Pattern 2: [ 363] ERROR: test_name (class) or [ 599] FAIL: test_name (class)
        prefix_pattern = re.compile(r"^\s*(ERROR|FAIL):\s+([\w_.]+)\s+")
        for line in log.split("\n"):
            # Match Pattern 1
            line_match = line_pattern.search(line)
            if line_match:
                test_name = line_match.group(1)
                status = line_match.group(2)
                if status == "ok":
                    passed_tests.add(test_name)
                elif status == "ERROR":
                    failed_tests.add(test_name)
                elif status == "skipped":
                    skipped_tests.add(test_name)
            # Match Pattern 2
            prefix_match = prefix_pattern.search(line)
            if prefix_match:
                status = prefix_match.group(1)
                test_name = prefix_match.group(2)
                failed_tests.add(test_name)
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
