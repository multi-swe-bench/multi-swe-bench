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
                """ls -F
###ACTION_DELIMITER###
pip install -r tools/test-requires
###ACTION_DELIMITER###
apt-get update && apt-get install -y python-pip
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3-pip
###ACTION_DELIMITER###
pip3 install -r tools/test-requires
###ACTION_DELIMITER###
apt-get install -y python3-coverage python3-ddt python3-nose python3-ordereddict python3-yaml python3-requests python3-six python3-testtools
###ACTION_DELIMITER###
apt-get install -y python3-coverage python3-ddt python3-nose python3-yaml python3-requests python3-six python3-testtools
###ACTION_DELIMITER###
nosetests
###ACTION_DELIMITER###
python3 -m nose
###ACTION_DELIMITER###
apt-get install -y python2.7
###ACTION_DELIMITER###
pip3 install --break-system-packages -r tools/test-requires
###ACTION_DELIMITER###
python3 -m nose
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
sed -i '17 a from collections.abc import MutableMapping' falcon/util/structures.py
###ACTION_DELIMITER###
sed -i 's/collections.MutableMapping/MutableMapping/g' falcon/util/structures.py
###ACTION_DELIMITER###
python3 -m nose
###ACTION_DELIMITER###
pip3 install --break-system-packages mimeparse
###ACTION_DELIMITER###
python3 -m nose --verbose
###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i 's/inspect.getargspec/inspect.getfullargspec/g' falcon/hooks.py
###ACTION_DELIMITER###
python3 -m nose --verbose
###ACTION_DELIMITER###

###ACTION_DELIMITER###
python3 -m nose --verbose tests/test_api.py
###ACTION_DELIMITER###

###ACTION_DELIMITER###
python3 -m nose --verbose
###ACTION_DELIMITER###
sed -i '17 a from collections.abc import MutableMapping' falcon/util/structures.py && sed -i 's/collections.MutableMapping/MutableMapping/g' falcon/util/structures.py
###ACTION_DELIMITER###
ls -F tests/
###ACTION_DELIMITER###
echo 'python3 -m nose --verbose' > /home/falcon/test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python3 -m nose --verbose

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
python3 -m nose --verbose

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
python3 -m nose --verbose

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
RUN git clone https://github.com/falconry/falcon.git /home/falcon

WORKDIR /home/falcon
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("falconry", "falcon_0_2_0b1")
class FALCON_0_2_0B1(Instance):
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
        test_pattern = re.compile(r"^([^\s]+)\s+\.\.\.\s+(ok|FAIL|ERROR|SKIP)(?:\s+\(([^)]+)\))?$", re.MULTILINE)
        for match in test_pattern.finditer(log):
            test_name, status, reason = match.groups()
            if reason:
                reason = reason.split('=')[-1]
            if status == 'ok':
                passed_tests.add(test_name)
            elif status in ('FAIL', 'ERROR'):
                failed_tests.add(test_name)
            elif status == 'SKIP':
                skipped_tests.add(test_name)

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
