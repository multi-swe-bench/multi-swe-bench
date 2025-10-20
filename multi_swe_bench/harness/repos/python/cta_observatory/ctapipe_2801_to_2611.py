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
cat Makefile
###ACTION_DELIMITER###
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
###ACTION_DELIMITER###
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda
###ACTION_DELIMITER###
source $HOME/miniconda/etc/profile.d/conda.sh
###ACTION_DELIMITER###
conda env create -f environment.yml
###ACTION_DELIMITER###
conda install -y -c conda-forge mamba
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
###ACTION_DELIMITER###
conda install -y -c conda-forge mamba
###ACTION_DELIMITER###
mamba env create -f environment.yml
###ACTION_DELIMITER###
cat README.rst
###ACTION_DELIMITER###
mamba create -y -n cta-dev -c conda-forge ctapipe
###ACTION_DELIMITER###
mamba activate cta-dev
###ACTION_DELIMITER###
eval "$(mamba shell hook --shell bash)"
###ACTION_DELIMITER###
mamba activate cta-dev
###ACTION_DELIMITER###
echo 'pytest --verbose --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
mamba install -y -n cta-dev -c conda-forge pytest
###ACTION_DELIMITER###
echo 'mamba run -n cta-dev pytest --verbose --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
mamba install -y -n cta-dev -c conda-forge pytest-astropy-header
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
mamba run -n cta-dev pip install -e .
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
mamba install -y -n cta-dev -c conda-forge h5py
###ACTION_DELIMITER###
mamba run -n cta-dev pip install -e ./test_plugin
###ACTION_DELIMITER###
mamba install -y -n cta-dev -c conda-forge astroquery
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
mamba run -n cta-dev pytest --verbose --no-header -rA --tb=no -p no:cacheprovider

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
mamba run -n cta-dev pytest --verbose --no-header -rA --tb=no -p no:cacheprovider

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
mamba run -n cta-dev pytest --verbose --no-header -rA --tb=no -p no:cacheprovider

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
RUN git clone https://github.com/cta-observatory/ctapipe.git /home/ctapipe

WORKDIR /home/ctapipe
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("cta-observatory", "ctapipe_2801_to_2611")
class CTAPIPE_2801_TO_2611(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        # Regex patterns to match test lines
        pattern1 = re.compile(r'(src/.*?\.py::test_\w+(?:\[[^\]]+\])?)\s+(PASSED|FAILED|SKIPPED|XFAIL)\s*\[\s*\d+%\s*\]')
        pattern2 = re.compile(r'(PASSED|FAILED|SKIPPED|XFAIL)\s+(src/.*?\.py::test_\w+(?:\[[^\]]+\])?)')
        pattern3 = re.compile(r'SKIPPED\s+\[\d+\]\s+(src/.*?\.py):\d+.*?\((test_\w+(?:\[[^\]]+\])?)\)')
        test_status = {}
        for line in log.split('\n'):
            line = line.strip()
            match = pattern1.search(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
                test_status[test_name] = status
                continue
            match = pattern2.search(line)
            if match:
                status = match.group(1)
                test_name = match.group(2)
                test_status[test_name] = status
                continue
            match = pattern3.search(line)
            if match:
                file_path = match.group(1)
                test_func = match.group(2)
                test_name = f'{file_path}::{test_func}'
                test_status[test_name] = 'SKIPPED'
                continue
        # Populate sets based on the latest status
        for test, status in test_status.items():
            if status == 'PASSED':
                passed_tests.add(test)
            elif status == 'FAILED':
                failed_tests.add(test)
            elif status == 'SKIPPED':
                skipped_tests.add(test)
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
