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
        return "python:3.6-buster"
    
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
                """ls -al
###ACTION_DELIMITER###
ls -al continuous_integration
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential python3-dev python3-pip libhdf5-dev libsnappy-dev libzstd-dev liblz4-dev libblosc-dev graphviz
###ACTION_DELIMITER###
pip3 install -e .[complete] pytest pytest-xdist flake8 bcolz blosc bokeh boto3 h5py scikit-learn cytoolz partd cloudpickle coverage requests sqlalchemy lz4 psutil tables scikit-image pandas_datareader graphviz moto cityhash mmh3 xxhash
###ACTION_DELIMITER###
pip3 install Cython && pip3 install bcolz==1.2.1
###ACTION_DELIMITER###
pip3 install blosc bokeh boto3 h5py scikit-learn cytoolz partd cloudpickle coverage requests sqlalchemy lz4 psutil tables scikit-image pandas_datareader graphviz moto cityhash mmh3 xxhash
###ACTION_DELIMITER###
echo 'pytest dask --runslow -v -n 3' > /home/dask/test_commands.sh && chmod +x /home/dask/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest dask --runslow -v -n 3

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
pytest dask --runslow -v -n 3

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
pytest dask --runslow -v -n 3

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
FROM python:3.6-buster

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


@Instance.register("dask", "dask_0_18_2")
class DASK_0_18_2(Instance):
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

        # Improved parser: track the latest status for each test, handle reruns and xfail/xpass.
        from collections import OrderedDict
        import re
        # Regex to match lines like:
        # [gw0] [  0%] PASSED dask/array/tests/test_array_core.py::test_getem
        # Also match XPASS, XFAIL, etc.
        pattern = re.compile(r"\[gw\d+\] \[ *\d+%\] (PASSED|FAILED|SKIPPED|XPASS|XFAIL|XPASS\(strict\)|XFAIL\(strict\)) ([^\s]+::[^\s]+)")
        test_status = OrderedDict()  # test_name -> status (last one wins)
        for match in pattern.finditer(log):
            status, test_name = match.groups()
            test_status[test_name] = status
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        for test_name, status in test_status.items():
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status == "FAILED" or status.startswith("XPASS"):
                # XPASS is considered a failure (unexpected pass)
                failed_tests.add(test_name)
            elif status == "SKIPPED" or status.startswith("XFAIL"):
                # XFAIL is considered skipped/expected fail
                skipped_tests.add(test_name)
        # Ensure no test is in more than one set
        passed_tests -= (failed_tests | skipped_tests)
        failed_tests -= (passed_tests | skipped_tests)
        skipped_tests -= (passed_tests | failed_tests)
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
