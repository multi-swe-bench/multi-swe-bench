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
pip install numpy scipy scikit-learn nibabel nose coverage matplotlib
###ACTION_DELIMITER###
make inplace
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make inplace
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
pip install scikit-learn==0.23.2 matplotlib==3.3.4
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libopenblas-dev
###ACTION_DELIMITER###
pip install scikit-learn==0.23.2 matplotlib==3.3.4
###ACTION_DELIMITER###
pip install setuptools==44.0.0
###ACTION_DELIMITER###
pip install scikit-learn==0.23.2 matplotlib==3.3.4
###ACTION_DELIMITER###
pip install numpy==1.19.5
###ACTION_DELIMITER###
pip install numpy==1.19.5 scipy==1.5.4 scikit-learn==0.23.2 nibabel==3.2.1 matplotlib==3.3.4 nose==1.3.7 coverage==5.5
###ACTION_DELIMITER###
pip install numpy==1.11.0 scipy==0.17.0 scikit-learn==0.15.2 nibabel==2.0.2 matplotlib==1.5.3 nose==1.3.7 coverage==4.0.3
###ACTION_DELIMITER###
apt-get update && apt-get install -y libfreetype6-dev libpng-dev
###ACTION_DELIMITER###
pip install numpy==1.19.5 scipy==1.5.4 scikit-learn==0.22.2.post1 nibabel==3.2.1 matplotlib==3.3.4 joblib==0.17.0 && mkdir -p /usr/local/lib/python3.9/site-packages/sklearn/externals/ && echo 'from joblib import *' > /usr/local/lib/python3.9/site-packages/sklearn/externals/joblib.py
###ACTION_DELIMITER###
pip install cython>=0.28.5 numpy==1.19.5 scipy==1.5.4 scikit-learn==0.22.2.post1 nibabel==3.2.1 matplotlib==3.3.4 joblib==0.17.0 && mkdir -p /usr/local/lib/python3.9/site-packages/sklearn/externals/ && echo 'from joblib import *' > /usr/local/lib/python3.9/site-packages/sklearn/externals/joblib.py
###ACTION_DELIMITER###
apt-get update && apt-get install -y liblinear-dev && pip install cython>=0.28.5 numpy==1.19.5 scipy==1.5.4 scikit-learn==0.22.2.post1 nibabel==3.2.1 matplotlib==3.3.4 joblib==0.17.0 && mkdir -p /usr/local/lib/python3.9/site-packages/sklearn/externals/ && echo 'from joblib import *' > /usr/local/lib/python3.9/site-packages/sklearn/externals/joblib.py
###ACTION_DELIMITER###
pip install nilearn==0.2.2 && mkdir -p /usr/local/lib/python3.9/site-packages/sklearn/externals/ && echo 'from joblib import *' > /usr/local/lib/python3.9/site-packages/sklearn/externals/joblib.py
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
pip install scipy==1.6.0 scikit-learn==0.19.2 && make test
###ACTION_DELIMITER###
pip install scipy==1.5.0 scikit-learn==0.24.2 && mkdir -p /usr/local/lib/python3.9/site-packages/sklearn/datasets/ && echo 'from sklearn.datasets._base import *' > /usr/local/lib/python3.9/site-packages/sklearn/datasets/base.py && make test
###ACTION_DELIMITER###
pip install --upgrade setuptools==58.0.0 cython && pip install numpy==1.19.5 scipy==1.5.4 scikit-learn==0.23.2 nibabel==3.2.1 matplotlib==3.3.4 joblib==0.17.0 && mkdir -p /usr/local/lib/python3.9/site-packages/sklearn/externals/ && echo 'from joblib import *' > /usr/local/lib/python3.9/site-packages/sklearn/externals/joblib.py && make test
###ACTION_DELIMITER###
pip install setuptools==50.0.0 numpy==1.19.5 scipy==1.5.4 cython==0.29.21 scikit-learn==0.22.2.post1 nibabel==3.2.1 matplotlib==3.3.4 joblib==0.17.0 && mkdir -p /usr/local/lib/python3.9/site-packages/sklearn/{externals,datasets}/ && echo 'from joblib import *' > /usr/local/lib/python3.9/site-packages/sklearn/externals/joblib.py && echo 'from sklearn.datasets._base import *' > /usr/local/lib/python3.9/site-packages/sklearn/datasets/base.py && make test
###ACTION_DELIMITER###
echo 'nosetests -v -s nilearn' > /home/nilearn/test_commands.sh && chmod +x /home/nilearn/test_commands.sh && bash /home/nilearn/test_commands.sh
###ACTION_DELIMITER###
mkdir -p /usr/local/lib/python3.9/site-packages/sklearn/cross_validation && echo 'from sklearn.model_selection import *' > /usr/local/lib/python3.9/site-packages/sklearn/cross_validation/__init__.py && make test
###ACTION_DELIMITER###
mkdir -p /usr/local/lib/python3.9/site-packages/sklearn/utils/testing && echo 'from sklearn.utils import *' > /usr/local/lib/python3.9/site-packages/sklearn/utils/testing/__init__.py && echo 'from sklearn.linear_model import *' > /usr/local/lib/python3.9/site-packages/sklearn/linear_model/base.py && make test
###ACTION_DELIMITER###
echo 'nosetests -v -s nilearn' > /home/nilearn/test_commands.sh && chmod +x /home/nilearn/test_commands.sh && submit"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
nosetests -v -s nilearn

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
nosetests -v -s nilearn

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
nosetests -v -s nilearn

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
RUN git clone https://github.com/nilearn/nilearn.git /home/nilearn

WORKDIR /home/nilearn
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("nilearn", "nilearn_995_to_794")
class NILEARN_995_TO_794(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        import json
        # Regex pattern to capture test name and status (ok, ERROR, skipped) from test lines
        test_status_pattern = re.compile(r'^(\S+)\s+\.\.\..*?(ok|ERROR|skipped)$', re.MULTILINE | re.DOTALL)
        # Regex pattern to capture ERROR: <test_name> lines
        error_test_pattern = re.compile(r'^ERROR:\s+(\S+)$', re.MULTILINE)
        # Extract tests with status from test lines
        for test_name, status in test_status_pattern.findall(log):
            if status == 'ok':
                passed_tests.add(test_name)
            elif status == 'ERROR':
                failed_tests.add(test_name)
            elif status == 'skipped':
                skipped_tests.add(test_name)
        # Extract additional failed tests from ERROR: lines
        for test_name in error_test_pattern.findall(log):
            failed_tests.add(test_name)
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
