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
        return "python:3.8-slim"
    
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
python3 --version
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
pip install pytest pytest-xdist moto h5py tables zarr tiledb fsspec sqlalchemy pyarrow coverage bcolz blosc boto3 botocore bokeh httpretty chest s3fs cloudpickle crick cytoolz distributed graphviz ipython lz4 partd psutil requests scikit-image scikit-learn scipy toolz python-snappy cachey python-graphviz pandas-datareader cityhash mmh3 xxhash
###ACTION_DELIMITER###
pip install .[complete]
###ACTION_DELIMITER###
pip install cityhash mmh3 xxhash
###ACTION_DELIMITER###
echo 'pytest --no-header -rA --tb=no -p no:cacheprovider dask --runslow' > /home/dask/test_commands.sh
###ACTION_DELIMITER###
bash /home/dask/test_commands.sh
###ACTION_DELIMITER###
which pytest
###ACTION_DELIMITER###
pip show pytest
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
which pytest
###ACTION_DELIMITER###
echo -e 'export PATH="/usr/local/bin:$PATH"
pytest --no-header -rA --tb=no -p no:cacheprovider dask --runslow' > /home/dask/test_commands.sh
###ACTION_DELIMITER###
bash /home/dask/test_commands.sh
###ACTION_DELIMITER###
pip install 'numpy<1.24'
###ACTION_DELIMITER###
bash /home/dask/test_commands.sh
###ACTION_DELIMITER###
pip install 'pandas<2.0'
###ACTION_DELIMITER###
bash /home/dask/test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PATH="/usr/local/bin:$PATH"
pytest -W ignore::DeprecationWarning --no-header -rA --tb=no -p no:cacheprovider dask --runslow' > /home/dask/test_commands.sh
###ACTION_DELIMITER###
bash /home/dask/test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PATH="/usr/local/bin:$PATH"
pytest -W ignore --no-header -rA --tb=no -p no:cacheprovider dask --runslow' > /home/dask/test_commands.sh
###ACTION_DELIMITER###
bash /home/dask/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
export PATH="/usr/local/bin:$PATH"
pytest -W ignore --no-header -rA --tb=no -p no:cacheprovider dask --runslow

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
export PATH="/usr/local/bin:$PATH"
pytest -W ignore --no-header -rA --tb=no -p no:cacheprovider dask --runslow

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
export PATH="/usr/local/bin:$PATH"
pytest -W ignore --no-header -rA --tb=no -p no:cacheprovider dask --runslow

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
FROM python:3.8-slim

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


@Instance.register("dask", "dask_2_10_1")
class DASK_2_10_1(Instance):
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
        pass_pattern = re.compile(r"^PASSED ([^\s]+::[^\s]+)", re.MULTILINE)
        fail_pattern = re.compile(r"^FAILED ([^\s]+::[^\s]+)", re.MULTILINE)
        skip_pattern = re.compile(r"^SKIPPED \[\d+\] ([^:]+):\d+:", re.MULTILINE)
        # XFAIL and XPASS are not counted as failed/passed/skipped per requirements
        passed_tests.update(pass_pattern.findall(log))
        failed_tests.update(fail_pattern.findall(log))
        skipped_tests.update(skip_pattern.findall(log))
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
