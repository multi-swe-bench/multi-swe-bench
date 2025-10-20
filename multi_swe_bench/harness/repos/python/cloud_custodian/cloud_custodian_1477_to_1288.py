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
apt-get update && apt-get install -y python2.7 python2.7-dev virtualenv build-essential libssl-dev zlib1g-dev libyaml-dev libreadline-dev libsqlite3-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y && apt-get update
###ACTION_DELIMITER###
apt-get install -y build-essential libssl-dev zlib1g-dev libreadline-dev libsqlite3-dev libyaml-dev
###ACTION_DELIMITER###
wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz
###ACTION_DELIMITER###
tar -xzf Python-2.7.18.tgz
###ACTION_DELIMITER###
cd Python-2.7.18 && ./configure
###ACTION_DELIMITER###
make
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
wget https://bootstrap.pypa.io/pip/2.7/get-pip.py && python2.7 get-pip.py
###ACTION_DELIMITER###
pip2.7 install virtualenv
###ACTION_DELIMITER###
cd /home/cloud-custodian
###ACTION_DELIMITER###
virtualenv --python=python2.7 custodian
###ACTION_DELIMITER###
source custodian/bin/activate
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
pip install cython
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
pip uninstall -y cython && pip install cython==0.29.37
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
pip install --no-use-pep517 PyYAML==5.3.1
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo 'pytest --verbose --tb=native -n auto tests tools' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest --verbose --tb=native -n auto tests tools

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
pytest --verbose --tb=native -n auto tests tools

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
pytest --verbose --tb=native -n auto tests tools

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
RUN git clone https://github.com/cloud-custodian/cloud-custodian.git /home/cloud-custodian

WORKDIR /home/cloud-custodian
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("cloud-custodian", "cloud_custodian_1477_to_1288")
class CLOUD_CUSTODIAN_1477_TO_1288(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re
        pattern = r'(?:\[gw\d+\] \[\s*\d+%\] )?(PASSED|FAILED|SKIPPED)[:\s]+(tests/[\w/\.::\-]+)'  # Allow colon or space after status
        # Capture summary to verify counts
        summary_pattern = r'======= (\d+) failed, (\d+) passed, (\d+) skipped'
        summary_match = re.search(summary_pattern, log)
        expected = {}
        if summary_match:
            expected = {
                'failed': int(summary_match.group(1)),
                'passed': int(summary_match.group(2)),
                'skipped': int(summary_match.group(3))
            }
        matches = re.findall(pattern, log)
        for status, test_name in matches:
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
        # Validate against summary counts
        if expected:
            # Check failed tests
            if len(failed_tests) < expected['failed']:
                fallback_pattern = re.compile(r'FAILED (tests/[\w/\.::\-]+)')
                additional_failed = re.findall(fallback_pattern, log)
                failed_tests.update(additional_failed)
            # Check passed tests
            if len(passed_tests) < expected['passed']:
                fallback_pattern = re.compile(r'PASSED[:\s]+(tests/[\w/\.::\-]+)')  # Handle colon or space after PASSED
                additional_passed = re.findall(fallback_pattern, log)
                passed_tests.update(additional_passed)
            # Check skipped tests
            if len(skipped_tests) < expected['skipped']:
                fallback_pattern = re.compile(r'SKIPPED (tests/[\w/\.::\-]+)')
                additional_skipped = re.findall(fallback_pattern, log)
                skipped_tests.update(additional_skipped)
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
