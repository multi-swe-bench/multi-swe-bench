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
        repo_name= self.pr.repo
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
                """ls -l /home/pbench
###ACTION_DELIMITER###
ls -la /home/pbench
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python python-pip bc libjson-perl libswitch-perl realpath
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip bc libjson-perl libswitch-perl coreutils
###ACTION_DELIMITER###
pip3 install 'configtools<0.4.0' elasticsearch
###ACTION_DELIMITER###
pip3 install --break-system-packages 'configtools<0.4.0' elasticsearch
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository ppa:fkrull/deadsnakes -y
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y
###ACTION_DELIMITER###
apt-get install -y python3.5 --force-yes
###ACTION_DELIMITER###
apt-get install -y python3.7
###ACTION_DELIMITER###
wget -O /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget -O /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py
###ACTION_DELIMITER###
python3.7 /tmp/get-pip.py --break-system-packages
###ACTION_DELIMITER###
wget -O /tmp/get-pip.py https://bootstrap.pypa.io/pip/3.7/get-pip.py
###ACTION_DELIMITER###
python3.7 /tmp/get-pip.py --break-system-packages
###ACTION_DELIMITER###
apt-get install -y python3.7-distutils
###ACTION_DELIMITER###
python3.7 /tmp/get-pip.py --break-system-packages
###ACTION_DELIMITER###
python3.7 /tmp/get-pip.py --break-system-packages --ignore-installed
###ACTION_DELIMITER###
pip3.7 install --break-system-packages 'configtools<0.4.0' elasticsearch
###ACTION_DELIMITER###
pip3.7 install --break-system-packages 'setuptools<60.0.0'
###ACTION_DELIMITER###
pip3.7 install --break-system-packages 'configtools<0.4.0' elasticsearch
###ACTION_DELIMITER###
echo -e 'LANG=C ./agent/bench-scripts/unittests
LANG=C ./agent/tool-scripts/postprocess/unittests
LANG=C ./agent/util-scripts/unittests
LANG=C ./server/pbench/bin/unittests' > /home/pbench/test_commands.sh
###ACTION_DELIMITER###
chmod +x /home/pbench/test_commands.sh
###ACTION_DELIMITER###
bash /home/pbench/test_commands.sh
###ACTION_DELIMITER###
apt-get install -y python2.7 python-is-python2
###ACTION_DELIMITER###
add-apt-repository universe && apt-get update && apt-get install -y python2.7
###ACTION_DELIMITER###
ln -s /usr/bin/python3.7 /usr/bin/python && ln -s /usr/bin/python3.7 /usr/bin/python2
###ACTION_DELIMITER###
bash /home/pbench/test_commands.sh
###ACTION_DELIMITER###
rm -rf /var/tmp/pbench-test-bench /var/tmp/pbench-test-server && bash /home/pbench/test_commands.sh
###ACTION_DELIMITER###
echo 'export PYTHONWARNINGS="ignore::DeprecationWarning"' >> /home/pbench/test_commands.sh && bash /home/pbench/test_commands.sh
###ACTION_DELIMITER###
sed -i '1i export PYTHONWARNINGS="ignore::DeprecationWarning"' /home/pbench/test_commands.sh && bash /home/pbench/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
export PYTHONWARNINGS="ignore::DeprecationWarning"
LANG=C ./agent/bench-scripts/unittests
LANG=C ./agent/tool-scripts/postprocess/unittests
LANG=C ./agent/util-scripts/unittests
LANG=C ./server/pbench/bin/unittests
export PYTHONWARNINGS="ignore::DeprecationWarning"

""".replace("[[REPO_NAME]]", repo_name)
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
if ! git -C /home/[[REPO_NAME]] apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
export PYTHONWARNINGS="ignore::DeprecationWarning"
LANG=C ./agent/bench-scripts/unittests
LANG=C ./agent/tool-scripts/postprocess/unittests
LANG=C ./agent/util-scripts/unittests
LANG=C ./server/pbench/bin/unittests
export PYTHONWARNINGS="ignore::DeprecationWarning"

""".replace("[[REPO_NAME]]", repo_name)
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
if ! git -C /home/[[REPO_NAME]] apply --whitespace=nowarn  /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
export PYTHONWARNINGS="ignore::DeprecationWarning"
LANG=C ./agent/bench-scripts/unittests
LANG=C ./agent/tool-scripts/postprocess/unittests
LANG=C ./agent/util-scripts/unittests
LANG=C ./server/pbench/bin/unittests
export PYTHONWARNINGS="ignore::DeprecationWarning"

""".replace("[[REPO_NAME]]", repo_name)
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
RUN git clone https://github.com/distributed-system-analysis/pbench.git /home/pbench

WORKDIR /home/pbench
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("distributed-system-analysis", "pbench_710_to_582")
class PBENCH_710_TO_582(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re
        import json
        test_status = {}
        # Track test statuses by processing each line to capture the final status
        for line in log.splitlines():
            # Match failed tests (e.g., 'FAIL - test-11')
            fail_match = re.search(r'FAIL - (test-\d+)', line)
            if fail_match:
                test_name = fail_match.group(1)
                test_status[test_name] = 'failed'
            # Match passed tests (e.g., 'PASS - test-00')
            pass_match = re.search(r'PASS - (test-\d+)', line)
            if pass_match:
                test_name = pass_match.group(1)
                test_status[test_name] = 'passed'
            # Match skipped tests (e.g., 'SKIP - test-02')
            skip_match = re.search(r'SKIP - (test-\d+)', line)
            if skip_match:
                test_name = skip_match.group(1)
                test_status[test_name] = 'skipped'
        # Populate sets based on the final statuses
        passed_tests = {test for test, status in test_status.items() if status == 'passed'}
        failed_tests = {test for test, status in test_status.items() if status == 'failed'}
        skipped_tests = {test for test, status in test_status.items() if status == 'skipped'}
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
