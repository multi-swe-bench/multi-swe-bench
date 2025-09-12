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
                """ls -la
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.4
###ACTION_DELIMITER###
apt-cache search python3.4
###ACTION_DELIMITER###
apt-cache search python3.7
###ACTION_DELIMITER###
apt-get install -y python3.7 python3.7-dev
###ACTION_DELIMITER###
apt-get install -y nodejs npm
###ACTION_DELIMITER###
npm install -g less
###ACTION_DELIMITER###
python3.7 -m ensurepip --upgrade
###ACTION_DELIMITER###
apt-get install -y python3.7-venv
###ACTION_DELIMITER###
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.7 get-pip.py
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.7 get-pip.py
###ACTION_DELIMITER###
curl https://bootstrap.pypa.io/pip/3.7/get-pip.py -o get-pip.py && python3.7 get-pip.py
###ACTION_DELIMITER###
pip3.7 install -r requirements.txt
###ACTION_DELIMITER###
pip3.7 install coverage
###ACTION_DELIMITER###
echo 'coverage run manage.py test --verbosity 2 evap.evaluation evap.staff evap.contributor evap.results evap.student evap.grades evap.rewards evap.evaluation.tests.test_misc.TestDataTest.load_test_data' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
coverage run manage.py test --verbosity 2 evap.evaluation evap.staff evap.contributor evap.results evap.student evap.grades evap.rewards evap.evaluation.tests.test_misc.TestDataTest.load_test_data

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
coverage run manage.py test --verbosity 2 evap.evaluation evap.staff evap.contributor evap.results evap.student evap.grades evap.rewards evap.evaluation.tests.test_misc.TestDataTest.load_test_data

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
coverage run manage.py test --verbosity 2 evap.evaluation evap.staff evap.contributor evap.results evap.student evap.grades evap.rewards evap.evaluation.tests.test_misc.TestDataTest.load_test_data

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
RUN git clone https://github.com/e-valuation/EvaP.git /home/EvaP

WORKDIR /home/EvaP
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("e-valuation", "EvaP_996_to_920")
class EVAP_996_TO_920(Instance):
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
        # Track the latest status of each test to avoid overlaps
        test_status = {}
        # Flexible regex to match test results (handles case, prefixes, and common statuses)
        test_pattern = re.compile(r'\b(\w+)\s*\(([\w\.]+)\)\s*\.\.\.\s*(OK|PASSED|FAIL|FAILED|SKIP|SKIPPED|ERROR|XFAIL)\b', re.IGNORECASE)
        for line in log.splitlines():
            line = line.strip()
            match = test_pattern.search(line)
            if match:
                test_method = match.group(1)
                test_class = match.group(2)
                status = match.group(3).upper()  # Normalize to uppercase
                test_name = f"{test_class}.{test_method}"
                # Update status (overwrites previous entries to keep the latest)
                if status in ("OK", "PASSED"):
                    test_status[test_name] = "passed"
                elif status in ("FAIL", "FAILED", "ERROR", "XFAIL"):
                    test_status[test_name] = "failed"
                elif status in ("SKIP", "SKIPPED"):
                    test_status[test_name] = "skipped"
        # Populate sets from the final statuses
        passed_tests = {name for name, status in test_status.items() if status == "passed"}
        failed_tests = {name for name, status in test_status.items() if status == "failed"}
        skipped_tests = {name for name, status in test_status.items() if status == "skipped"}
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
