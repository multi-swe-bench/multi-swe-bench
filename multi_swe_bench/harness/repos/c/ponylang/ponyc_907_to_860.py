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
        return "ubuntu:16.04"
    
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
echo "deb http://llvm.org/apt/xenial/ llvm-toolchain-xenial-3.8 main" | tee -a /etc/apt/sources.list
###ACTION_DELIMITER###
wget -O - http://llvm.org/apt/llvm-snapshot.gpg.key| apt-key add -
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget -O - http://llvm.org/apt/llvm-snapshot.gpg.key| apt-key add -
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y apt-transport-https
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
sed -i 's/https/http/g' /etc/apt/sources.list
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
sed -i '$d' /etc/apt/sources.list
###ACTION_DELIMITER###
echo "deb http://archive.ubuntu.com/ubuntu/ xenial main" | tee -a /etc/apt/sources.list
###ACTION_DELIMITER###
echo "deb http://llvm.org/apt/xenial/ llvm-toolchain-xenial-3.8 main" >> /etc/apt/sources.list
###ACTION_DELIMITER###
apt-get install -y make gcc g++ git zlib1g-dev libncurses5-dev libssl-dev llvm-3.8-dev
###ACTION_DELIMITER###
make config=release
###ACTION_DELIMITER###
ls -F test/
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
apt-cache search pcre2
###ACTION_DELIMITER###

###ACTION_DELIMITER###
apt-get install -y libpcre2-dev
###ACTION_DELIMITER###

###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
echo "make test" > /home/ponyc/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
make test

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
make test

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
make test

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
FROM ubuntu:16.04

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
RUN git clone https://github.com/ponylang/ponyc.git /home/ponyc

WORKDIR /home/ponyc
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ponylang", "ponyc_907_to_860")
class PONYC_907_TO_860(Instance):
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
        # Pattern for [       OK ] <test_name> (<duration>)
        passed_pattern1 = re.compile(r"\[\s+OK\s+\]\s+([\w\.]+)")
        # Pattern for ---- Passed: <test_name>
        passed_pattern2 = re.compile(r"---- Passed: ([\w/.-]*[a-zA-Z]+[\w/.-]*)")
        # Pattern for tests that are complete
        passed_pattern3 = re.compile(r"\d+ tests started, \d+ complete: ([\w/.-]+) complete")
        # Pattern for [  FAILED  ] <test_name>
        failed_pattern1 = re.compile(r"\[  FAILED  \]\s+([\w\.]+\.[\w\.]+)")
        # Pattern for **** FAILED: <test_name>
        failed_pattern2 = re.compile(r"\*\*\*\* FAILED: ([\w/.-]*[a-zA-Z]+[\w/.-]*)")
        for line in log.splitlines():
            # Passed tests
            match = passed_pattern1.search(line)
            if match:
                passed_tests.add(match.group(1))
                continue
            match = passed_pattern2.search(line)
            if match:
                passed_tests.add(match.group(1))
                continue
            match = passed_pattern3.search(line)
            if match:
              passed_tests.add(match.group(1).strip())
              continue
            # Failed tests
            match = failed_pattern1.search(line)
            if match:
                failed_tests.add(match.group(1))
                continue
            match = failed_pattern2.search(line)
            if match:
                failed_tests.add(match.group(1))
                continue
        passed_tests -= failed_tests
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
