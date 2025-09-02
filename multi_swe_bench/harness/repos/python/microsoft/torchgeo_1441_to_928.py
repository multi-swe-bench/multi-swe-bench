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
        return "pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime"
    
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
                """ls .github/workflows
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgl1-mesa-glx libxrender1 xvfb
###ACTION_DELIMITER###
export MPLBACKEND=Agg && Xvfb :99 -screen 0 1024x768x16 &
###ACTION_DELIMITER###
export DISPLAY=:99
###ACTION_DELIMITER###
pip install -r requirements/required.txt -r requirements/datasets.txt -r requirements/tests.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip install -r requirements/required.txt -r requirements/datasets.txt -r requirements/tests.txt
###ACTION_DELIMITER###
echo 'pytest -v --cov=torchgeo --cov-report=xml --durations=10' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install python-multipart
###ACTION_DELIMITER###
echo 'pytest -v --cov=torchgeo --cov-report=xml --durations=10 -W ignore::PendingDeprecationWarning' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --cov=torchgeo --cov-report=xml --durations=10 -W ignore::DeprecationWarning -W ignore::PendingDeprecationWarning' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install --reinstall -y unrar && pip install --force-reinstall rarfile
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v --cov=torchgeo --cov-report=xml --durations=10 -W ignore::DeprecationWarning -W ignore::PendingDeprecationWarning

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
pytest -v --cov=torchgeo --cov-report=xml --durations=10 -W ignore::DeprecationWarning -W ignore::PendingDeprecationWarning

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
pytest -v --cov=torchgeo --cov-report=xml --durations=10 -W ignore::DeprecationWarning -W ignore::PendingDeprecationWarning

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
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

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
RUN git clone https://github.com/microsoft/torchgeo.git /home/torchgeo

WORKDIR /home/torchgeo
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("microsoft", "torchgeo_1441_to_928")
class TORCHGEO_1441_TO_928(Instance):
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
        passed_tests = set[str]() # Tests that passed successfully
        failed_tests = set[str]() # Tests that failed
        skipped_tests = set[str]() # Tests that were skipped
        import re
        lines = log.split('\n')
        for line in lines:
            line = line.strip()
            # Extract passed tests
            # Skip leading line numbers in brackets (e.g., [  11])
            line = re.sub(r'^\[.*?\]\s*', '', line)
            # Extract passed tests
            passed_match = re.match(r'^(.*?)\s+PASSED\b', line)
            if passed_match:
                test_name = passed_match.group(1).strip()
                passed_tests.add(test_name)
            # Extract failed tests
            failed_match = re.match(r'^(.*?)\s+FAILED\b', line)
            if not failed_match:
                failed_match = re.match(r'^FAILED\s+(.*?)(\s+-|$)', line)
            if failed_match:
                test_name = failed_match.group(1).strip()
                failed_tests.add(test_name)
            # Extract skipped tests
            skipped_match = re.match(r'^(.*?)\s+SKIPPED\b', line)
            if not skipped_match:
                skipped_match = re.match(r'^SKIPPED\s+(.*?)(\s+-|$)', line)
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
