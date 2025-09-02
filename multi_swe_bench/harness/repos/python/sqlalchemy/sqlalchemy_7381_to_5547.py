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
                """pip install -e ".[testing]"
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential python3-dev
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
echo 'pytest -v ./test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
ls
###ACTION_DELIMITER###
pip install --force-reinstall pytest
###ACTION_DELIMITER###
pytest --version
###ACTION_DELIMITER###
echo 'def test_sample(): pass' > test_sample.py && pytest test_sample.py
###ACTION_DELIMITER###
cat setup.cfg
###ACTION_DELIMITER###
echo 'pytest -v' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
ls test
###ACTION_DELIMITER###
cat test/conftest.py
###ACTION_DELIMITER###
pytest --noconftest -v ./test
###ACTION_DELIMITER###
cat tox.ini
###ACTION_DELIMITER###
pip install pytest-xdist
###ACTION_DELIMITER###
pip install pytest==7.4.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'python -m pytest -v' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v test/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --collect-only test/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pytest -v test/sql/test_values.py
###ACTION_DELIMITER###
pip install -e ".[aiosqlite]" && pip install mock
###ACTION_DELIMITER###
echo 'pytest --rootdir=/home/sqlalchemy -v test/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
cat README.unittests.rst
###ACTION_DELIMITER###
echo 'pytest -n4' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest --dburi=sqlite:///:memory: -v test/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip install tox && echo 'tox -e py' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/passenv=.*/passenv=ORACLE_HOME,NLS_LANG,TOX_POSTGRESQL,TOX_POSTGRESQL_PY2K,TOX_MYSQL,TOX_MYSQL_PY2K,TOX_ORACLE,TOX_MSSQL,TOX_SQLITE,TOX_SQLITE_FILE,TOX_WORKERS,EXTRA_SQLITE_DRIVERS,EXTRA_PG_DRIVERS,EXTRA_MYSQL_DRIVERS/' tox.ini
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'python -m pytest -v --tb=native test/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
tox -e py
###ACTION_DELIMITER###
pip install pytest==6.2.5 && bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest-xdist==2.5.0 && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python -m pytest -v --tb=native test/

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
python -m pytest -v --tb=native test/

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
python -m pytest -v --tb=native test/

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
RUN git clone https://github.com/sqlalchemy/sqlalchemy.git /home/sqlalchemy

WORKDIR /home/sqlalchemy
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("sqlalchemy", "sqlalchemy_7381_to_5547")
class SQLALCHEMY_7381_TO_5547(Instance):
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
        import json
        # Regex patterns for extracting test names and statuses
        # Passed tests patterns
        passed_patterns = [
            re.compile(r"\[\d+\] (test/.*?) (?:<- .*?)? PASSED \[\s*\d+%\]", re.MULTILINE),
            re.compile(r"^(test/.*?) PASSED \[\s*\d+%\]", re.MULTILINE)
        ]
        # Skipped tests patterns
        skipped_patterns = [
            re.compile(r"\[\d+\] (test/.*?) SKIPPED \[\s*\d+%\]", re.MULTILINE),
            re.compile(r"^(test/.*?) SKIPPED \[\s*\d+%\]", re.MULTILINE),
            re.compile(r"SKIPPED \[\d+\] .*?: '([^']+)' :", re.MULTILINE)
        ]
        # Failed tests patterns
        failed_patterns = [
            re.compile(r"\[\d+\] FAILED (test/.*)$", re.MULTILINE),
            re.compile(r"^FAILED (test/.*)$", re.MULTILINE)
        ]
        # Extract passed tests
        for pattern in passed_patterns:
            for match in pattern.findall(log):
                passed_tests.add(match.strip())
        # Extract skipped tests
        for pattern in skipped_patterns:
            for match in pattern.findall(log):
                skipped_tests.add(match.strip())
        # Extract failed tests
        for pattern in failed_patterns:
            for match in pattern.findall(log):
                failed_tests.add(match.strip())
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
