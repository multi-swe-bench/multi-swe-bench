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
                """apt-get update && apt-get install -y python3.10 python3.10-venv python3.10-dev build-essential libpq-dev default-libmysqlclient-dev unixodbc-dev libsqlite3-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository -y ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.10 python3.10-venv python3.10-dev build-essential libpq-dev default-libmysqlclient-dev unixodbc-dev libsqlite3-dev
###ACTION_DELIMITER###
python3.10 -m venv venv
###ACTION_DELIMITER###
./venv/bin/pip install -e . pytest!=3.9.1,!=3.9.2 pytest-xdist mock psycopg2-binary mysqlclient pyodbc
###ACTION_DELIMITER###
apt-get install -y pkg-config
###ACTION_DELIMITER###
./venv/bin/pip install -e . pytest!=3.9.1,!=3.9.2 pytest-xdist mock psycopg2-binary mysqlclient pyodbc
###ACTION_DELIMITER###
echo './venv/bin/pytest -v test/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
./venv/bin/pip install pytest==7.4.0
###ACTION_DELIMITER###
./venv/bin/pip install pytest==6.2.5
###ACTION_DELIMITER###
./venv/bin/pip install pytest-xdist==2.5.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
./venv/bin/pip install pytest==5.4.3 pytest-xdist==1.34.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.8 python3.8-venv python3.8-dev
###ACTION_DELIMITER###
rm -rf venv && python3.8 -m venv venv
###ACTION_DELIMITER###
./venv/bin/pip install -e . pytest==6.2.5 pytest-xdist==2.5.0 mock psycopg2-binary mysqlclient pyodbc
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'PYTHONWARNINGS=ignore ./venv/bin/pytest -v test/' > test_commands.sh
###ACTION_DELIMITER###
echo './venv/bin/pytest -v --disable-warnings test/' > test_commands.sh
###ACTION_DELIMITER###
./venv/bin/pip install pytest==6.0.0 pytest-xdist==2.1.0 && echo './venv/bin/pytest -v test/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
./venv/bin/pip install tox && ./venv/bin/tox
###ACTION_DELIMITER###
sed -i 's/passenv=ORACLE_HOME NLS_LANG TOX_POSTGRESQL TOX_MYSQL TOX_ORACLE TOX_MSSQL TOX_SQLITE TOX_SQLITE_FILE TOX_WORKERS/passenv=ORACLE_HOME,NLS_LANG,TOX_POSTGRESQL,TOX_MYSQL,TOX_ORACLE,TOX_MSSQL,TOX_SQLITE,TOX_SQLITE_FILE,TOX_WORKERS/' tox.ini && ./venv/bin/tox
###ACTION_DELIMITER###
sed -i 's/pytest!=3.9.1,!=3.9.2/pytest==6.2.5/' tox.ini && ./venv/bin/tox
###ACTION_DELIMITER###
sed -i 's/pytest-xdist/pytest-xdist==1.34.0/' tox.ini && ./venv/bin/tox
###ACTION_DELIMITER###
sed -i 's/pytest==6.2.5/pytest==5.4.3/' tox.ini && sed -i 's/pytest-xdist==1.34.0/pytest-xdist==1.34.0/' tox.ini && ./venv/bin/tox -e py -- -W ignore::DeprecationWarning
###ACTION_DELIMITER###
echo './venv/bin/pytest -v -W ignore::DeprecationWarning -n4 --max-worker-restart=5 test/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
./venv/bin/pip install pytest-xdist==1.34.0 && echo './venv/bin/pytest -v -W ignore::DeprecationWarning -n4 --max-worker-restart=5 test/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
./venv/bin/pytest -v -W ignore::DeprecationWarning -n4 --max-worker-restart=5 test/

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
./venv/bin/pytest -v -W ignore::DeprecationWarning -n4 --max-worker-restart=5 test/

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
./venv/bin/pytest -v -W ignore::DeprecationWarning -n4 --max-worker-restart=5 test/

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
RUN git clone https://github.com/sqlalchemy/sqlalchemy.git /home/sqlalchemy

WORKDIR /home/sqlalchemy
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("sqlalchemy", "sqlalchemy_5232_to_5062")
class SQLALCHEMY_5232_TO_5062(Instance):
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
        import json
        # Parse passed tests
        passed_pattern = r"PASSED (test/.*?)(?=\s|$)"
        passed_matches = re.findall(passed_pattern, log)
        passed_tests.update(passed_matches)
        # Parse failed tests
        failed_pattern = r"FAILED (test/.*?)(?=\s|$)"
        failed_matches = re.findall(failed_pattern, log)
        failed_tests.update(failed_matches)
        # Parse skipped tests
        skipped_pattern = r"SKIPPED.*?: '(.*?)'"
        skipped_matches = re.findall(skipped_pattern, log)
        skipped_tests.update(skipped_matches)
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
