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
        return "ubuntu:22.04"
    
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
                """ls
###ACTION_DELIMITER###
ls evap
###ACTION_DELIMITER###
echo 'SECRET_KEY = "django-insecure-test-key-for-evap"' > evap/localsettings.py
###ACTION_DELIMITER###
service postgresql start
###ACTION_DELIMITER###
dpkg -l postgresql
###ACTION_DELIMITER###
apt-get update && apt-get install -y postgresql
###ACTION_DELIMITER###
pg_ctlcluster 14 main start
###ACTION_DELIMITER###
su postgres -c 'createdb evap'
###ACTION_DELIMITER###
python3 manage.py migrate
###ACTION_DELIMITER###
apt-get install -y python3
###ACTION_DELIMITER###
apt-get install -y python3-pip
###ACTION_DELIMITER###
pip3 install -r requirements.txt
###ACTION_DELIMITER###
apt-get install -y libpq-dev
###ACTION_DELIMITER###
pip3 install -r requirements.txt
###ACTION_DELIMITER###
sed -i 's/psycopg2-binary == 2.7.5/psycopg2-binary == 2.8.6/' requirements.txt
###ACTION_DELIMITER###
pip3 install -r requirements.txt
###ACTION_DELIMITER###
python3 manage.py migrate
###ACTION_DELIMITER###
sed -i 's/local   all             postgres                                peer/local   all             postgres                                trust/' /etc/postgresql/14/main/pg_hba.conf
###ACTION_DELIMITER###
pg_ctlcluster 14 main restart
###ACTION_DELIMITER###
python3 manage.py migrate
###ACTION_DELIMITER###
echo 'python3 manage.py test --verbosity 2' > test_commands.sh
###ACTION_DELIMITER###
python3 manage.py test --verbosity 2
###ACTION_DELIMITER###
sed -i 's/WebTest==2.0.30/WebTest==2.0.37/' requirements.txt && sed -i 's/django-webtest==1.9.7/django-webtest==1.10.1/' requirements.txt
###ACTION_DELIMITER###
pip3 install -r requirements.txt
###ACTION_DELIMITER###
sed -i 's/WebTest\s*==\s*2.0.30/WebTest==2.0.37/' requirements.txt && sed -i 's/django-webtest\s*==\s*1.9.7/django-webtest==1.10.1/' requirements.txt && pip3 install -r requirements.txt
###ACTION_DELIMITER###
sed -i 's/django-webtest==1.9.7/django-webtest==1.9.13/' requirements.txt && sed -i 's/WebTest==2.0.30/WebTest==2.0.37/' requirements.txt && pip3 install -r requirements.txt
###ACTION_DELIMITER###
sed -i 's/django-webtest==1.9.7/django-webtest==1.9.13/' requirements.txt && sed -i 's/WebTest==2.0.30/WebTest==2.0.37/' requirements.txt && pip3 install -r requirements.txt
###ACTION_DELIMITER###
sed -i 's/django-webtest==1.9.7/django-webtest==1.9.13/' requirements.txt && sed -i 's/WebTest==2.0.30/WebTest==2.0.37/' requirements.txt && pip3 install -r requirements.txt
###ACTION_DELIMITER###
sed -i 's/django-webtest==1\.9\.7/django-webtest==1.9.13/' requirements.txt && sed -i 's/WebTest==2\.0\.30/WebTest==2.0.37/' requirements.txt && pip3 install -r requirements.txt
###ACTION_DELIMITER###
sed -i 's/django-webtest==1.9.7/django-webtest==1.9.13/' requirements.txt && sed -i 's/WebTest==2.0.30/WebTest==2.0.37/' requirements.txt && pip3 install -r requirements.txt
###ACTION_DELIMITER###
sed -i 's/^django-webtest==.*/django-webtest==1.9.13/' requirements.txt && sed -i 's/^WebTest==.*/WebTest==2.0.37/' requirements.txt && pip3 install -r requirements.txt
###ACTION_DELIMITER###
sed -i 's/^django-webtest==.*/django-webtest==1.9.13/' requirements.txt && sed -i 's/^WebTest==.*/WebTest==2.0.35/' requirements.txt && pip3 install -r requirements.txt
###ACTION_DELIMITER###
python3 manage.py test --verbosity 2"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
python3 manage.py test --verbosity 2

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
python3 manage.py test --verbosity 2

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
python3 manage.py test --verbosity 2

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:22.04 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:22.04

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


@Instance.register("e-valuation", "EvaP_1416_to_1360")
class EVAP_1416_TO_1360(Instance):
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
        passed_tests = set[str]()
        failed_tests = set[str]()
        skipped_tests = set[str]()
        import re
        # Expanded patterns to include more statuses and allow dots in test names
        # Matches lines with varied statuses and test names: e.g., [ 310] test_wrong_state (module) ... ok or test.wrong_state ... pass
        status_pattern = re.compile(r'(?:\[\s*\d+\]\s*)?(test_[\w.]+)\s*(?:\(.*?\))?\s*\.\.\.\s*(ok|passed|pass|skipped|failed|fail|error)', re.IGNORECASE)
        # Matches error lines with varied error indicators and test names: e.g., [ 603] ERROR: test_put_delegates (module) or FAIL: test.put_delegates
        error_pattern = re.compile(r'(?:\[\s*\d+\]\s*)?(error|failed|fail):\s*(test_[\w.]+)\s*(?:\(.*?\))?', re.IGNORECASE)
        # Extract tests from status lines
        for match in status_pattern.finditer(log):
            test_name, status = match.groups()
            status = status.lower()
            if status in ('ok', 'passed'):
                passed_tests.add(test_name)
            elif status == 'skipped':
                skipped_tests.add(test_name)
            elif status in ('failed', 'error'):
                failed_tests.add(test_name)
        # Extract failed tests from error lines
        for match in error_pattern.finditer(log):
            _, test_name = match.groups()
            failed_tests.add(test_name)
        # Remove overlap: prioritize failed status
        passed_tests -= failed_tests
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
