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
apt-get update && apt-get install -y phantomjs
###ACTION_DELIMITER###
apt-get install -y nodejs npm
###ACTION_DELIMITER###
npm install phantomjs
###ACTION_DELIMITER###
npm install phantomjs-prebuilt
###ACTION_DELIMITER###
pip3 install flit && flit install --symlink
###ACTION_DELIMITER###
pip3 install -e .
###ACTION_DELIMITER###
pip3 install flit==3.0.0 && flit install --symlink
###ACTION_DELIMITER###
apt-get update && apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl
###ACTION_DELIMITER###
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
###ACTION_DELIMITER###
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc && echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc && echo 'eval "$(pyenv init -)"' >> ~/.bashrc && source ~/.bashrc
###ACTION_DELIMITER###
pyenv install 3.4.0
###ACTION_DELIMITER###
apt-get install -y libssl-dev libffi-dev && export CFLAGS="-I/usr/include/openssl" LDFLAGS="-L/usr/lib/x86_64-linux-gnu" && pyenv install 3.4.0
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye main' >> /etc/apt/sources.list && apt-get update && apt-get install -y libssl1.1 libssl-dev && export CFLAGS="-I/usr/include/openssl" LDFLAGS="-L/usr/lib/x86_64-linux-gnu" && pyenv install 3.4.0
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye main' >> /etc/apt/sources.list && apt-get update && apt-get install -y libssl1.1 libssl-dev/bullseye && export CFLAGS="-I/usr/include/openssl" LDFLAGS="-L/usr/lib/x86_64-linux-gnu" && pyenv install 3.4.0
###ACTION_DELIMITER###
apt-get install -y --allow-downgrades libssl-dev/bullseye && export CFLAGS="-I/usr/include/openssl" LDFLAGS="-L/usr/lib/x86_64-linux-gnu" && pyenv install 3.4.0
###ACTION_DELIMITER###
export CONFIGURE_OPTS="--with-ssl" && export CFLAGS="-I/usr/include/openssl" && export LDFLAGS="-L/usr/lib/x86_64-linux-gnu" && pyenv install 3.4.0
###ACTION_DELIMITER###
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && bash miniconda.sh -b -p $HOME/miniconda && export PATH="$HOME/miniconda/bin:$PATH" && conda create -y -n py34 python=3.4 && conda activate py34
###ACTION_DELIMITER###
conda tos accept --yes --channel https://repo.anaconda.com/pkgs/main --channel https://repo.anaconda.com/pkgs/r
###ACTION_DELIMITER###
echo 'yes' | conda tos accept --channel https://repo.anaconda.com/pkgs/main --channel https://repo.anaconda.com/pkgs/r
###ACTION_DELIMITER###
conda create -y -n py34 python=3.4 && conda activate py34
###ACTION_DELIMITER###
conda config --add channels conda-forge && conda create -y -n py34 python=3.4 -c conda-forge && conda activate py34
###ACTION_DELIMITER###
conda init bash && source ~/.bashrc
###ACTION_DELIMITER###
conda activate py34
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
curl https://bootstrap.pypa.io/pip/3.4/get-pip.py | python - && pip install -e .
###ACTION_DELIMITER###
pip install flit==3.0.0 && flit install --symlink
###ACTION_DELIMITER###
pip install flit==1.3 && flit install --symlink
###ACTION_DELIMITER###
pip install flit==1.3 --ignore-installed certifi && flit install --symlink
###ACTION_DELIMITER###
pip install flit==1.3 --ignore-installed certifi && FLIT_ROOT_INSTALL=1 flit install --symlink
###ACTION_DELIMITER###
pip install tornado==4.5.3 && FLIT_ROOT_INSTALL=1 flit install --symlink
###ACTION_DELIMITER###
pip install jsonschema==2.6.0 && FLIT_ROOT_INSTALL=1 flit install --symlink
###ACTION_DELIMITER###
pip install pyzmq==14.7.0 && FLIT_ROOT_INSTALL=1 flit install --symlink
###ACTION_DELIMITER###
apt-get install -y libsodium-dev && pip install pyzmq==16.0.2 && FLIT_ROOT_INSTALL=1 flit install --symlink
###ACTION_DELIMITER###
invoke tests
###ACTION_DELIMITER###
pip install invoke==1.4.1 && invoke tests
###ACTION_DELIMITER###
cat tasks.py
###ACTION_DELIMITER###
py.test --cov nbgrader --no-cov-on-fail -v -x
###ACTION_DELIMITER###
echo 'py.test --cov nbgrader --no-cov-on-fail -v' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
py.test --cov nbgrader --no-cov-on-fail -v

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
py.test --cov nbgrader --no-cov-on-fail -v

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
py.test --cov nbgrader --no-cov-on-fail -v

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
RUN git clone https://github.com/jupyter/nbgrader.git /home/nbgrader

WORKDIR /home/nbgrader
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("jupyter", "nbgrader_357_to_339")
class NBGRADER_357_TO_339(Instance):
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
        # Parse test cases using regex pattern
        pattern = re.compile(r'\s+(nbgrader/tests/.*?\.py::.*?)\s+(PASSED|FAILED|SKIPPED|ERROR)\s+')
        for test_name, status in pattern.findall(log):
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ('FAILED', 'ERROR'):
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
