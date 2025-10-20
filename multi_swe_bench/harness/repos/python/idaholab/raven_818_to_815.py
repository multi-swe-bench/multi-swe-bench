from typing import Dict, Set

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
                """ls -la
###ACTION_DELIMITER###
git submodule status
###ACTION_DELIMITER###
git submodule update --init --recursive
###ACTION_DELIMITER###
git submodule update --init moose
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential g++ python3-dev libboost-all-dev
###ACTION_DELIMITER###
make
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2.7
###ACTION_DELIMITER###
apt-get update && apt-get install -y swig
###ACTION_DELIMITER###
sed -i '17s/$/.decode(\'utf-8\')/' crow/setup.py
###ACTION_DELIMITER###
sed -i '17s/$/.decode("utf-8")/' crow/setup.py
###ACTION_DELIMITER###
make
###ACTION_DELIMITER###
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && bash miniconda.sh -b -p /root/miniconda3 && rm miniconda.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && bash miniconda.sh -b -p /root/miniconda3 && rm miniconda.sh
###ACTION_DELIMITER###
source /root/miniconda3/etc/profile.d/conda.sh
###ACTION_DELIMITER###
./scripts/establish_conda_env.sh --create
###ACTION_DELIMITER###
./scripts/establish_conda_env.sh --create --conda-defs /root/miniconda3/etc/profile.d/conda.sh
###ACTION_DELIMITER###
./scripts/establish_conda_env.sh --install --conda-defs /root/miniconda3/etc/profile.d/conda.sh
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
###ACTION_DELIMITER###
./scripts/establish_conda_env.sh --install --conda-defs /root/miniconda3/etc/profile.d/conda.sh
###ACTION_DELIMITER###
conda create --name raven_libraries -y h5py=2.7.1 numpy=1.12.1 scipy=1.1.0 scikit-learn=0.19.1 pandas=0.20.3 xarray=0.10.3 netcdf4=1.4.0 matplotlib=2.1.1 statsmodels=0.8.0 python=2.7 hdf5=1.8.18 swig pylint coverage lxml psutil numexpr
###ACTION_DELIMITER###
conda activate raven_libraries
###ACTION_DELIMITER###
make
###ACTION_DELIMITER###
ln -s /root/miniconda3 /root/miniconda2
###ACTION_DELIMITER###
make
###ACTION_DELIMITER###
./run_tests --verbose
###ACTION_DELIMITER###
./run_tests -h
###ACTION_DELIMITER###
./run_tests
###ACTION_DELIMITER###
echo './run_tests -j 4' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
./run_tests -j 4

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
./run_tests -j 4

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
./run_tests -j 4

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
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Ensure bash is available
RUN if [ ! -f /bin/bash ]; then         if command -v apk >/dev/null 2>&1; then             apk add --no-cache bash;         elif command -v apt-get >/dev/null 2>&1; then             apt-get update && apt-get install -y bash;         elif command -v yum >/dev/null 2>&1; then             yum install -y bash;         else             exit 1;         fi     fi

WORKDIR /home/
COPY fix.patch /home/
COPY test.patch /home/
RUN git clone https://github.com/idaholab/raven.git /home/raven

WORKDIR /home/raven
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("idaholab", "raven_818_to_815")
class RAVEN_818_TO_815(Instance):
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
        passed_tests: Set[str] = set()  # Tests that passed successfully
        failed_tests: Set[str] = set()  # Tests that failed
        skipped_tests: Set[str] = set()  # Tests that were skipped
        try:
            import re
            # Parse passed tests
            passed_pattern = re.compile(r"\(\d+/\d+\) Success \([^)]*\) (.*)")
            passed_tests.update([test.strip() for test in passed_pattern.findall(log) if test.strip()])
            # Parse skipped tests
            skipped_pattern = re.compile(r"\(\d+/\d+\) Skipped \([^)]*\) (.*)")
            skipped_tests.update([test.strip() for test in skipped_pattern.findall(log) if test.strip()])
            # Parse failed tests
            failed_pattern = re.compile(r'FAILED:')
            summary_pattern = re.compile(r'PASSED:\s*\d+\s*FAILED:\s*\d+\s*SKIPPED\s*\d+', re.IGNORECASE)
            lines = log.splitlines()
            failed_start = None
            for i, line in enumerate(lines):
                if failed_pattern.search(line):
                    failed_start = i + 1
                    break
            if failed_start is not None:
                for line in lines[failed_start:]:
                    line = line.strip()
                    if not line:
                        continue
                    if summary_pattern.search(line):
                        break
                    test_name = re.sub(r'^\[\s*\d+\s*\]\s*', '', line)
                    if test_name:
                        failed_tests.add(test_name.strip())
            # Debug print to verify failed tests count
            print(f"Debug: Failed tests captured: {len(failed_tests)}")
        except Exception as e:
            print(f"Parsing error: {str(e)}", file=sys.stderr)
            raise  # Re-raise to show full traceback
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
