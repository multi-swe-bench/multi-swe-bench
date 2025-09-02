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
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
pip install torch
###ACTION_DELIMITER###
pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip uninstall -y torch && pip install torch==1.13.1
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
pytest -v --no-header -rA -p no:cacheprovider
###ACTION_DELIMITER###
pip install --force-reinstall scikit-learn
###ACTION_DELIMITER###
pytest -v --no-header -rA -p no:cacheprovider
###ACTION_DELIMITER###
pip install scikit-learn==1.0.2
###ACTION_DELIMITER###
pytest -v --no-header -rA -p no:cacheprovider --ignore=tests/ignite/contrib/metrics/regression/test_canberra_metric.py --ignore=tests/ignite/contrib/metrics/regression/test_manhattan_distance.py
###ACTION_DELIMITER###
pip install numpy==1.23.5
###ACTION_DELIMITER###
pytest -v --no-header -rA -p no:cacheprovider --ignore=tests/ignite/contrib/metrics/regression/test_canberra_metric.py --ignore=tests/ignite/contrib/metrics/regression/test_manhattan_distance.py
###ACTION_DELIMITER###
echo 'pytest -v -n auto --no-header -rA --tb=no -p no:cacheprovider --ignore=tests/ignite/contrib/metrics/regression/test_canberra_metric.py --ignore=tests/ignite/contrib/metrics/regression/test_manhattan_distance.py' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v -n auto --no-header -rA --tb=no -p no:cacheprovider --ignore=tests/ignite/contrib/metrics/regression/test_canberra_metric.py --ignore=tests/ignite/contrib/metrics/regression/test_manhattan_distance.py

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
pytest -v -n auto --no-header -rA --tb=no -p no:cacheprovider --ignore=tests/ignite/contrib/metrics/regression/test_canberra_metric.py --ignore=tests/ignite/contrib/metrics/regression/test_manhattan_distance.py

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
pytest -v -n auto --no-header -rA --tb=no -p no:cacheprovider --ignore=tests/ignite/contrib/metrics/regression/test_canberra_metric.py --ignore=tests/ignite/contrib/metrics/regression/test_manhattan_distance.py

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
RUN git clone https://github.com/pytorch/ignite.git /home/ignite

WORKDIR /home/ignite
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pytorch", "ignite_2019_to_1756")
class IGNITE_2019_TO_1756(Instance):
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
        # Remove ANSI escape codes from the log content
        cleaned_log = re.sub(r'\x1b\[[0-9;]*m', '', log)
        # Split into individual lines
        lines = cleaned_log.split('\n')
        for line in lines:
            # Check for test status and extract test name
            if 'PASSED' in line:
                match = re.search(r'tests/[^:]+::[^ ]+', line)
                if match:
                    passed_tests.add(match.group(0))
            elif 'SKIPPED' in line:
                match = re.search(r'tests/[^:]+::[^ ]+', line)
                if match:
                    skipped_tests.add(match.group(0))
            elif 'FAILED' in line:
                match = re.search(r'tests/[^:]+::[^ ]+', line)
                if match:
                    failed_tests.add(match.group(0))
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
