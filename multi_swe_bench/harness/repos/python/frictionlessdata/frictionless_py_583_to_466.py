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
                """ls
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip python3-dev python3-venv build-essential libpq-dev libssl-dev libxml2-dev libxslt1-dev
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
make test-ci
###ACTION_DELIMITER###
make format
###ACTION_DELIMITER###
make test-ci
###ACTION_DELIMITER###
pytest --cov frictionless --cov-report term-missing --cov-fail-under 80 --ci
###ACTION_DELIMITER###
pip install moto==4.2.7
###ACTION_DELIMITER###
pytest -v --cov frictionless --cov-report term-missing --cov-fail-under 80 --ci
###ACTION_DELIMITER###
apt-get update && apt-get install -y postgresql mysql-server && service postgresql start && service mysql start && su - postgres -c 'createdb testdb' && su - postgres -c "psql -c 'CREATE USER testuser WITH PASSWORD \'testpass\';'" && su - postgres -c "psql -c 'GRANT ALL PRIVILEGES ON DATABASE testdb TO testuser;'" && mysql -u root -e 'CREATE DATABASE testdb;' && mysql -u root -e "CREATE USER 'testuser'@'localhost' IDENTIFIED BY 'testpass';" && mysql -u root -e "GRANT ALL PRIVILEGES ON testdb.* TO 'testuser'@'localhost';" && mysql -u root -e 'FLUSH PRIVILEGES;' && export POSTGRESQL_URL='postgresql://testuser:testpass@localhost/testdb' && export MYSQL_URL='mysql://testuser:testpass@localhost/testdb'
###ACTION_DELIMITER###
apt-get update && apt-get install -y postgresql mysql-server && service postgresql start && service mysql start && su - postgres -c 'createdb testdb' && su - postgres -c "psql -c 'CREATE USER testuser WITH PASSWORD \'testpass\';'" && su - postgres -c "psql -c 'GRANT ALL PRIVILEGES ON DATABASE testdb TO testuser;'" && mysql -u root -e 'CREATE DATABASE testdb;' && mysql -u root -e "CREATE USER 'testuser'@'localhost' IDENTIFIED BY 'testpass';" && mysql -u root -e "GRANT ALL PRIVILEGES ON testdb.* TO 'testuser'@'localhost';" && mysql -u root -e 'FLUSH PRIVILEGES;' && export POSTGRESQL_URL='postgresql://testuser:testpass@localhost/testdb' && export MYSQL_URL='mysql://testuser:testpass@localhost/testdb'
###ACTION_DELIMITER###
export POSTGRESQL_URL='postgresql://testuser:testpass@localhost/testdb' && export MYSQL_URL='mysql://testuser:testpass@localhost/testdb' && pytest -v --cov frictionless --cov-report term-missing --cov-fail-under 80 --ci
###ACTION_DELIMITER###
pip install mysqlclient psycopg2-binary && service postgresql restart && service mysql restart && export POSTGRESQL_URL='postgresql://testuser:testpass@localhost/testdb' && export MYSQL_URL='mysql://testuser:testpass@localhost/testdb' && pytest -v --cov frictionless --cov-report term-missing --cov-fail-under 80 --ci
###ACTION_DELIMITER###
apt-get update && apt-get install -y pkg-config libmysqlclient-dev && pip install mysqlclient psycopg2-binary && service postgresql restart && service mysql restart && export POSTGRESQL_URL='postgresql://testuser:testpass@localhost/testdb' && export MYSQL_URL='mysql://testuser:testpass@localhost/testdb' && pytest -v --cov frictionless --cov-report term-missing --cov-fail-under 80 --ci
###ACTION_DELIMITER###
sed -i 's/local   all             all                                     peer/local   all             all                                     md5/' /etc/postgresql/16/main/pg_hba.conf && service postgresql restart && mysql -u root -e "DROP USER IF EXISTS 'testuser'@'localhost';" && mysql -u root -e "CREATE USER 'testuser'@'%' IDENTIFIED BY 'testpass';" && mysql -u root -e "GRANT ALL PRIVILEGES ON testdb.* TO 'testuser'@'%';" && mysql -u root -e 'FLUSH PRIVILEGES;' && service mysql restart && pip install --upgrade pytest && export POSTGRESQL_URL='postgresql://testuser:testpass@localhost/testdb' && export MYSQL_URL='mysql://testuser:testpass@localhost/testdb' && pytest -v --cov frictionless --cov-report term-missing --cov-fail-under 80 --ci
###ACTION_DELIMITER###
echo 'pytest -v --cov frictionless --cov-report term-missing --cov-fail-under 80 --ci' > /home/frictionless-py/test_commands.sh && chmod +x /home/frictionless-py/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v --cov frictionless --cov-report term-missing --cov-fail-under 80 --ci

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
pytest -v --cov frictionless --cov-report term-missing --cov-fail-under 80 --ci

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
pytest -v --cov frictionless --cov-report term-missing --cov-fail-under 80 --ci

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
RUN git clone https://github.com/frictionlessdata/frictionless-py.git /home/frictionless-py

WORKDIR /home/frictionless-py
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("frictionlessdata", "frictionless_py_583_to_466")
class FRICTIONLESS_PY_583_TO_466(Instance):
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
        # Parse log line by line
        for line in log.splitlines():
            line = line.strip()
            # Remove leading line number bracket
            if line.startswith('['):
                split_line = line.split(']', 1)
                if len(split_line) > 1:
                    line = split_line[1].strip()
                else:
                    line = ''
            # Extract passed tests
            if 'PASSED' in line:
                test_name = line.split(' PASSED')[0].strip()
                passed_tests.add(test_name)
            # Extract failed tests
            elif 'FAILED' in line:
                test_part = line.partition('FAILED ')[2]
                if test_part:
                    test_name = test_part.partition(' - ')[0].strip()
                    failed_tests.add(test_name)
            elif 'ERROR' in line:
                test_part = line.partition('ERROR ')[2]
                if test_part:
                    test_name = test_part.partition(' - ')[0].strip()
                    failed_tests.add(test_name)
            # Extract skipped tests
            elif 'SKIPPED' in line:
                if line.startswith('SKIPPED'):
                    test_name = line.split('SKIPPED ')[1].strip()
                else:
                    test_name = line.split(' SKIPPED')[0].strip()
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
