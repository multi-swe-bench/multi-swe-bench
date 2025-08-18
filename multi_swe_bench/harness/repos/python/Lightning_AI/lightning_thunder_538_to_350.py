from typing import Optional

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
pip install -r requirements/devel.txt
###ACTION_DELIMITER###
pip install --pre 'nvfuser-cu121[torch]' --extra-index-url https://pypi.nvidia.com
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
wget https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/cuda-keyring_1.1-1_all.deb && dpkg -i cuda-keyring_1.1-1_all.deb
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
wget https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/cuda-keyring_1.1-1_all.deb && dpkg -i cuda-keyring_1.1-1_all.deb
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y cuda-12-1
###ACTION_DELIMITER###
apt-cache search cuda
###ACTION_DELIMITER###
apt-get install -y cuda-12-3
###ACTION_DELIMITER###
pip install --pre 'nvfuser-cu123[torch]' --extra-index-url https://pypi.nvidia.com
###ACTION_DELIMITER###
pip install --pre 'nvfuser-cu121[torch]' --extra-index-url https://pypi.nvidia.com
###ACTION_DELIMITER###
pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cu121
###ACTION_DELIMITER###
apt-get install -y python3.10 python3.10-pip && python3.10 -m pip install --pre 'nvfuser-cu121[torch]' --extra-index-url https://pypi.nvidia.com
###ACTION_DELIMITER###
apt-get install -y nvidia-utils-575
###ACTION_DELIMITER###
apt-cache search nvidia-utils
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.10
###ACTION_DELIMITER###
apt-get install -y python3.10-venv
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python3.10 -t bullseye-backports
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bookworm-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python3.10 -t bookworm-backports
###ACTION_DELIMITER###
sed -i '/bullseye-backports/d' /etc/apt/sources.list && echo 'deb http://deb.debian.org/debian bookworm-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python3.10 -t bookworm-backports
###ACTION_DELIMITER###
apt-get install -y python3.10 python3.10-pip -t bookworm-backports
###ACTION_DELIMITER###
apt-get install -y python3.10 && python3.10 -m ensurepip --upgrade
###ACTION_DELIMITER###
apt-cache search python3.10
###ACTION_DELIMITER###
apt-get install -y python3.11 python3.11-venv && python3.11 -m venv venv && source venv/bin/activate && pip install --upgrade pip
###ACTION_DELIMITER###
pip install -r requirements/devel.txt
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider thunder/tests' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install nvidia-cudnn-frontend
###ACTION_DELIMITER###
apt-get install -y libcudnn8 libcudnn8-dev && bash test_commands.sh
###ACTION_DELIMITER###
pip install --pre 'nvfuser-cu123[torch]' --extra-index-url https://pypi.nvidia.com && bash test_commands.sh
###ACTION_DELIMITER###
export CUDA_HOME=/usr/local/cuda-12.3 && export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH && bash test_commands.sh
###ACTION_DELIMITER###
pip install torch --index-url https://download.pytorch.org/whl/cu123 && python -c 'import torch; print("CUDA available: ", torch.cuda.is_available())' && bash test_commands.sh
###ACTION_DELIMITER###
pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cu123 && bash test_commands.sh
###ACTION_DELIMITER###
python -c 'import torch; print("CUDA available: ", torch.cuda.is_available())' && export LD_LIBRARY_PATH=/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64 && bash test_commands.sh
###ACTION_DELIMITER###
export LD_LIBRARY_PATH=/usr/local/cuda-12.3/lib64:/usr/local/cuda-12.3/extras/CUPTI/lib64 && pip install --force-reinstall torch --index-url https://download.pytorch.org/whl/cu123 && python -c 'import torch; print("CUDA available: ", torch.cuda.is_available())' && bash test_commands.sh
###ACTION_DELIMITER###
export LD_LIBRARY_PATH=/usr/local/cuda-12.3/lib64:/usr/local/cuda-12.3/extras/CUPTI/lib64 && pip install --force-reinstall torch --index-url https://download.pytorch.org/whl/cu121 && python -c 'import torch; print("CUDA available: ", torch.cuda.is_available())' && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v --no-header -rA --tb=no -p no:cacheprovider thunder/tests

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider thunder/tests

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider thunder/tests

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
RUN git clone https://github.com/Lightning-AI/lightning-thunder.git /home/lightning-thunder

WORKDIR /home/lightning-thunder
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Lightning-AI", "lightning_thunder_538_to_350")
class LIGHTNING_THUNDER_538_TO_350(Instance):
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
        # Remove ANSI escape codes
        clean_log = re.sub(r'\x1b\[[0-9;]*m', '', log)
        lines = clean_log.splitlines()
        # Define regex patterns
        pattern1 = re.compile(r'(?:\[\s*\d+\] )?\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] (.*?) (PASSED|SKIPPED|FAILED) \[\s*\d+%\](?:.*)')
        pattern2 = re.compile(r'\[\s*\d+\] (PASSED|FAILED) (.*?) (?:- |$)')
        for line in lines:
            line = line.strip()
            # Check pattern1 (timestamp lines)
            match = pattern1.match(line)
            if match:
                test_name = match.group(1).strip()
                status = match.group(2)
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
                continue
            # Check pattern2 (status first lines)
            match = pattern2.match(line)
            if match:
                status = match.group(1)
                test_name = match.group(2).strip()
                # Ensure test name contains '::' to avoid false positives
                if '::' in test_name:
                    if status == 'PASSED':
                        passed_tests.add(test_name)
                    elif status == 'FAILED':
                        failed_tests.add(test_name)
                continue
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
