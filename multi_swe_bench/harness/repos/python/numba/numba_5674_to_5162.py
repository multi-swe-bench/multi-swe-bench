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
python3 --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository -y ppa:deadsnakes/ppa
###ACTION_DELIMITER###
apt-get install -y python3.8
###ACTION_DELIMITER###
apt-get install -y python3.8-pip
###ACTION_DELIMITER###
wget https://bootstrap.pypa.io/get-pip.py && python3.8 get-pip.py
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget https://bootstrap.pypa.io/get-pip.py && python3.8 get-pip.py
###ACTION_DELIMITER###
wget https://bootstrap.pypa.io/pip/3.8/get-pip.py && python3.8 get-pip.py
###ACTION_DELIMITER###
python3.8 -m ensurepip --default-pip
###ACTION_DELIMITER###
wget -O get-pip.py https://bootstrap.pypa.io/pip/3.8/get-pip.py && python3.8 get-pip.py
###ACTION_DELIMITER###
apt-get install -y python3.8-distutils
###ACTION_DELIMITER###
wget -O get-pip.py https://bootstrap.pypa.io/pip/3.8/get-pip.py && python3.8 get-pip.py
###ACTION_DELIMITER###
python3.8 get-pip.py --user
###ACTION_DELIMITER###
python3.8 -m pip install -r requirements.txt
###ACTION_DELIMITER###
python3.8 -m pip install pytest
###ACTION_DELIMITER###
echo 'python3.8 -m pytest --no-header -rA --tb=no -p no:cacheprovider' > /home/numba/test_commands.sh
###ACTION_DELIMITER###
cat /home/numba/test_commands.sh
###ACTION_DELIMITER###
bash /home/numba/test_commands.sh
###ACTION_DELIMITER###
python3.8 -m pip uninstall -y numpy && python3.8 -m pip install numpy==1.20.3
###ACTION_DELIMITER###
bash /home/numba/test_commands.sh
###ACTION_DELIMITER###
echo 'python3.8 runtests.py -v' > /home/numba/test_commands.sh
###ACTION_DELIMITER###
bash /home/numba/test_commands.sh
###ACTION_DELIMITER###
python3.8 setup.py build_ext --inplace
###ACTION_DELIMITER###
apt-get install -y python3.8-dev
###ACTION_DELIMITER###
python3.8 setup.py build_ext --inplace
###ACTION_DELIMITER###
bash /home/numba/test_commands.sh
###ACTION_DELIMITER###
echo 'python3.8 -m pytest -v -n auto' > /home/numba/test_commands.sh
###ACTION_DELIMITER###
bash /home/numba/test_commands.sh
###ACTION_DELIMITER###
python3.8 -m pip install pytest-xdist
###ACTION_DELIMITER###
bash /home/numba/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python3.8 -m pytest -v -n auto

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
python3.8 -m pytest -v -n auto

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
python3.8 -m pytest -v -n auto

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
RUN git clone https://github.com/numba/numba.git /home/numba

WORKDIR /home/numba
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("numba", "numba_5674_to_5162")
class NUMBA_5674_TO_5162(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        import json
        # Regular expressions to match test status lines
        # Update pattern to capture SKIPPED and handle varying formats
        # Update pattern to handle varying whitespace and greedy capture
        # Capture any test name after status with flexible matching
        status_pattern = re.compile(r'\[\w+\]\s+\[\s*\d+%\]\s+(PASSED|FAILED|SKIPPED)\s+(.*?)\s*$')
        # Capture any test name after ERROR with flexible matching
        error_pattern = re.compile(r'ERROR\s+(.*?)\s*(?:-|$)')
        # Split log into lines and process each line
        for line in log.splitlines():
            # Check for PASSED, FAILED, or SKIPPED status
            status_match = status_pattern.search(line)
            if status_match:
                status = status_match.group(1)
                test_name = status_match.group(2).strip()
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
            # Check for ERROR status
            error_match = error_pattern.search(line)
            if error_match:
                test_name = error_match.group(1).strip()
                failed_tests.add(test_name)
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
