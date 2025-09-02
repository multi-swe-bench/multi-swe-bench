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
ls requirements
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libssl-dev libffi-dev python3-dev
###ACTION_DELIMITER###
pip install -r requirements/test.txt
###ACTION_DELIMITER###
echo 'pytest -v -rA tests' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
git submodule update --init
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install cython
###ACTION_DELIMITER###
python setup.py build
###ACTION_DELIMITER###
python setup.py build_ext --inplace
###ACTION_DELIMITER###
cython aiohttp/_websocket.pyx
###ACTION_DELIMITER###
ls aiohttp
###ACTION_DELIMITER###
python setup.py build_ext --inplace
###ACTION_DELIMITER###
cython aiohttp/_http_parser.pyx
###ACTION_DELIMITER###
make
###ACTION_DELIMITER###
apt-get install -y nodejs npm
###ACTION_DELIMITER###
make"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v -rA tests

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
pytest -v -rA tests

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
pytest -v -rA tests

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
RUN git clone https://github.com/aio-libs/aiohttp.git /home/aiohttp

WORKDIR /home/aiohttp
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("aio-libs", "aiohttp_7079_to_6201")
class AIOHTTP_7079_TO_6201(Instance):
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
        passed_tests = set[str]() # Tests that passed successfully
        failed_tests = set[str]() # Tests that failed
        skipped_tests = set[str]() # Tests that were skipped
        import re
        import json
        lines = log.split('\n')
        for line in lines:
            # Check for PASSED tests (e.g., 'tests/test___all__.py::test___all__ PASSED')
            passed_match = re.match(r'\s*(tests/.*?) PASSED\b', line)
            if passed_match:
                test_name = passed_match.group(1).strip()
                passed_tests.add(test_name)
            # Check for FAILED tests (e.g., 'FAILED tests/test_client_session.py::test_client_session_timeout_zero - ...')
            failed_match = re.match(r'\s*FAILED (tests/.*?)(?: -|$)', line)
            if failed_match:
                test_name = failed_match.group(1).strip()
                failed_tests.add(test_name)
            # Check for SKIPPED tests (two formats: 'tests/... SKIPPED' or 'SKIPPED [1] tests/...')
            skipped_match1 = re.match(r'\s*(tests/.*?) SKIPPED\b', line)
            skipped_match2 = re.match(r'\s*SKIPPED \[\d+\] (tests/.*?):', line)
            if skipped_match1:
                test_name = skipped_match1.group(1).strip()
                skipped_tests.add(test_name)
            elif skipped_match2:
                test_name = skipped_match2.group(1).strip()
                skipped_tests.add(test_name)
            # Ignore XFAIL tests (not counted as failed)
            xfail_match = re.match(r'\s*XFAIL (tests/.*?)(?:$|\s)', line)
            if xfail_match:
                pass  # XFAIL is not a failure, so no action
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
