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
                """ls -al
###ACTION_DELIMITER###

###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip python3-dev build-essential
###ACTION_DELIMITER###
pip3 install -e .[complete] pytest pytest-xdist flake8 coverage bcolz blosc bokeh boto3 chest h5py lz4 partd psutil tables requests scikit-image scikit-learn sqlalchemy cityhash mmh3 xxhash moto
###ACTION_DELIMITER###
pip3 install --upgrade pip cython numpy
###ACTION_DELIMITER###
pip3 install bcolz blosc bokeh boto3 chest h5py lz4 partd psutil tables requests scikit-image scikit-learn sqlalchemy cityhash mmh3 xxhash moto
###ACTION_DELIMITER###
echo 'pytest dask --runslow -v --tb=short' > /home/dask/test_commands.sh && chmod +x /home/dask/test_commands.sh
###ACTION_DELIMITER###
bash /home/dask/test_commands.sh
###ACTION_DELIMITER###
pip3 show pytest
###ACTION_DELIMITER###
pip3 install pytest pytest-xdist
###ACTION_DELIMITER###
bash /home/dask/test_commands.sh
###ACTION_DELIMITER###
pip3 install pandas dask[dataframe] dask[array] dask[bag] dask[distributed]
###ACTION_DELIMITER###
bash /home/dask/test_commands.sh
###ACTION_DELIMITER###
pip3 install 'pytest<=3.1.1'
###ACTION_DELIMITER###
bash /home/dask/test_commands.sh
###ACTION_DELIMITER###
pip3 uninstall -y pytest-xdist
###ACTION_DELIMITER###
bash /home/dask/test_commands.sh
###ACTION_DELIMITER###
pip3 install 'PyYAML==5.1'
###ACTION_DELIMITER###
pip3 install 'PyYAML==5.1' --only-binary :all:
###ACTION_DELIMITER###
pip3 install Cython
###ACTION_DELIMITER###
pip3 install wheel
###ACTION_DELIMITER###
pip3 install 'PyYAML==5.1'
###ACTION_DELIMITER###
pip3 install 'setuptools==57.5.0'
###ACTION_DELIMITER###
pip3 install 'PyYAML==5.4.1'
###ACTION_DELIMITER###
bash /home/dask/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest dask --runslow -v --tb=short

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
pytest dask --runslow -v --tb=short

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
pytest dask --runslow -v --tb=short

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


@Instance.register("dask", "dask_0_19_4")
class DASK_0_19_4(Instance):
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
        # Regular expression to match test result lines
        # Example: dask/array/tests/test_array_core.py::test_getem PASSED
        test_line_re = re.compile(r"^(.*?)::(.*?) (PASSED|FAILED|SKIPPED|XPASS|xfailed|xpassed|xfail)", re.MULTILINE)
        for match in test_line_re.finditer(log):
            test_path = match.group(1)
            test_name = match.group(2)
            status = match.group(3).upper()
            full_test_name = f"{test_path}::{test_name}"
            if status == "PASSED":
                passed_tests.add(full_test_name)
            elif status == "FAILED":
                failed_tests.add(full_test_name)
            elif status == "SKIPPED":
                skipped_tests.add(full_test_name)
            elif status == "XFAIL":
                skipped_tests.add(full_test_name)
            elif status == "XPASS":
                failed_tests.add(full_test_name)
            elif status == "XFAILED":
                skipped_tests.add(full_test_name)
            elif status == "XPASSED":
                failed_tests.add(full_test_name)
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
