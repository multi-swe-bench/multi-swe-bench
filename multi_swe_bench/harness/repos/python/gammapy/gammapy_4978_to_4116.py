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
        return "python:3.11-slim"
    
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
pip install --upgrade pip && pip install astropy click cython 'numpy>1.20' 'pydantic<2.0' pyyaml 'regions>=0.5' 'matplotlib>=3.4' 'scipy!=1.10' 'iminuit>=2.8.0' extension-helpers codecov 'pytest==6' pytest-astropy pytest-cov pytest-xdist coverage requests tqdm
###ACTION_DELIMITER###
gammapy info
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
gammapy info
###ACTION_DELIMITER###
pip install astropy==6.0.0
###ACTION_DELIMITER###
gammapy info
###ACTION_DELIMITER###
pip install matplotlib==3.5.3
###ACTION_DELIMITER###
gammapy info
###ACTION_DELIMITER###
python -m pytest -v gammapy
###ACTION_DELIMITER###
pip install pytest==7.2.0
###ACTION_DELIMITER###
python -m pytest -v gammapy
###ACTION_DELIMITER###
pip install --upgrade pytest-cov
###ACTION_DELIMITER###
pip install astropy==5.3.0 && pip install --upgrade pytest-astropy pytest-xdist pytest-mock
###ACTION_DELIMITER###
python -m pytest -v gammapy
###ACTION_DELIMITER###
pip install astropy==5.0.0
###ACTION_DELIMITER###
pip install setuptools==65.0.0 && pip install astropy==5.3.0
###ACTION_DELIMITER###
python -m pytest -v gammapy
###ACTION_DELIMITER###
pip install -e . && python -m pytest -v gammapy
###ACTION_DELIMITER###
pip install scipy==1.9.3 && python -m pytest -v gammapy
###ACTION_DELIMITER###
echo 'python -m pytest -v gammapy' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python -m pytest -v gammapy

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
python -m pytest -v gammapy

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
python -m pytest -v gammapy

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

# Choose an appropriate base image based on the project's requirements - replace python:3.11-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.11-slim

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
RUN git clone https://github.com/gammapy/gammapy.git /home/gammapy

WORKDIR /home/gammapy
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("gammapy", "gammapy_4978_to_4116")
class GAMMAPY_4978_TO_4116(Instance):
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
        # Regex patterns to match test names and statuses
        passed_pattern = re.compile(r'.*?([\w/]+/tests/[\w.]+\.py::[\w\[\]_-]+(?:\[[^\]]+\])?)\s+PASSED')
        skipped_pattern = re.compile(r'.*?([\w/]+/tests/[\w.]+\.py::[\w\[\]_-]+(?:\[[^\]]+\])?)\s+SKIPPED')
        failed_pattern = re.compile(r'.*?FAILED\s+([\w/]+/tests/[\w.]+\.py::[\w\[\]_-]+(?:\[[^\]]+\])?)')
        # Extract test names for each status
        passed_tests.update(passed_pattern.findall(log))
        skipped_tests.update(skipped_pattern.findall(log))
        failed_tests.update(failed_pattern.findall(log))
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
