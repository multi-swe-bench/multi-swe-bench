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
        return "python:3.11-slim"
    
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
pip install -e . && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo "pytest -sv -rs --cov=moto --cov-report xml ./tests/ --ignore tests/test_batch --ignore tests/test_ec2 --ignore tests/test_sqs
pytest -sv -rs ./tests/test_xray
MOTO_CALL_RESET_API=false pytest -sv --cov=moto --cov-report xml --cov-append -n 4 ./tests/test_batch ./tests/test_ec2 ./tests/test_sqs --dist loadscope" > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash /home/moto/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -sv -rs --cov=moto --cov-report xml ./tests/ --ignore tests/test_batch --ignore tests/test_ec2 --ignore tests/test_sqs
pytest -sv -rs ./tests/test_xray
MOTO_CALL_RESET_API=false pytest -sv --cov=moto --cov-report xml --cov-append -n 4 ./tests/test_batch ./tests/test_ec2 ./tests/test_sqs --dist loadscope

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
pytest -sv -rs --cov=moto --cov-report xml ./tests/ --ignore tests/test_batch --ignore tests/test_ec2 --ignore tests/test_sqs
pytest -sv -rs ./tests/test_xray
MOTO_CALL_RESET_API=false pytest -sv --cov=moto --cov-report xml --cov-append -n 4 ./tests/test_batch ./tests/test_ec2 ./tests/test_sqs --dist loadscope

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
pytest -sv -rs --cov=moto --cov-report xml ./tests/ --ignore tests/test_batch --ignore tests/test_ec2 --ignore tests/test_sqs
pytest -sv -rs ./tests/test_xray
MOTO_CALL_RESET_API=false pytest -sv --cov=moto --cov-report xml --cov-append -n 4 ./tests/test_batch ./tests/test_ec2 ./tests/test_sqs --dist loadscope

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
FROM python:3.11-slim

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
RUN git clone https://github.com/getmoto/moto.git /home/moto

WORKDIR /home/moto
RUN git reset --hard
RUN git checkout 5252e9202f170b62edaae9239640b564e83710c3

RUN git checkout {pr.base.sha}"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("getmoto", "moto_5_1_0")
class MOTO_5_1_0(Instance):
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
        # Remove ANSI codes
        log = re.sub(r'\x1b\[[0-9;]*m', '', log)
        # Regex: start of line, path ending in .py, ::, test name, optional [::param], whitespace, STATUS at end of line
        test_line_re = re.compile(
            r'^(?P<test>[\w./-]+\.py::[\w\[\]<>.,:=-]+)\s+(?P<status>PASSED|FAILED|SKIPPED)\s*$',
            re.MULTILINE
        )
            # Track the last status for each test
        test_status = {}
        for match in test_line_re.finditer(log):
            test_name = match.group('test').strip()
            status = match.group('status')
            test_status[test_name] = status  # Only the last status will remain
        # Build sets based on final status
        passed_tests = {t for t, s in test_status.items() if s == "PASSED"}
        failed_tests = {t for t, s in test_status.items() if s == "FAILED"}
        skipped_tests = {t for t, s in test_status.items() if s == "SKIPPED"}
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
