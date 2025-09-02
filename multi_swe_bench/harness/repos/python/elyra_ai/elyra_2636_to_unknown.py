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
apt-get update && apt-get install -y curl && curl -sL https://deb.nodesource.com/setup_14.x | bash - && apt-get install -y nodejs
###ACTION_DELIMITER###
pip3 install --upgrade "elyra[all]>=3.7.0" --use-deprecated legacy-resolver
###ACTION_DELIMITER###
jupyter server extension list
###ACTION_DELIMITER###
pip3 install ipython-genutils
###ACTION_DELIMITER###
jupyter server extension list
###ACTION_DELIMITER###
echo 'make test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip3 install pytest-jupyter
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
mkdir -p docker
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
mkdir -p elyra/tests/kfp/docker
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls -ld docker
###ACTION_DELIMITER###
touch docker/dummy.txt
###ACTION_DELIMITER###
touch docker/Dockerfile
###ACTION_DELIMITER###
touch elyra/tests/kfp/docker/Dockerfile
###ACTION_DELIMITER###
rm -rf docker && touch docker
###ACTION_DELIMITER###
rm -f docker && mkdir -p docker && chmod 777 docker
###ACTION_DELIMITER###
apt-get update && apt-get install -y docker.io
###ACTION_DELIMITER###
make elyra-image
###ACTION_DELIMITER###
apt-get update && apt-get install -y rsync
###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i 's/docker buildx build \\/docker build \\/; /--progress=plain/d; /--output=type=docker/d' Makefile
###ACTION_DELIMITER###
make elyra-image
###ACTION_DELIMITER###
service docker start
###ACTION_DELIMITER###
service docker status
###ACTION_DELIMITER###
dockerd --debug
###ACTION_DELIMITER###
update-alternatives --set iptables /usr/sbin/iptables-legacy && update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy
###ACTION_DELIMITER###
service docker start
###ACTION_DELIMITER###
service docker status
###ACTION_DELIMITER###
mkdir -p /etc/docker && echo '{"iptables": false}' > /etc/docker/daemon.json
###ACTION_DELIMITER###
cat /var/log/docker.log
###ACTION_DELIMITER###
apt-get update && apt-get install -y kmod iptables && iptables -t nat -N DOCKER && service docker restart
###ACTION_DELIMITER###
mkdir -p elyra/tests/kfp/docker && echo 'make test' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v elyra -k "not docker"' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'alias docker=true; pytest -v elyra' > test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
alias docker=true; pytest -v elyra

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
alias docker=true; pytest -v elyra

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
alias docker=true; pytest -v elyra

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
RUN git clone https://github.com/elyra-ai/elyra.git /home/elyra

WORKDIR /home/elyra
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("elyra-ai", "elyra_2636_to_unknown")
class ELYRA_2636_TO_UNKNOWN(Instance):
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
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        # Pattern for PASSED tests: matches lines ending with " PASSED [xx%]"
        passed_pattern = re.compile(r'^(.*?)\s+PASSED\s+\[.*?\]$', re.MULTILINE)
        for match in passed_pattern.findall(log):
            passed_tests.add(match.strip())
        # Pattern for FAILED tests: matches lines ending with " FAILED [xx%]"
        failed_pattern = re.compile(r'^(.*?)\s+FAILED\s+\[.*?\]$', re.MULTILINE)
        for match in failed_pattern.findall(log):
            failed_tests.add(match.strip())
        # Pattern for ERROR tests: matches lines starting with "ERROR " followed by test name
        error_pattern = re.compile(r'^ERROR\s+(.*?)$', re.MULTILINE)
        for match in error_pattern.findall(log):
            failed_tests.add(match.strip())
        # Pattern for SKIPPED tests: matches lines ending with " SKIPPED [xx%]"
        skipped_pattern = re.compile(r'^(.*?)\s+SKIPPED\s+\[.*?\]$', re.MULTILINE)
        for match in skipped_pattern.findall(log):
            skipped_tests.add(match.strip())
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
