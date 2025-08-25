import re
import sys

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
        return "ubuntu:20.04"
    
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
mkdir build
###ACTION_DELIMITER###
cd build
###ACTION_DELIMITER###
cmake -DCATCH_BUILD_TESTING=ON -DCATCH_BUILD_EXAMPLES=ON -DCATCH_BUILD_EXTRA_TESTS=ON ..
###ACTION_DELIMITER###
make
###ACTION_DELIMITER###
echo "mkdir -p build && cd build && cmake -DCATCH_BUILD_TESTING=ON -DCATCH_BUILD_EXAMPLES=ON -DCATCH_BUILD_EXTRA_TESTS=ON .. && make && ctest -E DebugBreakMacros -V" > /home/Catch2/test_commands.sh
###ACTION_DELIMITER###
ctest --show-only"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
mkdir -p build && cd build && cmake -DCATCH_BUILD_TESTING=ON -DCATCH_BUILD_EXAMPLES=ON -DCATCH_BUILD_EXTRA_TESTS=ON .. && make && ctest -E DebugBreakMacros -V

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
mkdir -p build && cd build && cmake -DCATCH_BUILD_TESTING=ON -DCATCH_BUILD_EXAMPLES=ON -DCATCH_BUILD_EXTRA_TESTS=ON .. && make && ctest -E DebugBreakMacros -V

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
mkdir -p build && cd build && cmake -DCATCH_BUILD_TESTING=ON -DCATCH_BUILD_EXAMPLES=ON -DCATCH_BUILD_EXTRA_TESTS=ON .. && make && ctest -E DebugBreakMacros -V

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
FROM ubuntu:20.04

## Set noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Install basic requirements
# For example: RUN apt-get update && apt-get install -y git
# For example: RUN yum install -y git
# For example: RUN apk add --no-cache git
RUN apt-get update && apt-get install -y git cmake clang g++

# Ensure bash is available
RUN if [ ! -f /bin/bash ]; then         if command -v apk >/dev/null 2>&1; then             apk add --no-cache bash;         elif command -v apt-get >/dev/null 2>&1; then             apt-get update && apt-get install -y bash;         elif command -v yum >/dev/null 2>&1; then             yum install -y bash;         else             exit 1;         fi     fi

WORKDIR /home/
COPY fix.patch /home/
COPY test.patch /home/
RUN git clone https://github.com/catchorg/Catch2.git /home/Catch2

WORKDIR /home/Catch2
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("catchorg", "Catch2_1866_to_1510")
class CATCH2_1866_TO_1510(Instance):
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
        # Regex to find all test names
        all_tests_pattern = re.compile(r"^\t(.+)", re.MULTILINE)
        all_tests = set(all_tests_pattern.findall(log))
        # Regex to find the block of failed tests
        failed_tests_block_pattern = re.compile(r"The following tests FAILED:([\s\S]*)")
        failed_tests_block_match = failed_tests_block_pattern.search(log)
        if failed_tests_block_match:
            failed_tests_block = failed_tests_block_match.group(1)
            # Regex to find individual failed test names within the block
            failed_test_pattern = re.compile(r"\t  \d+ - (.*) \(Failed\)")
            failed_tests.update(failed_test_pattern.findall(failed_tests_block))
        # Passed tests are all tests minus failed tests
        passed_tests = all_tests - failed_tests
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
