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
apt-get update
###ACTION_DELIMITER###
apt-get install -y build-essential libhdf5-dev hdf5-tools wget
###ACTION_DELIMITER###
export HDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/serial/ && pip install -r test_requirements.txt
###ACTION_DELIMITER###
pip install numpy
###ACTION_DELIMITER###
export HDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/serial/ && pip install -r test_requirements.txt
###ACTION_DELIMITER###
export CFLAGS="-I/usr/local/lib/python3.9/site-packages/numpy/core/include" && export HDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/serial/ && pip install -r test_requirements.txt
###ACTION_DELIMITER###
pip install numpy==1.16.6
###ACTION_DELIMITER###
export CFLAGS="-I/usr/local/lib/python3.9/site-packages/numpy/core/include" && export HDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/serial/ && pip install pandas==0.24.2 && pip install -r test_requirements.txt
###ACTION_DELIMITER###
pip install cython && export CFLAGS="-I/usr/local/lib/python3.9/site-packages/numpy/core/include" && export HDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/serial/ && pip install pandas==0.24.2 && pip install -r test_requirements.txt
###ACTION_DELIMITER###
pip install cython==0.29.24 && export CFLAGS="-I/usr/local/lib/python3.9/site-packages/numpy/core/include" && export HDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/serial/ && pip install pandas==0.24.2 && pip install -r test_requirements.txt
###ACTION_DELIMITER###
apt-get install -y cmake && pip install cython==0.29.24 && export CFLAGS="-I/usr/local/lib/python3.9/site-packages/numpy/core/include" && export HDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/serial/ && pip install pandas==0.24.2 && pip install -r test_requirements.txt
###ACTION_DELIMITER###
apt-get install -y wget && wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && bash miniconda.sh -b -p /opt/miniconda && rm miniconda.sh && /opt/miniconda/bin/conda create -y -n py37 python=3.7 && /opt/miniconda/bin/conda init bash && source ~/.bashrc && conda activate py37 && pip install numpy==1.16.6 cython==0.29.24 && export CFLAGS="-I/opt/miniconda/envs/py37/lib/python3.7/site-packages/numpy/core/include" && export HDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/serial/ && pip install pandas==0.24.2 && pip install -r test_requirements.txt
###ACTION_DELIMITER###
/opt/miniconda/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main --channel https://repo.anaconda.com/pkgs/r && /opt/miniconda/bin/conda create -y -n py37 python=3.7 && source /opt/miniconda/bin/activate py37 && pip install numpy==1.16.6 cython==0.29.24 && export CFLAGS="-I/opt/miniconda/envs/py37/lib/python3.7/site-packages/numpy/core/include" && export HDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/serial/ && pip install pandas==0.24.2 && pip install -r test_requirements.txt
###ACTION_DELIMITER###
echo 'pytest -v -rA --tb=short -p no:cacheprovider tests
behave' > /home/kedro/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v -rA --tb=short -p no:cacheprovider tests
behave

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
pytest -v -rA --tb=short -p no:cacheprovider tests
behave

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
pytest -v -rA --tb=short -p no:cacheprovider tests
behave

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
RUN git clone https://github.com/kedro-org/kedro.git /home/kedro

WORKDIR /home/kedro
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("kedro-org", "kedro_20_to_unknown")
class KEDRO_20_TO_UNKNOWN(Instance):
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
        pattern = re.compile(r'(tests/.*?\.py::.*?)\s+(PASSED|FAILED|SKIPPED)')
        matches = pattern.findall(log)
        for test_name, status in matches:
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
