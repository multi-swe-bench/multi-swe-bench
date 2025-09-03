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
                """apt-get update && apt-get install -y python3.7 python3.7-venv python3.7-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl
###ACTION_DELIMITER###
wget https://www.python.org/ftp/python/3.7.17/Python-3.7.17.tgz && tar xzf Python-3.7.17.tgz && cd Python-3.7.17 && ./configure --prefix=/usr/local --enable-shared && make -j 4 && make altinstall && ldconfig
###ACTION_DELIMITER###

###ACTION_DELIMITER###
python3.7 --version
###ACTION_DELIMITER###
pip install nox
###ACTION_DELIMITER###
cd /home/google-cloud-python
###ACTION_DELIMITER###
echo -e '#!/bin/bash
for package in */; do
  if [ -f "$package/noxfile.py" ]; then
    echo "Running tests for $package"
    (cd "$package" && nox -v -s unit-3.7 system-3.7 snippets-3.7)
  fi
 done' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
for package in */; do
  if [ -f "$package/noxfile.py" ]; then
    echo "Running tests for $package"
    (cd "$package" && \
     nox --list-sessions | grep -q "unit-3.7" && nox -v -s unit-3.7 || true; \
     nox --list-sessions | grep -q "system-3.7" && nox -v -s system-3.7 || true; \
     nox --list-sessions | grep -q "snippets-3.7" && nox -v -s snippets-3.7 || true)
  fi
 done' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
for package in */; do
  if [ -f "$package/noxfile.py" ]; then
    echo "Running tests for $package"
    (cd "$package" && \
     # Upgrade pip to compatible version for Python 3.7 before installing dependencies
     nox --list-sessions | grep -q "unit-3.7" && nox -v -s unit-3.7 --pip-args "--upgrade pip==22.3.1" || true; \
     nox --list-sessions | grep -q "system-3.7" && nox -v -s system-3.7 || true; \
     nox --list-sessions | grep -q "snippets-3.7" && nox -v -s snippets-3.7 || true)
  fi
 done' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
for package in */; do
  if [ -f "$package/noxfile.py" ]; then
    echo "Running tests for $package"
    (cd "$package" && \
     export VIRTUALENV_PIP=22.3.1 && \
     nox --list-sessions | grep -q "unit-3.7" && nox -v -s unit-3.7 || true; \
     nox --list-sessions | grep -q "system-3.7" && nox -v -s system-3.7 || true; \
     nox --list-sessions | grep -q "snippets-3.7" && nox -v -s snippets-3.7 || true)
  fi
 done' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
for package in */; do
  if [ -f "$package/noxfile.py" ]; then
    echo "Running tests for $package"
    (cd "$package" && \
     export VIRTUALENV_PIP=22.3.1 && \
     export VIRTUALENV_SETUPTOOLS=65.5.1 && \
     nox --list-sessions | grep -q "unit-3.7" && nox -v -s unit-3.7 || true; \
     nox --list-sessions | grep -q "system-3.7" && nox -v -s system-3.7 || true; \
     nox --list-sessions | grep -q "snippets-3.7" && nox -v -s snippets-3.7 || true)
  fi
 done' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
for package in */; do
  if [ -f "$package/noxfile.py" ]; then
    echo "Running tests for $package"
    (cd "$package" && \
     export VIRTUALENV_PIP=22.3.1 && \
     export VIRTUALENV_SETUPTOOLS=65.5.1 && \
     export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python && \
     nox --list-sessions | grep -q "unit-3.7" && nox -v -s unit-3.7 || true; \
     nox --list-sessions | grep -q "system-3.7" && nox -v -s system-3.7 || true; \
     nox --list-sessions | grep -q "snippets-3.7" && nox -v -s snippets-3.7 || true)
  fi
 done' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
for package in */; do
  if [ -f "$package/noxfile.py" ]; then
    echo "Running tests for $package"
    (cd "$package" && \
     export VIRTUALENV_PIP=22.3.1 && \
     export VIRTUALENV_SETUPTOOLS=65.5.1 && \
     export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python && \
     nox --list-sessions | grep -q "unit-3.7" && nox -v -s unit-3.7 || true; \
     nox --list-sessions | grep -q "system-3.7" && nox -v -s system-3.7 || true; \
     nox --list-sessions | grep -q "snippets-3.7" && nox -v -s snippets-3.7 || true)
  fi
 done

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
#!/bin/bash
for package in */; do
  if [ -f "$package/noxfile.py" ]; then
    echo "Running tests for $package"
    (cd "$package" && \
     export VIRTUALENV_PIP=22.3.1 && \
     export VIRTUALENV_SETUPTOOLS=65.5.1 && \
     export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python && \
     nox --list-sessions | grep -q "unit-3.7" && nox -v -s unit-3.7 || true; \
     nox --list-sessions | grep -q "system-3.7" && nox -v -s system-3.7 || true; \
     nox --list-sessions | grep -q "snippets-3.7" && nox -v -s snippets-3.7 || true)
  fi
 done

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
#!/bin/bash
for package in */; do
  if [ -f "$package/noxfile.py" ]; then
    echo "Running tests for $package"
    (cd "$package" && \
     export VIRTUALENV_PIP=22.3.1 && \
     export VIRTUALENV_SETUPTOOLS=65.5.1 && \
     export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python && \
     nox --list-sessions | grep -q "unit-3.7" && nox -v -s unit-3.7 || true; \
     nox --list-sessions | grep -q "system-3.7" && nox -v -s system-3.7 || true; \
     nox --list-sessions | grep -q "snippets-3.7" && nox -v -s snippets-3.7 || true)
  fi
 done

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
RUN git clone https://github.com/googleapis/google-cloud-python.git /home/google-cloud-python

WORKDIR /home/google-cloud-python
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("googleapis", "google_cloud_python_10205_to_unknown")
class GOOGLE_CLOUD_PYTHON_10205_TO_UNKNOWN(Instance):
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
        pass
