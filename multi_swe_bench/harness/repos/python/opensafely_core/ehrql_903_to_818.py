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
        return "python:3.11-slim"
    
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
just devenv
###ACTION_DELIMITER###
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
###ACTION_DELIMITER###
source $HOME/.cargo/env && cargo install just
###ACTION_DELIMITER###
apt-get install -y build-essential
###ACTION_DELIMITER###
source $HOME/.cargo/env && cargo install just
###ACTION_DELIMITER###
just devenv
###ACTION_DELIMITER###
PYTHON_VERSION=python3.11 just devenv
###ACTION_DELIMITER###
source .venv/bin/activate && pip install pre-commit
###ACTION_DELIMITER###
PYTHON_VERSION=python3.11 just devenv
###ACTION_DELIMITER###
source .venv/bin/activate && just test-all --verbose
###ACTION_DELIMITER###
source .venv/bin/activate && pip install sqlalchemy
###ACTION_DELIMITER###
PYTHON_VERSION=python3.11 just test-all --verbose
###ACTION_DELIMITER###
source .venv/bin/activate && pip install structlog
###ACTION_DELIMITER###
PYTHON_VERSION=python3.11 just test-all --verbose
###ACTION_DELIMITER###
source .venv/bin/activate && pip install databricks-sql-connector
###ACTION_DELIMITER###
source .venv/bin/activate && just test-all --verbose
###ACTION_DELIMITER###
source .venv/bin/activate && pip install pyhive
###ACTION_DELIMITER###
source .venv/bin/activate && pip install 'pyhive[sqlalchemy]'
###ACTION_DELIMITER###
source .venv/bin/activate && pip install sqlalchemy==1.4.49
###ACTION_DELIMITER###
source .venv/bin/activate && python -c 'from pyhive.sqlalchemy_hive import HiveHTTPDialect'
###ACTION_DELIMITER###
source .venv/bin/activate && just test-all --verbose
###ACTION_DELIMITER###
source .venv/bin/activate && pip install pytest
###ACTION_DELIMITER###
source .venv/bin/activate && just test-all --verbose
###ACTION_DELIMITER###
source .venv/bin/activate && pip install pyarrow
###ACTION_DELIMITER###
source .venv/bin/activate && just test-all --verbose
###ACTION_DELIMITER###
source .venv/bin/activate && pip install docker
###ACTION_DELIMITER###
source .venv/bin/activate && just test-all --verbose
###ACTION_DELIMITER###
source .venv/bin/activate && pip install pytest-cov
###ACTION_DELIMITER###
source .venv/bin/activate && just test-all --verbose
###ACTION_DELIMITER###
source .venv/bin/activate && pip install hypothesis
###ACTION_DELIMITER###
source .venv/bin/activate && pip install toml
###ACTION_DELIMITER###
source .venv/bin/activate && pip install --force-reinstall hypothesis && just test-all --verbose
###ACTION_DELIMITER###
source .venv/bin/activate && just test-no-spark --verbose
###ACTION_DELIMITER###
echo 'source .venv/bin/activate && just test-no-spark --verbose -k "not mssql"' > /home/ehrql/test_commands.sh
###ACTION_DELIMITER###
bash /home/ehrql/test_commands.sh
###ACTION_DELIMITER###
echo 'source .venv/bin/activate && pytest -k "not spark and not mssql" --verbose' > /home/ehrql/test_commands.sh
###ACTION_DELIMITER###
bash /home/ehrql/test_commands.sh
###ACTION_DELIMITER###
echo 'source .venv/bin/activate && pytest -k "not (spark or mssql or docker)" --verbose' > /home/ehrql/test_commands.sh
###ACTION_DELIMITER###
bash /home/ehrql/test_commands.sh
###ACTION_DELIMITER###
echo 'source .venv/bin/activate && BACKEND=sqlite pytest --ignore=tests/docker -k "not (spark or mssql)" --verbose' > /home/ehrql/test_commands.sh
###ACTION_DELIMITER###
echo 'source .venv/bin/activate && BACKEND=sqlite pytest --ignore=tests/docker -k "not (spark or mssql)" --verbose' > /home/ehrql/test_commands.sh
###ACTION_DELIMITER###
bash /home/ehrql/test_commands.sh
###ACTION_DELIMITER###
echo 'source .venv/bin/activate && BACKEND=sqlite pytest --ignore=tests/docker --ignore=tests/integration/backends -k "not (spark or mssql or docker or tpp)" --verbose' > /home/ehrql/test_commands.sh
###ACTION_DELIMITER###
echo 'source .venv/bin/activate && pytest tests/unit --verbose' > /home/ehrql/test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
source .venv/bin/activate && pytest tests/unit --verbose

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
source .venv/bin/activate && pytest tests/unit --verbose

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
source .venv/bin/activate && pytest tests/unit --verbose

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
FROM python:3.11-slim

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
RUN git clone https://github.com/opensafely-core/ehrql.git /home/ehrql

WORKDIR /home/ehrql
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("opensafely-core", "ehrql_903_to_818")
class EHRQL_903_TO_818(Instance):
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
        # Parse the log content into lines
        lines = log.split('\n')
        # Regex patterns to match test cases and their statuses
        main_test_pattern = re.compile(r"^(tests/.*?::.*?) (PASSED|FAILED|SKIPPED) \[\s*\d+%\]$")
        summary_pattern = re.compile(r"^(FAILED|ERROR) (tests/.*?::.*?)$")
        for line in lines:
            line = line.strip()
            # Check for main test execution lines
            main_match = main_test_pattern.match(line)
            if main_match:
                test_name = main_match.group(1)
                status = main_match.group(2)
                if status == "PASSED":
                    passed_tests.add(test_name)
                elif status == "FAILED":
                    failed_tests.add(test_name)
                elif status == "SKIPPED":
                    skipped_tests.add(test_name)
            # Check for summary lines (failed/error tests)
            summary_match = summary_pattern.match(line)
            if summary_match:
                test_name = summary_match.group(2)
                failed_tests.add(test_name)
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
