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
                """ls evap/
###ACTION_DELIMITER###
psql --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y postgresql-client
###ACTION_DELIMITER###
ls /etc/postgresql/
###ACTION_DELIMITER###
dpkg -l | grep postgresql
###ACTION_DELIMITER###
apt-get install -y postgresql
###ACTION_DELIMITER###
service postgresql start
###ACTION_DELIMITER###
su - postgres -c 'createdb evap'
###ACTION_DELIMITER###
ls /etc/postgresql/15/main/
###ACTION_DELIMITER###
sed -i 's/local   all             postgres                                peer/local   all             postgres                                trust/' /etc/postgresql/15/main/pg_hba.conf
###ACTION_DELIMITER###
service postgresql restart
###ACTION_DELIMITER###
apt-get install -y libpq-dev build-essential
###ACTION_DELIMITER###
pip install -r requirements-travis.txt
###ACTION_DELIMITER###
python manage.py migrate
###ACTION_DELIMITER###
echo 'SECRET_KEY = "evap-travis-secret-key"' > evap/localsettings.py
###ACTION_DELIMITER###
python manage.py migrate
###ACTION_DELIMITER###
echo 'python manage.py test --verbosity 2' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
python manage.py test --verbosity 2

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
python manage.py test --verbosity 2

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
python manage.py test --verbosity 2

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
RUN git clone https://github.com/e-valuation/EvaP.git /home/EvaP

WORKDIR /home/EvaP
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("e-valuation", "EvaP_1541_to_1463")
class EVAP_1541_TO_1463(Instance):
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
        lines = log.split('\n')
        previous_line = ''
        for line in lines:
            line = line.strip()
            # Check if current line is a status line
            status_match = re.search(r'\.\.\.\s*(ok|FAIL|skipped)\s*$', line)
            if status_match:
                status = status_match.group(1)
                # Extract test name
                # Check if previous line is a test name line (starts with test_ after line number)
                prev_line_content = re.sub(r'\[\s*\d+\]\s*', '', previous_line).strip()
                if prev_line_content.startswith('test_'):
                    test_name = prev_line_content
                else:
                    # Extract test name from current line
                    current_line_match = re.search(r'\[\s*\d+\]\s*(.*?)\s*\.\.\.\s*(ok|FAIL|skipped)\s*$', line)
                    if current_line_match:
                        test_name = current_line_match.group(1).strip()
                    else:
                        # Invalid format, skip
                        continue
                # Add to appropriate set
                if status == 'ok':
                    passed_tests.add(test_name)
                elif status == 'FAIL':
                    failed_tests.add(test_name)
                elif status == 'skipped':
                    skipped_tests.add(test_name)
            # Update previous_line
            previous_line = line
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
