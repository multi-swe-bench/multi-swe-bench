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
ls -F ci/
###ACTION_DELIMITER###
ls -aF
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl build-essential
###ACTION_DELIMITER###
export TRAVIS_RUST_VERSION=1.20.0 && export TARGET=x86_64-unknown-linux-gnu && export TRAVIS_OS_NAME=linux && bash ci/install.sh
###ACTION_DELIMITER###
source "$HOME/.cargo/env" && export TRAVIS_RUST_VERSION=1.20.0 && export TARGET=x86_64-unknown-linux-gnu && export TRAVIS_OS_NAME=linux && bash ci/install.sh
###ACTION_DELIMITER###
source "$HOME/.cargo/env" && export TRAVIS_RUST_VERSION=1.20.0 && export TARGET=x86_64-unknown-linux-gnu && export TRAVIS_OS_NAME=linux && bash ci/script.sh
###ACTION_DELIMITER###
apt-get install -y zsh xz-utils
###ACTION_DELIMITER###
source "$HOME/.cargo/env" && export TRAVIS_RUST_VERSION=1.20.0 && export TARGET=x86_64-unknown-linux-gnu && export TRAVIS_OS_NAME=linux && bash ci/script.sh
###ACTION_DELIMITER###
apt-get install -y file
###ACTION_DELIMITER###
echo 'source "$HOME/.cargo/env" && cargo test --verbose --all' > /home/ripgrep/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
source "$HOME/.cargo/env" && cargo test --verbose --all

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
source "$HOME/.cargo/env" && cargo test --verbose --all

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
source "$HOME/.cargo/env" && cargo test --verbose --all

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
RUN apt-get update && apt-get install -y git

# Ensure bash is available
RUN if [ ! -f /bin/bash ]; then         if command -v apk >/dev/null 2>&1; then             apk add --no-cache bash;         elif command -v apt-get >/dev/null 2>&1; then             apt-get update && apt-get install -y bash;         elif command -v yum >/dev/null 2>&1; then             yum install -y bash;         else             exit 1;         fi     fi

WORKDIR /home/
COPY fix.patch /home/
COPY test.patch /home/
RUN git clone https://github.com/BurntSushi/ripgrep.git /home/ripgrep

WORKDIR /home/ripgrep
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("BurntSushi", "ripgrep_772_to_406")
class RIPGREP_772_TO_406(Instance):
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
        # Pattern for lines like: test path::to::test ... ok
        passed_pattern = re.compile(r"^test (.*) \.\.\. ok$")
        # Pattern for lines like: test path::to::test ... ignored
        ignored_pattern = re.compile(r"^test (.*) \.\.\. ignored$")
        # Pattern to find the "failures:" block and capture the lines underneath until the next "test result:"
        failures_block_pattern = re.compile(r"failures:\n(.*?)\ntest result:", re.DOTALL)
        # First, find all the explicitly listed failed tests.
        failures_match = failures_block_pattern.search(log)
        if failures_match:
            failed_lines_str = failures_match.group(1).strip()
            for line in failed_lines_str.split('\n'):
                line = line.strip()
                # Ignore decorative lines like "---- thread 'main' panicked at ... ----"
                if line and not line.startswith("----"):
                    failed_tests.add(line)
        # Now, iterate over the log line by line to get passed and ignored tests.
        for line in log.splitlines():
            passed_match = passed_pattern.match(line)
            if passed_match:
                test_name = passed_match.group(1).strip()
                # Only count a test as passed if it's not in our list of failures.
                if test_name not in failed_tests:
                    passed_tests.add(test_name)
                continue
            ignored_match = ignored_pattern.match(line)
            if ignored_match:
                test_name = ignored_match.group(1).strip()
                if test_name not in failed_tests:
                    skipped_tests.add(test_name)
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
