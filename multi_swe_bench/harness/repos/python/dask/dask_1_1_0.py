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
        return "python:3.7-buster"
    
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
                """ls -la
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3-pip python3-dev build-essential git
###ACTION_DELIMITER###
pip3 install numpy pandas toolz cloudpickle partd distributed bcolz blosc bokeh boto3 botocore httpretty chest coverage cytoolz graphviz h5py ipython lz4 numba psutil tables requests scikit-image scikit-learn scipy sqlalchemy pytest pytest-xdist flake8 locket git+https://github.com/dask/partd git+https://github.com/dask/zict git+https://github.com/dask/distributed git+https://github.com/pydata/sparse git+https://github.com/dask/s3fs cachey graphviz pandas_datareader cityhash mmh3 xxhash moto
###ACTION_DELIMITER###
pip3 install --upgrade pip setuptools wheel
###ACTION_DELIMITER###
pip3 install 'setuptools_scm<8.0.0'
###ACTION_DELIMITER###
pip3 install numpy pandas toolz cloudpickle partd distributed bcolz blosc bokeh boto3 botocore httpretty chest coverage cytoolz graphviz h5py ipython lz4 numba psutil tables requests scikit-image scikit-learn scipy sqlalchemy pytest pytest-xdist flake8 locket git+https://github.com/dask/partd git+https://github.com/dask/zict git+https://github.com/dask/distributed git+https://github.com/pydata/sparse git+https://github.com/dask/s3fs cachey graphviz pandas_datareader cityhash mmh3 xxhash moto
###ACTION_DELIMITER###
pip3 install numpy pandas toolz cloudpickle partd distributed bcolz blosc bokeh boto3 botocore httpretty chest coverage cytoolz graphviz h5py ipython lz4 numba psutil tables requests scikit-image scikit-learn scipy sqlalchemy pytest pytest-xdist flake8 locket git+https://github.com/dask/partd git+https://github.com/dask/zict git+https://github.com/dask/distributed git+https://github.com/dask/s3fs cachey graphviz pandas_datareader cityhash mmh3 xxhash moto
###ACTION_DELIMITER###
apt-get install -y libatlas-base-dev libopenblas-dev liblapack-dev gfortran libhdf5-dev python3-h5py
###ACTION_DELIMITER###
pip3 install numpy pandas toolz cloudpickle partd distributed blosc bokeh boto3 botocore httpretty chest coverage cytoolz graphviz h5py ipython lz4 numba psutil tables requests scikit-image scikit-learn scipy sqlalchemy pytest pytest-xdist flake8 locket git+https://github.com/dask/partd git+https://github.com/dask/zict git+https://github.com/dask/distributed git+https://github.com/dask/s3fs cachey graphviz pandas_datareader cityhash mmh3 xxhash moto
###ACTION_DELIMITER###
pip3 install pandas==1.1.5
###ACTION_DELIMITER###
pip3 install toolz cloudpickle partd distributed blosc bokeh boto3 botocore httpretty chest coverage cytoolz graphviz h5py ipython lz4 numba psutil tables requests scikit-image scikit-learn scipy sqlalchemy pytest pytest-xdist flake8 locket git+https://github.com/dask/partd git+https://github.com/dask/zict git+https://github.com/dask/distributed git+https://github.com/dask/s3fs cachey graphviz pandas_datareader cityhash mmh3 xxhash moto
###ACTION_DELIMITER###
pip3 install partd==1.2.0
###ACTION_DELIMITER###
pip3 install cloudpickle distributed blosc bokeh boto3 botocore httpretty chest coverage cytoolz graphviz h5py ipython lz4 numba psutil tables requests scikit-image scikit-learn scipy sqlalchemy pytest pytest-xdist flake8 git+https://github.com/dask/partd git+https://github.com/dask/zict git+https://github.com/dask/distributed git+https://github.com/dask/s3fs cachey graphviz pandas_datareader cityhash mmh3 xxhash moto
###ACTION_DELIMITER###
pip3 install distributed==2022.2.0 cloudpickle==2.2.1
###ACTION_DELIMITER###
pip3 install blosc bokeh boto3 botocore httpretty chest coverage cytoolz graphviz h5py ipython lz4 numba psutil tables requests scikit-image scikit-learn scipy sqlalchemy pytest pytest-xdist flake8 git+https://github.com/dask/partd git+https://github.com/dask/zict git+https://github.com/dask/s3fs cachey graphviz pandas_datareader cityhash mmh3 xxhash moto
###ACTION_DELIMITER###
pip3 install httpretty==1.0.2
###ACTION_DELIMITER###
pip3 install blosc bokeh boto3 botocore chest coverage cytoolz graphviz h5py ipython lz4 numba psutil tables requests scikit-image scikit-learn scipy sqlalchemy pytest pytest-xdist flake8 git+https://github.com/dask/partd git+https://github.com/dask/zict git+https://github.com/dask/s3fs cachey graphviz pandas_datareader cityhash mmh3 xxhash moto
###ACTION_DELIMITER###
pip3 install blosc bokeh boto3 botocore chest coverage cytoolz graphviz h5py ipython lz4 numba psutil tables requests scikit-image scikit-learn scipy sqlalchemy pytest pytest-xdist flake8 cachey graphviz pandas_datareader cityhash mmh3 xxhash moto
###ACTION_DELIMITER###
echo 'pytest --no-header -rA --tb=no -p no:cacheprovider --runslow dask' > /home/dask/test_commands.sh && chmod +x /home/dask/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest --no-header -rA --tb=no -p no:cacheprovider --runslow dask

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
pytest --no-header -rA --tb=no -p no:cacheprovider --runslow dask

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
pytest --no-header -rA --tb=no -p no:cacheprovider --runslow dask

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
FROM python:3.7-buster

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
RUN git clone https://github.com/dask/dask.git /home/dask

WORKDIR /home/dask
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("dask", "dask_1_1_0")
class DASK_1_1_0(Instance):
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
        import json
        # Regex patterns for test results
        passed_pattern = re.compile(r"^PASSED ([^\s]+::[^\s]+)", re.MULTILINE)
        failed_pattern = re.compile(r"^FAILED ([^\s]+::[^\s]+)", re.MULTILINE)
        skipped_pattern = re.compile(r"^SKIPPED \[\d+\] ([^:]+:\d+):", re.MULTILINE)
        xfail_pattern = re.compile(r"^XFAIL ([^\s]+::[^\s]+)", re.MULTILINE)
        xpass_pattern = re.compile(r"^XPASS ([^\s]+::[^\s]+)", re.MULTILINE)
        # Find all matches
        passed_tests.update(passed_pattern.findall(log))
        failed_tests.update(failed_pattern.findall(log))
        failed_tests.update(xfail_pattern.findall(log))  # Treat XFAIL as failed
        passed_tests.update(xpass_pattern.findall(log))  # Treat XPASS as passed
        skipped_tests.update(skipped_pattern.findall(log))
        # TODO: Implement the parse_log function
        # Implement the log parsing logic here
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
