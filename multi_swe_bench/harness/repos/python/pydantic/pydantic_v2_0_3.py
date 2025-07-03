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
                """ls -la
###ACTION_DELIMITER###
pdm --version
###ACTION_DELIMITER###
pip install pdm
###ACTION_DELIMITER###
pdm install --group :all
###ACTION_DELIMITER###
pdm lock --update-reuse
###ACTION_DELIMITER###
pdm install --group :all
###ACTION_DELIMITER###
echo 'pdm run coverage run -m pytest --durations=10' > /home/pydantic/test_commands.sh && chmod +x /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
pdm add --dev coverage
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
pdm add --dev pytest
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
pdm add --dev pytest-benchmark
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
pdm fix
###ACTION_DELIMITER###
pdm install --group :all
###ACTION_DELIMITER###
pdm add -dG :all -e .
###ACTION_DELIMITER###
pdm add -e .
###ACTION_DELIMITER###
pdm install
###ACTION_DELIMITER###
pdm venv list
###ACTION_DELIMITER###
/home/pydantic/.venv/bin/pip install -e .
###ACTION_DELIMITER###
ls /home/pydantic/.venv/bin/
###ACTION_DELIMITER###
/home/pydantic/.venv/bin/python -m ensurepip
###ACTION_DELIMITER###
/home/pydantic/.venv/bin/pip install -e .
###ACTION_DELIMITER###
curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py && /home/pydantic/.venv/bin/python get-pip.py && rm get-pip.py
###ACTION_DELIMITER###
wget https://bootstrap.pypa.io/get-pip.py -O get-pip.py && /home/pydantic/.venv/bin/python get-pip.py && rm get-pip.py
###ACTION_DELIMITER###
.venv/bin/python -m pytest --durations=10
###ACTION_DELIMITER###
.venv/bin/python -m pip install typing-extensions annotated-types pydantic-core dirty_equals pytest pytest-benchmark coverage
###ACTION_DELIMITER###
.venv/bin/python -m pip install -e .
###ACTION_DELIMITER###
.venv/bin/python -m pytest --durations=10
###ACTION_DELIMITER###
.venv/bin/python -m pip install pytest-examples
###ACTION_DELIMITER###
.venv/bin/python -m pytest --durations=10
###ACTION_DELIMITER###
echo '.venv/bin/python -m pytest --durations=10' > /home/pydantic/test_commands.sh && chmod +x /home/pydantic/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
.venv/bin/python -m pytest --durations=10

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
.venv/bin/python -m pytest --durations=10

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
.venv/bin/python -m pytest --durations=10

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
RUN git clone https://github.com/pydantic/pydantic.git /home/pydantic

WORKDIR /home/pydantic
RUN git reset --hard
RUN git checkout 1aac3d8e83ab8731885fcf116fa4c2e8f48e8e55

RUN git checkout {pr.base.sha}"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pydantic", "pydantic_v2_0_3")
class PYDANTIC_V2_0_3(Instance):
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
        import json
        # Extract all test names from timing lines (with 'call' and '::')
        timing_pattern = re.compile(r"^.*call\s+([\w./\-]+::[\w\[\]_.-]+)", re.MULTILINE)
        all_tests = set(timing_pattern.findall(log))
        # Extract failed and error test names from 'FAILED ...' and 'ERROR ...' lines
        failed_pattern = re.compile(r"^FAILED ([\w./\-]+::[\w\[\]_.-]+)", re.MULTILINE)
        error_pattern = re.compile(r"^ERROR ([\w./\-]+::[\w\[\]_.-]+)", re.MULTILINE)
        failed_tests.update(failed_pattern.findall(log))
        failed_tests.update(error_pattern.findall(log))
        # Passed tests: all tests in timing lines not in failed_tests
        passed_tests = all_tests - failed_tests
        # Skipped tests: not extractable by name from these logs
        # (left empty)
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
