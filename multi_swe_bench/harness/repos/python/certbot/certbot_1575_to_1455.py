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
                """ls
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python2.7 python-pip build-essential libssl-dev python-dev
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository -y ppa:deadsnakes/ppa
###ACTION_DELIMITER###
apt-get install -y build-essential zlib1g-dev libssl-dev libncurses5-dev libsqlite3-dev libreadline-dev libtk8.6 libgdm-dev libdb4o-cil-dev libpcap-dev
###ACTION_DELIMITER###
apt-get install -y build-essential zlib1g-dev libssl-dev libncurses-dev libsqlite3-dev libreadline-dev libtk8.6 libgdm-dev libpcap-dev
###ACTION_DELIMITER###
wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz
###ACTION_DELIMITER###
tar xzf Python-2.7.18.tgz
###ACTION_DELIMITER###
cd Python-2.7.18
###ACTION_DELIMITER###
./configure
###ACTION_DELIMITER###
make
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
cd /home/certbot
###ACTION_DELIMITER###
wget https://bootstrap.pypa.io/pip/2.7/get-pip.py && python2.7 get-pip.py
###ACTION_DELIMITER###
pip2.7 install -e ".[testing]"
###ACTION_DELIMITER###
cd acme && pip2.7 install -e .
###ACTION_DELIMITER###
cd /home/certbot
###ACTION_DELIMITER###
pip2.7 install -e ".[testing]"
###ACTION_DELIMITER###
echo 'nosetests -v' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
nosetests -v

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
nosetests -v

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
nosetests -v

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
RUN git clone https://github.com/certbot/certbot.git /home/certbot

WORKDIR /home/certbot
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("certbot", "certbot_1575_to_1455")
class CERTBOT_1575_TO_1455(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        import json
        # Regex patterns to match test lines
        # Passed tests: [line_num] test_name (class) ... ok
        passed_pattern = re.compile(r'^\s*(?:\[\s*\d+\]\s+)?(test_\w+(?:\s*\(.*?\))?).*?\s*(?:ok|passed)', re.IGNORECASE | re.MULTILINE)
        passed_tests = set(passed_pattern.findall(log))
        # Failed tests: [line_num] FAIL: test_name (class)
        failed_pattern = re.compile(r'^\s*(?:\[\s*\d+\]\s+)?(?:FAIL|FAILED):\s+(test_\w+(?:\s*\(.*?\))?)', re.IGNORECASE | re.MULTILINE)
        failed_tests = set(failed_pattern.findall(log))
        # Skipped tests: [line_num] test_name (class) ... skipped
        skipped_pattern = re.compile(r'^\s*(?:\[\s*\d+\]\s+)?(test_\w+(?:\s*\(.*?\))?)\s*\.\.\.\s*(?:skipped)', re.IGNORECASE | re.MULTILINE)
        skipped_tests = set(skipped_pattern.findall(log))
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
