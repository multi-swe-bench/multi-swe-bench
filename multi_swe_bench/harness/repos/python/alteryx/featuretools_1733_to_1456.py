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
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
python -m pip install --upgrade pip
###ACTION_DELIMITER###
python -m pip install -e .
###ACTION_DELIMITER###
python -m pip install -r test-requirements.txt
###ACTION_DELIMITER###
python -m pip uninstall -y numpy && python -m pip install numpy==1.26.0
###ACTION_DELIMITER###
python -m pip install -r test-requirements.txt
###ACTION_DELIMITER###
echo 'pytest featuretools/ -v -rA -p no:cacheprovider -n 2' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip list | grep woodwork
###ACTION_DELIMITER###
python -m pip install --upgrade woodwork>=0.31.0
###ACTION_DELIMITER###
python -m pip install woodwork==0.30.0
###ACTION_DELIMITER###
python -m pip install pandas==1.5.3 && python -m pip install --force-reinstall woodwork==0.30.0
###ACTION_DELIMITER###
python -m pip install pandas==1.5.3 && python -m pip install woodwork==0.28.0
###ACTION_DELIMITER###
python -m pip install woodwork==0.27.0
###ACTION_DELIMITER###
pip show -f woodwork | grep 'serialize.py'
###ACTION_DELIMITER###
python -m pip install woodwork==0.28.0 && pip show -f woodwork | grep 'serialize.py'
###ACTION_DELIMITER###
python -m pip install woodwork==0.30.0 && python -m pip install pandas==1.5.3 && pip show -f woodwork | grep 'serialize.py'
###ACTION_DELIMITER###
python -m pip install woodwork==0.25.0 && pip show -f woodwork | grep 'serialize.py'
###ACTION_DELIMITER###
python -m pip install woodwork==0.24.0 && pip show -f woodwork | grep 'serialize.py'
###ACTION_DELIMITER###
python -m pip install woodwork==0.8.1 && pip show -f woodwork | grep 'serialize.py'
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
python -m pip install numpy==1.21.6 && python -m pip install graphviz
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
python -m pip install numpy==1.23.5
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
python -m pip install pygraphviz && python -m pip install pytest==7.4.0
###ACTION_DELIMITER###
apt-get update && apt-get install -y graphviz graphviz-dev && python -m pip install pygraphviz
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
python -m pip install graphviz==0.19.1 pytest==7.4.0 dask==2023.3.0
###ACTION_DELIMITER###
python -m pip install graphviz==0.20.1 distributed==2023.3.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
python -m pip install graphviz==0.17"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest featuretools/ -v -rA -p no:cacheprovider -n 2

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
pytest featuretools/ -v -rA -p no:cacheprovider -n 2

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
pytest featuretools/ -v -rA -p no:cacheprovider -n 2

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim with actual base image
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
RUN git clone https://github.com/alteryx/featuretools.git /home/featuretools

WORKDIR /home/featuretools
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("alteryx", "featuretools_1733_to_1456")
class FEATURETOOLS_1733_TO_1456(Instance):
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
        test_status = {}  # Track latest status for each test
        import re
        # Use regex to find all test cases with their statuses
        pattern = re.compile(r'(?:\[\s*\d+\] )?(?:\[gw\d+\] \[\s*\d+%\] )?(PASSED|SKIPPED|FAILED|ERROR)\s+(featuretools/[\w/]+\.py::[^\s]+)')
        matches = pattern.findall(log)
        for status, test_name in matches:
            test_status[test_name] = status  # Overwrite with latest status
        # Populate sets based on final statuses
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        for test, status in test_status.items():
            if status == 'PASSED':
                passed_tests.add(test)
            elif status == 'SKIPPED':
                skipped_tests.add(test)
            elif status in ('FAILED', 'ERROR'):
                failed_tests.add(test)
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
