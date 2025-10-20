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
        return "python:3.11-slim-bookworm"
    
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
ls -la src
###ACTION_DELIMITER###
apt-get update && apt-get install -y redis-server
###ACTION_DELIMITER###
python src/manage.py check
###ACTION_DELIMITER###
pip install pipenv
###ACTION_DELIMITER###
export MYSQLCLIENT_CFLAGS="-I/usr/include/mysql" && export MYSQLCLIENT_LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lmysqlclient" && pipenv install --dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y libpq-dev
###ACTION_DELIMITER###
export MYSQLCLIENT_CFLAGS="-I/usr/include/mysql" && export MYSQLCLIENT_LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lmysqlclient" && pipenv install --dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
export MYSQLCLIENT_CFLAGS="-I/usr/include/mysql" && export MYSQLCLIENT_LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lmysqlclient" && pipenv install --dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y libmysqlclient-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y libmariadb-dev-compat libmariadb-dev
###ACTION_DELIMITER###
export MYSQLCLIENT_CFLAGS="-I/usr/include/mysql" && export MYSQLCLIENT_LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lmariadb" && pipenv install --dev
###ACTION_DELIMITER###
pipenv run pip list
###ACTION_DELIMITER###
echo 'pipenv run pytest --verbose --ds=paperless.settings --no-header -rA --tb=no -p no:cacheprovider' > /home/paperless-ngx/test_commands.sh
###ACTION_DELIMITER###
cat /home/paperless-ngx/test_commands.sh
###ACTION_DELIMITER###
bash /home/paperless-ngx/test_commands.sh
###ACTION_DELIMITER###
echo 'PYTHONPATH=src pipenv run pytest --verbose --ds=paperless.settings --no-header -rA --tb=no -p no:cacheprovider' > /home/paperless-ngx/test_commands.sh
###ACTION_DELIMITER###
cat /home/paperless-ngx/test_commands.sh
###ACTION_DELIMITER###
bash /home/paperless-ngx/test_commands.sh
###ACTION_DELIMITER###
export PAPERLESS_SECRET_KEY='dummy-secret-key' && pipenv run python src/manage.py migrate && bash /home/paperless-ngx/test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y tesseract-ocr
###ACTION_DELIMITER###
apt-get update && apt-get install -y ghostscript poppler-utils libzbar0 imagemagick
###ACTION_DELIMITER###
export PAPERLESS_SECRET_KEY='dummy-secret-key' && pipenv run python src/manage.py migrate && bash /home/paperless-ngx/test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libmagic1
###ACTION_DELIMITER###
export PAPERLESS_SECRET_KEY='dummy-secret-key' && pipenv run python src/manage.py migrate && bash /home/paperless-ngx/test_commands.sh
###ACTION_DELIMITER###
mkdir -p consume media
###ACTION_DELIMITER###
export PAPERLESS_SECRET_KEY='dummy-secret-key' && pipenv run python src/manage.py migrate && bash /home/paperless-ngx/test_commands.sh
###ACTION_DELIMITER###
redis-server --daemonize yes && export PAPERLESS_SECRET_KEY='dummy-secret-key' && pipenv run python src/manage.py migrate && bash /home/paperless-ngx/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
PYTHONPATH=src pipenv run pytest --verbose --ds=paperless.settings --no-header -rA --tb=no -p no:cacheprovider

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
PYTHONPATH=src pipenv run pytest --verbose --ds=paperless.settings --no-header -rA --tb=no -p no:cacheprovider

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
PYTHONPATH=src pipenv run pytest --verbose --ds=paperless.settings --no-header -rA --tb=no -p no:cacheprovider

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
FROM python:3.11-slim-bookworm

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
RUN git clone https://github.com/paperless-ngx/paperless-ngx.git /home/paperless-ngx

WORKDIR /home/paperless-ngx
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("paperless-ngx", "paperless_ngx_4179_to_4171")
class PAPERLESS_NGX_4179_TO_4171(Instance):
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
        # Regex pattern to match test lines with status either before or after the test name
        pattern = re.compile(r'(?P<test1>src/[\w/\.::\-]+) (?P<status1>PASSED|FAILED|SKIPPED)|(?P<status2>PASSED|FAILED|SKIPPED) (?P<test2>src/[\w/\.::\-]+)')
        for match in pattern.finditer(log):
            test1 = match.group('test1')
            status1 = match.group('status1')
            status2 = match.group('status2')
            test2 = match.group('test2')
            if test1 and status1:
                test_name = test1
                status = status1
            elif test2 and status2:
                test_name = test2
                status = status2
            else:
                continue  # No match
            # Add to the appropriate set
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
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
