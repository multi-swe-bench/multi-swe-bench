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
                """wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && bash miniconda.sh -b -p /home/miniconda
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && bash miniconda.sh -b -p /home/miniconda
###ACTION_DELIMITER###
export PATH="/home/miniconda/bin:$PATH"
###ACTION_DELIMITER###
conda env create -f environment.yml
###ACTION_DELIMITER###
conda install -y -n base -c conda-forge mamba
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
###ACTION_DELIMITER###
conda install -y -n base -c conda-forge mamba
###ACTION_DELIMITER###
mamba env create -f environment.yml
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip install -e .[test]
###ACTION_DELIMITER###
pip install 'setuptools<60.0'
###ACTION_DELIMITER###
pip install -e .[test]
###ACTION_DELIMITER###
pip install --no-build-isolation 'astropy~=5.0'
###ACTION_DELIMITER###
rm -rf /home/miniconda && pip3 install -e .[test]
###ACTION_DELIMITER###
echo 'pytest --no-header -rA --tb=no -p no:cacheprovider' > /home/ctapipe/test_commands.sh
###ACTION_DELIMITER###
cat /home/ctapipe/test_commands.sh
###ACTION_DELIMITER###
bash /home/ctapipe/test_commands.sh
###ACTION_DELIMITER###
pip list | grep pytest
###ACTION_DELIMITER###
pip3 install pytest
###ACTION_DELIMITER###
pip3 show pytest
###ACTION_DELIMITER###
echo 'python3 -m pytest --no-header -rA --tb=no -p no:cacheprovider' > /home/ctapipe/test_commands.sh
###ACTION_DELIMITER###
bash /home/ctapipe/test_commands.sh
###ACTION_DELIMITER###
pip3 install pytest-astropy-header
###ACTION_DELIMITER###
bash /home/ctapipe/test_commands.sh
###ACTION_DELIMITER###
pip3 install pandas importlib_resources tomli
###ACTION_DELIMITER###
echo 'python3 -m pytest -v --no-header -rA --tb=short -p no:cacheprovider' > /home/ctapipe/test_commands.sh
###ACTION_DELIMITER###
bash /home/ctapipe/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
python3 -m pytest -v --no-header -rA --tb=short -p no:cacheprovider

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
python3 -m pytest -v --no-header -rA --tb=short -p no:cacheprovider

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
python3 -m pytest -v --no-header -rA --tb=short -p no:cacheprovider

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
RUN git clone https://github.com/cta-observatory/ctapipe.git /home/ctapipe

WORKDIR /home/ctapipe
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("cta-observatory", "ctapipe_1967_to_unknown")
class CTAPIPE_1967_TO_UNKNOWN(Instance):
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
        # Parse log lines to extract test names and statuses
        lines = log.split('\n')
        # Regex patterns for different test statuses
        passed_pattern = re.compile(r'^(.*?)\s+PASSED\s+\[\s*\d+%\]')
        failed_pattern = re.compile(r'^FAILED\s+(.*?)\s+-\s+.*')
        skipped_pattern = re.compile(r'^(.*?)\s+SKIPPED\s+\[\s*\d+%\]')  # Adjust pattern if needed
        for line in lines:
            line = line.strip()
            # Check for passed tests
            passed_match = passed_pattern.match(line)
            if passed_match:
                test_name = passed_match.group(1).strip()
                passed_tests.add(test_name)
            # Check for failed tests
            failed_match = failed_pattern.match(line)
            if failed_match:
                test_name = failed_match.group(1).strip()
                failed_tests.add(test_name)
            # Check for skipped tests
            skipped_match = skipped_pattern.match(line)
            if skipped_match:
                test_name = skipped_match.group(1).strip()
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
