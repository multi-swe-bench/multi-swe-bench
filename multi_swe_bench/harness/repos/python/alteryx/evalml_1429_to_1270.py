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
                """make installdeps-test
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make installdeps-test
###ACTION_DELIMITER###
sed -i 's/codecov==2.1.0/codecov==2.1.13/' test-requirements.txt
###ACTION_DELIMITER###
make installdeps-test
###ACTION_DELIMITER###
make circleci-test
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libgomp1 libopenblas-dev pkg-config
###ACTION_DELIMITER###
pip list
###ACTION_DELIMITER###

###ACTION_DELIMITER###
export OMP_NUM_THREADS=8 && make circleci-test
###ACTION_DELIMITER###
virtualenv test_python && source test_python/bin/activate && make installdeps-test && make circleci-test
###ACTION_DELIMITER###
pip install virtualenv
###ACTION_DELIMITER###
virtualenv test_python && source test_python/bin/activate && make installdeps-test && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip install --upgrade pytest && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip install --upgrade pytest-xdist && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip install --upgrade pytest-cov && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip install --upgrade nlp_primitives && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip install pandas==1.5.3 nlp-primitives==2.0.0 && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip install numpy==1.24.4 && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip install numpy==1.23.5 pandas==1.5.3 woodwork==0.15.0 nlp-primitives==2.0.0 featuretools==1.29.0 && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip install numpy==1.23.5 pandas==1.5.3 woodwork==0.23.0 nlp-primitives==2.0.0 featuretools==1.29.0 && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip install scikit-learn==0.24.2 lightgbm==3.3.2 && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip install numpy==1.23.5 pandas==1.5.3 woodwork==0.13.0 featuretools==0.20.0 nlp-primitives==2.0.0 scikit-learn==0.24.2 lightgbm==3.3.2 && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip install numpy==1.23.5 pandas==1.5.3 woodwork==0.13.0 featuretools==0.20.0 nlp-primitives==1.1.0 scikit-learn==0.24.2 lightgbm==3.3.2 && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip install --force-reinstall numpy==1.23.5 pandas==1.5.3 woodwork==0.13.0 featuretools==0.20.0 nlp-primitives==1.1.0 scikit-learn==0.24.2 lightgbm==3.3.2 && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip install --force-reinstall numpy==1.23.5 pandas==1.5.3 woodwork==0.13.0 featuretools==0.20.0 nlp-primitives==1.1.0 scikit-learn==0.24.2 lightgbm==3.3.2 && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip list | grep woodwork && pip check
###ACTION_DELIMITER###
source test_python/bin/activate && pip install scikit-optimize==0.9.0 && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip uninstall -y woodwork && pip install woodwork==0.13.0 && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip install woodwork==0.11.0 && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip install woodwork==0.10.0 && make circleci-test
###ACTION_DELIMITER###
source test_python/bin/activate && pip uninstall -y woodwork && pip cache purge && pip install woodwork==0.10.0 && python -c 'import woodwork; print(woodwork.DataTable)' && make circleci-test
###ACTION_DELIMITER###
echo 'pytest evalml/ -n 8 --doctest-modules --cov=evalml --junitxml=test-reports/junit.xml --doctest-continue-on-failure -v' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest evalml/ -n 8 --doctest-modules --cov=evalml --junitxml=test-reports/junit.xml --doctest-continue-on-failure -v

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
pytest evalml/ -n 8 --doctest-modules --cov=evalml --junitxml=test-reports/junit.xml --doctest-continue-on-failure -v

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
pytest evalml/ -n 8 --doctest-modules --cov=evalml --junitxml=test-reports/junit.xml --doctest-continue-on-failure -v

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
RUN git clone https://github.com/alteryx/evalml.git /home/evalml

WORKDIR /home/evalml
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("alteryx", "evalml_1429_to_1270")
class EVALML_1429_TO_1270(Instance):
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
        # Regex pattern to match test status and name
        pattern = r'\b(PASSED|SKIPPED|FAILED|ERROR)\b\s+(.*?::.*?)\s*$'
        matches = re.findall(pattern, log, re.MULTILINE)
        for status, test_name in matches:
            status = status.upper()
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
            elif status in ('FAILED', 'ERROR'):
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
