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
                """python --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.10 python3.10-dev python3.10-distutils
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git
###ACTION_DELIMITER###
curl https://pyenv.run | bash
###ACTION_DELIMITER###
export PYENV_ROOT="$HOME/.pyenv" && export PATH="$PYENV_ROOT/bin:$PATH" && eval "$(pyenv init - bash)"
###ACTION_DELIMITER###
pyenv install 3.10.13
###ACTION_DELIMITER###
pyenv local 3.10.13
###ACTION_DELIMITER###
pip install poetry
###ACTION_DELIMITER###
poetry install --with test -E duckdb -E polars -E postgres
###ACTION_DELIMITER###
apt-get update && apt-get install -y libpq-dev
###ACTION_DELIMITER###
poetry install --with test -E duckdb -E polars -E postgres
###ACTION_DELIMITER###
echo 'poetry run pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
poetry install --with test -E duckdb -E polars -E postgres -E bigquery -E clickhouse -E dask -E datafusion -E druid -E exasol -E impala -E mssql -E mysql -E oracle -E pyspark -E snowflake -E trino -E examples -E visualization
###ACTION_DELIMITER###
apt-get update && apt-get install -y unixodbc-dev openjdk-11-jre
###ACTION_DELIMITER###
apt-get update && apt-get install -y unixodbc-dev openjdk-17-jre
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
poetry run pip install apache-flink
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
poetry run pip install apache-flink==1.17.6
###ACTION_DELIMITER###
poetry run pip install apache-flink==1.17.2
###ACTION_DELIMITER###
echo 'poetry run pytest -v --no-header -rA --tb=no -p no:cacheprovider -W ignore::DeprecationWarning' > test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
echo 'poetry run pytest -v --no-header -rA --tb=no -p no:cacheprovider -W ignore::DeprecationWarning -n auto' > test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
echo 'poetry run pytest -v --no-header -rA --tb=no -p no:cacheprovider -W ignore::DeprecationWarning -n auto -k "not (mysql or postgres or bigquery or clickhouse or druid or exasol or impala or mssql or oracle or pyspark or snowflake or trino)"' > test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
poetry add --dev black
###ACTION_DELIMITER###
poetry add --dev black==24.10.0
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
mkdir -p /home/ibis/ci/ib
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
mkdir -p /home/ibis/ci/ibis"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
poetry run pytest -v --no-header -rA --tb=no -p no:cacheprovider -W ignore::DeprecationWarning -n auto -k "not (mysql or postgres or bigquery or clickhouse or druid or exasol or impala or mssql or oracle or pyspark or snowflake or trino)"

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
poetry run pytest -v --no-header -rA --tb=no -p no:cacheprovider -W ignore::DeprecationWarning -n auto -k "not (mysql or postgres or bigquery or clickhouse or druid or exasol or impala or mssql or oracle or pyspark or snowflake or trino)"

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
poetry run pytest -v --no-header -rA --tb=no -p no:cacheprovider -W ignore::DeprecationWarning -n auto -k "not (mysql or postgres or bigquery or clickhouse or druid or exasol or impala or mssql or oracle or pyspark or snowflake or trino)"

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
RUN git clone https://github.com/ibis-project/ibis.git /home/ibis

WORKDIR /home/ibis
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ibis-project", "ibis_9272_to_9015")
class IBIS_9272_TO_9015(Instance):
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
        # Regex pattern to match test status and name (captures test name until first whitespace)
        # Refined regex to match structured test names (ibis/.../test.py::test_name)
        # Expanded regex to capture parameterized test names with symbols like <, >, ,, :
        pattern = re.compile(r'(PASSED|FAILED|ERROR|SKIPPED)\s+(ibis/[\w/.]+\.py::[\w\[\]<>.,:_-]+)')
        matches = pattern.findall(log)
        for status, test_name in matches:
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ('FAILED', 'ERROR'):
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
