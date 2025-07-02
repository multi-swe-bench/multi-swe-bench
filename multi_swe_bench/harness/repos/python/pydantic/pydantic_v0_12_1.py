import re

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

    def dependency(self) -> Image | None:
        return "python:3.7-slim"
    
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
make install
###ACTION_DELIMITER###
pip install -U setuptools pip
###ACTION_DELIMITER###
pip install -U -r requirements.txt
###ACTION_DELIMITER###
pip install -U pytest pytest-cov pytest-isort pytest-mock pytest-sugar attrs coverage ujson email-validator .
###ACTION_DELIMITER###
echo 'pytest --cov=pydantic -v
pip uninstall -y ujson email-validator
pytest --cov=pydantic -v' > /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y ujson email-validator
###ACTION_DELIMITER###
pytest --cov=pydantic -v"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest --cov=pydantic -v
pip uninstall -y ujson email-validator
pytest --cov=pydantic -v

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
pytest --cov=pydantic -v
pip uninstall -y ujson email-validator
pytest --cov=pydantic -v

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
pytest --cov=pydantic -v
pip uninstall -y ujson email-validator
pytest --cov=pydantic -v

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
FROM python:3.7-slim

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
RUN git clone https://github.com/pydantic/pydantic.git /home/pydantic

WORKDIR /home/pydantic
RUN git reset --hard
RUN git checkout 8885503ccb4b496d8591e9715004740d7494cc40

RUN git checkout {pr.base.sha}"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pydantic", "pydantic_v0_12_1")
class PYDANTIC_V0_12_1(Instance):
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
        # ISORT SKIPPED: must be handled first
        isort_skipped_pattern = re.compile(r"^(tests/.*?::ISORT) SKIPPED")
        # Regular test result: PASSED or SKIPPED (not ISORT)
        test_result_pattern = re.compile(
            r"^(tests/.*?::(?!ISORT)[\w\[\]-]+)\s+(PASSED|SKIPPED)\b"
        )
        # Collection errors
        error_collect_pattern = re.compile(r"ERROR collecting (\S+)")
        # Summary error lines
        error_summary_pattern = re.compile(r"^ERROR (\S+)")
        for line in log.splitlines():
            m = isort_skipped_pattern.match(line)
            if m:
                skipped_tests.add(m.group(1))
                continue
            m = test_result_pattern.match(line)
            if m:
                test_name, status = m.group(1), m.group(2)
                if status == "PASSED":
                    passed_tests.add(test_name)
                elif status == "SKIPPED":
                    skipped_tests.add(test_name)
                continue
            m = error_collect_pattern.search(line)
            if m:
                failed_tests.add(m.group(1))
                continue
            m = error_summary_pattern.match(line)
            if m:
                failed_tests.add(m.group(1))
                continue
        # Remove any overlap: a test can only be in one set
        skipped_tests -= passed_tests
        failed_tests -= (passed_tests | skipped_tests)

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
