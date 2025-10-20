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
echo 'pytest -v -rA tests' > test_commands.sh
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
pip install --requirement requirements-dev-test.txt --constraint constraints-dev.txt
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pandas
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install ruamel.yaml
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pyparsing
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install ipython
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install scipy
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install tqdm
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install altair
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install ipywidgets
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install tzlocal
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
locale-gen en_US.UTF-8
###ACTION_DELIMITER###
apt-get update && apt-get install -y locales
###ACTION_DELIMITER###
locale-gen en_US.UTF-8
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
locale
###ACTION_DELIMITER###
export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8
###ACTION_DELIMITER###
locale -a
###ACTION_DELIMITER###
export LANG=C.utf8 && export LC_ALL=C.utf8
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/^# *en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
###ACTION_DELIMITER###
export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8 && bash test_commands.sh
###ACTION_DELIMITER###
pip install pandas==1.5.3
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.23.5
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v -rA tests

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
pytest -v -rA tests

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
pytest -v -rA tests

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
RUN git clone https://github.com/great-expectations/great_expectations.git /home/great_expectations

WORKDIR /home/great_expectations
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("great-expectations", "great_expectations_5628_to_5436")
class GREAT_EXPECTATIONS_5628_TO_5436(Instance):
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
        # TODO: Implement the parse_log function
        # Use regular expressions to find test names and their statuses
        # Pattern for skipped tests: captures test name before ' SKIPPED'
        skipped_pattern = re.compile(r'(tests/.*?) SKIPPED')
        # Pattern for failed tests: captures test name after 'FAILED '
        failed_pattern = re.compile(r'FAILED (tests/.*)')
        # Pattern for passed tests: captures test name before ' PASSED'
        passed_pattern = re.compile(r'(tests/.*?) PASSED')
        for line in log.splitlines():
            line = line.strip()
            # Check for skipped tests
            skipped_match = skipped_pattern.search(line)
            if skipped_match:
                test_name = skipped_match.group(1).strip()
                skipped_tests.add(test_name)
            # Check for failed tests
            failed_match = failed_pattern.search(line)
            if failed_match:
                test_name = failed_match.group(1).strip()
                failed_tests.add(test_name)
            # Check for passed tests
            passed_match = passed_pattern.search(line)
            if passed_match:
                test_name = passed_match.group(1).strip()
                passed_tests.add(test_name)
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
