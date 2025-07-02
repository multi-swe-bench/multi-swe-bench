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
        return "python:2.7-slim"
    
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
                """ls -F
###ACTION_DELIMITER###
pip install https://github.com/spulec/python-coveralls/tarball/796d9dba34b759664e42ba39e6414209a0f319ad
###ACTION_DELIMITER###
pip install -r requirements.txt --no-deps
###ACTION_DELIMITER###
nosetests
###ACTION_DELIMITER###
pip install boto
###ACTION_DELIMITER###
nosetests
###ACTION_DELIMITER###
pip install httpretty python-dateutil
###ACTION_DELIMITER###
pip install funcsigs
###ACTION_DELIMITER###
nosetests
###ACTION_DELIMITER###
pip install flask
###ACTION_DELIMITER###
nosetests
###ACTION_DELIMITER###
pip install rednose
###ACTION_DELIMITER###
echo 'nosetests -v --rednose' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
nosetests -v --rednose

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
nosetests -v --rednose

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
nosetests -v --rednose

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
FROM python:2.7-slim

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
RUN git checkout ba012d990277afdb5e39f0bfedf0fcad36879c7f

RUN git checkout {pr.base.sha}"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("getmoto", "moto_0_3_3")
class MOTO_0_3_3(Instance):
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
        # Implement the log parsing logic here
        test_pattern = re.compile(r"^([^.\n].*?)\s*\.{3}\s*(passed|FAILED|skipped)", re.MULTILINE)
        for match in test_pattern.finditer(log):
            test_name = match.group(1).strip()
            status = match.group(2)
            if status == "passed":
                passed_tests.add(test_name)
            elif status == "FAILED":
                failed_tests.add(test_name)
            elif status == "skipped":
                skipped_tests.add(test_name)
        failed_pattern = re.compile(r"^(test_.*|.*\.test_.*)", re.MULTILINE)
        lines = log.splitlines()
        for i, line in enumerate(lines):
            if line == "FAILED":
                if i > 0:
                    match = failed_pattern.match(lines[i-1])
                    if match:
                        failed_tests.add(match.group(1).strip())
        exception_pattern = re.compile(r"^(.*?\s*\.{3})?.*Exception in thread.*", re.MULTILINE)
        for match in exception_pattern.finditer(log):
            if match.group(1):
                failed_tests.add(match.group(1).replace(" ...", "").strip())
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
