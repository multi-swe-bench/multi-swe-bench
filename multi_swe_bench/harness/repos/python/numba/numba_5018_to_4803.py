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
cat requirements.txt
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
python runtests.py --help
###ACTION_DELIMITER###
python setup.py build_ext --inplace
###ACTION_DELIMITER###
apt-get update && apt-get install -y gcc
###ACTION_DELIMITER###
python setup.py build_ext --inplace
###ACTION_DELIMITER###
apt-get install -y g++
###ACTION_DELIMITER###
python setup.py build_ext --inplace
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install numpy==1.21.6
###ACTION_DELIMITER###
python setup.py build_ext --inplace
###ACTION_DELIMITER###
python runtests.py --help
###ACTION_DELIMITER###
pip uninstall -y llvmlite && pip install llvmlite==0.31.0
###ACTION_DELIMITER###
apt-get install -y llvm-8-dev
###ACTION_DELIMITER###
apt-get install -y llvm-dev
###ACTION_DELIMITER###
LLVM_CONFIG=$(which llvm-config) pip install llvmlite==0.31.0
###ACTION_DELIMITER###
pip install llvmlite==0.40.0
###ACTION_DELIMITER###
python runtests.py --help
###ACTION_DELIMITER###
apt-get update && apt-get install -y llvm-7-dev
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian buster main' >> /etc/apt/sources.list && apt-get update && apt-get install -y llvm-8-dev
###ACTION_DELIMITER###
wget https://releases.llvm.org/8.0.1/clang+llvm-8.0.1-x86_64-linux-gnu-ubuntu-18.04.tar.xz && tar -xf clang+llvm-8.0.1-x86_64-linux-gnu-ubuntu-18.04.tar.xz && export LLVM_CONFIG=$(pwd)/clang+llvm-8.0.1-x86_64-linux-gnu-ubuntu-18.04/bin/llvm-config && pip install llvmlite==0.31.0
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget https://releases.llvm.org/8.0.1/clang+llvm-8.0.1-x86_64-linux-gnu-ubuntu-18.04.tar.xz && tar -xf clang+llvm-8.0.1-x86_64-linux-gnu-ubuntu-18.04.tar.xz && export LLVM_CONFIG=$(pwd)/clang+llvm-8.0.1-x86_64-linux-gnu-ubuntu-18.04/bin/llvm-config && pip install llvmlite==0.31.0
###ACTION_DELIMITER###
wget https://github.com/llvm/llvm-project/releases/download/llvmorg-8.0.1/clang+llvm-8.0.1-x86_64-linux-gnu-ubuntu-18.04.tar.xz && tar -xf clang+llvm-8.0.1-x86_64-linux-gnu-ubuntu-18.04.tar.xz && export LLVM_CONFIG=$(pwd)/clang+llvm-8.0.1-x86_64-linux-gnu-ubuntu-18.04/bin/llvm-config && pip install llvmlite==0.31.0
###ACTION_DELIMITER###
wget https://releases.llvm.org/8.0.1/clang+llvm-8.0.1-x86_64-linux-gnu.tar.xz && tar -xf clang+llvm-8.0.1-x86_64-linux-gnu.tar.xz && export LLVM_CONFIG=$(pwd)/clang+llvm-8.0.1-x86_64-linux-gnu/bin/llvm-config && pip install llvmlite==0.31.0
###ACTION_DELIMITER###
echo 'deb [trusted=yes] http://deb.debian.org/debian buster main' >> /etc/apt/sources.list && apt-get update && apt-get install -y llvm-8-dev && export LLVM_CONFIG=/usr/bin/llvm-config-8 && pip install llvmlite==0.31.0
###ACTION_DELIMITER###
sed -i '/buster/d' /etc/apt/sources.list && echo 'deb [trusted=yes] http://deb.debian.org/debian buster main' >> /etc/apt/sources.list && apt-get update && apt-get install -y llvm-8-dev && export LLVM_CONFIG=/usr/bin/llvm-config-8 && pip install llvmlite==0.31.0
###ACTION_DELIMITER###
sed -i '/buster/d' /etc/apt/sources.list && echo 'deb [trusted=yes] http://archive.debian.org/debian buster main' >> /etc/apt/sources.list && apt-get update && apt-get install -y llvm-8-dev && export LLVM_CONFIG=/usr/bin/llvm-config-8 && pip install llvmlite==0.31.0
###ACTION_DELIMITER###
sed -i '/buster/d' /etc/apt/sources.list && echo 'deb [trusted=yes] http://archive.debian.org/debian buster main' >> /etc/apt/sources.list && apt-get update && apt-get install -y llvm-7-dev && export LLVM_CONFIG=/usr/bin/llvm-config-7 && pip install llvmlite==0.31.0
###ACTION_DELIMITER###
apt-get install -y make && export LLVM_CONFIG=/usr/bin/llvm-config-7 && pip install llvmlite==0.31.0
###ACTION_DELIMITER###
python runtests.py --help
###ACTION_DELIMITER###
echo 'python runtests.py -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'python runtests.py -v -m 4' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'python runtests.py -v -m auto' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'python runtests.py -v -m 4' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'python runtests.py -v -m 4 --exclude-tags cuda,hsa' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python runtests.py -v -m 4 --exclude-tags cuda,hsa

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
python runtests.py -v -m 4 --exclude-tags cuda,hsa

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
python runtests.py -v -m 4 --exclude-tags cuda,hsa

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
RUN git clone https://github.com/numba/numba.git /home/numba

WORKDIR /home/numba
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("numba", "numba_5018_to_4803")
class NUMBA_5018_TO_4803(Instance):
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
        # Regex pattern to match test lines with line numbers
        pattern = re.compile(r'^\s*(\w+)\s*\((.*?)\)\s*\.\.\.\s*(\w+)\s*$', re.MULTILINE)
        # Extract test information from log
        for match in pattern.finditer(log):
            test_method, class_path, status = match.groups()
            test_name = f"{class_path}.{test_method}"
            if status == 'ok':
                passed_tests.add(test_name)
            elif status in ('ERROR', 'FAILED'):
                failed_tests.add(test_name)
            elif status == 'skipped':
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
