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
                """add-apt-repository -y ppa:deadsnakes/ppa && apt-get update && apt-get install -y python2.7 python2.7-pip virtualenv
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository -y ppa:deadsnakes/ppa && apt-get update && apt-get install -y python2.7 python2.7-pip virtualenv
###ACTION_DELIMITER###
ls
###ACTION_DELIMITER###
add-apt-repository universe && apt-get update && apt-get install -y python2.7 python2.7-pip
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential zlib1g-dev libssl-dev libncurses5-dev libsqlite3-dev libreadline-dev libgdm-dev libdb4o-cil-dev libpcap-dev wget
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential zlib1g-dev libssl-dev libncurses5-dev libsqlite3-dev libreadline-dev libgdm-dev libpcap-dev wget
###ACTION_DELIMITER###
wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz
###ACTION_DELIMITER###
tar -xzf Python-2.7.18.tgz
###ACTION_DELIMITER###
cd Python-2.7.18 && ./configure --prefix=/usr/local && make -j 4 && make install
###ACTION_DELIMITER###
cd ..
###ACTION_DELIMITER###
virtualenv -p python2.7 venv
###ACTION_DELIMITER###
python2.7 -m ensurepip --default-pip && pip2.7 install virtualenv
###ACTION_DELIMITER###
virtualenv -p python2.7 venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
pip install 'Cython<0.29.21'
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
pip install 'PyYAML<5.4'
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo -e 'AWS_ACCESS_KEY_ID=foo AWS_SECRET_ACCESS_KEY=bar AWS_DEFAULT_REGION=us-east-1 C7N_VALIDATE=true nosetests -v --processes=-1 --process-timeout=300 tests' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
AWS_ACCESS_KEY_ID=foo AWS_SECRET_ACCESS_KEY=bar AWS_DEFAULT_REGION=us-east-1 C7N_VALIDATE=true nosetests -v --processes=-1 --process-timeout=300 tests

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
AWS_ACCESS_KEY_ID=foo AWS_SECRET_ACCESS_KEY=bar AWS_DEFAULT_REGION=us-east-1 C7N_VALIDATE=true nosetests -v --processes=-1 --process-timeout=300 tests

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
AWS_ACCESS_KEY_ID=foo AWS_SECRET_ACCESS_KEY=bar AWS_DEFAULT_REGION=us-east-1 C7N_VALIDATE=true nosetests -v --processes=-1 --process-timeout=300 tests

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


@Instance.register("cloud-custodian", "cloud_custodian_1288_to_787")
class CLOUD_CUSTODIAN_1288_TO_787(Instance):
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
        # Parse log content and extract test results
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re
        # Parse passed tests
        passed_pattern = re.compile(r'.*?([\w_]+) \(.+?\) \.\.\. ok', re.MULTILINE)
        for match in passed_pattern.finditer(log):
            passed_tests.add(match.group(1))
        # Parse failed tests (errors and failures)
        error_pattern = re.compile(r'.*?(?:ERROR|FAIL): ([\w_]+) \(.+?\)', re.MULTILINE)
        failed_tests.update(error_pattern.findall(log))
        failed_status_pattern = re.compile(r'.*?([\w_]+) \(.+?\) \.\.\. FAILED', re.MULTILINE)
        failed_tests.update(failed_status_pattern.findall(log))
        # Parse skipped tests
        skipped_pattern = re.compile(r'.*?([\w_]+) \(.+?\) \.\.\. skipped', re.MULTILINE)
        skipped_tests.update(skipped_pattern.findall(log))
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
