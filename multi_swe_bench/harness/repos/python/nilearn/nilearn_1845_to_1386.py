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
pip list
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
pip install numpy scipy scikit-learn nibabel nose coverage
###ACTION_DELIMITER###
make inplace
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
pip uninstall -y scikit-learn && pip install scikit-learn==0.22.2.post1
###ACTION_DELIMITER###
pip install 'cython>=0.28.5'
###ACTION_DELIMITER###
pip install scikit-learn==0.22.2.post1
###ACTION_DELIMITER###
apt-get update && apt-get install -y gcc
###ACTION_DELIMITER###
pip install scikit-learn==0.22.2.post1
###ACTION_DELIMITER###
pip uninstall -y cython numpy && pip install cython==0.29.36 numpy==1.21.6
###ACTION_DELIMITER###
pip uninstall -y scipy nibabel && pip install scipy==1.7.3 nibabel==3.2.2
###ACTION_DELIMITER###
pip install scikit-learn==0.22.2.post1
###ACTION_DELIMITER###
apt-get update && apt-get install -y g++
###ACTION_DELIMITER###
pip install scikit-learn==0.22.2.post1
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
pip uninstall -y joblib && pip install joblib==0.14.1
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
echo 'nosetests -v -s nilearn' > /home/nilearn/test_commands.sh"""
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
RUN git clone https://github.com/nilearn/nilearn.git /home/nilearn

WORKDIR /home/nilearn
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("nilearn", "nilearn_1845_to_1386")
class NILEARN_1845_TO_1386(Instance):
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
        # Extract test names using pattern matching for observed log formats
        # Passed tests: Lines ending with '... ok'
        passed_pattern = r'^(.*?)\s+\.\.\.\s+ok$'
        passed_matches = re.findall(passed_pattern, log, re.MULTILINE | re.IGNORECASE)
        passed_tests = set(test.strip() for test in passed_matches if 'test' in test.lower())
        # Failed tests: Lines starting with 'ERROR:' or 'FAIL:'
        failed_pattern = r'^(ERROR|FAIL):\s+(.*)$'
        failed_matches = re.findall(failed_pattern, log, re.MULTILINE | re.IGNORECASE)
        failed_tests = set(test.strip() for (_, test) in failed_matches if 'test' in test.lower())
        # Skipped tests: Lines ending with '... SKIP' or starting with 'SKIP:'
        skipped_pattern1 = r'^(.*?)\s+\.\.\.\s+SKIP$'
        skipped_pattern2 = r'^SKIP:\s+(.*)$'
        skipped_matches1 = re.findall(skipped_pattern1, log, re.MULTILINE | re.IGNORECASE)
        skipped_matches2 = re.findall(skipped_pattern2, log, re.MULTILINE | re.IGNORECASE)
        skipped_tests = set(
            test.strip() for test in skipped_matches1 + skipped_matches2
            if 'test' in test.lower()
        )
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
