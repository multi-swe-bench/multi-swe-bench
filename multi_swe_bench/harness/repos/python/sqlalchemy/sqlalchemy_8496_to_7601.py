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
                """ls
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip build-essential python3-dev
###ACTION_DELIMITER###
pip install 'pytest>=7.0.0rc1,<8' pytest-xdist
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install cython
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install 'pytest>=7.0.0rc1,<8' pytest-xdist
###ACTION_DELIMITER###
echo 'venv/bin/pytest -v --tb native -r sfxX --maxfail=250 -p warnings -p logging --strict-markers test/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'venv/bin/pytest -v --tb native -r sfxX --maxfail=250 -p warnings -p logging --strict-markers -W ignore::DeprecationWarning:sqlalchemy.sql.sqltypes test/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -e ".[mypy]"
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'venv/bin/pytest -v --tb native -r sfxX --maxfail=250 -p warnings -p logging --strict-markers -n auto -m "not memory_intensive and not timing_intensive and not mypy" test/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'venv/bin/pytest -v --tb native -r sfxX --maxfail=250 -p warnings -p logging --strict-markers -n auto -m "not memory_intensive and not timing_intensive and not mypy" -W ignore::DeprecationWarning:sqlalchemy.sql.sqltypes test/' > test_commands.sh
###ACTION_DELIMITER###
echo 'export PYTHONWARNINGS="ignore::DeprecationWarning:sqlalchemy.sql.sqltypes"; venv/bin/pytest -v --tb native -r sfxX --maxfail=250 -p warnings -p logging --strict-markers -n auto -m "not memory_intensive and not timing_intensive and not mypy" test/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'export PYTHONWARNINGS="ignore::DeprecationWarning:sqlalchemy.sql.sqltypes"; venv/bin/pytest -v --tb native -r sfxX --maxfail=250 -p warnings -p logging --strict-markers -n auto -m "not memory_intensive and not timing_intensive and not mypy" -o "filterwarnings=default::DeprecationWarning:sqlalchemy" test/' > test_commands.sh
###ACTION_DELIMITER###
echo 'export PYTHONWARNINGS="ignore::DeprecationWarning:sqlalchemy.sql.sqltypes"; venv/bin/pytest -v --tb native -r sfxX --maxfail=250 -p warnings -p logging --strict-markers -n auto -m "not memory_intensive and not timing_intensive and not mypy" -o "filterwarnings=ignore::DeprecationWarning:sqlalchemy" test/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
export PYTHONWARNINGS="ignore::DeprecationWarning:sqlalchemy.sql.sqltypes"; venv/bin/pytest -v --tb native -r sfxX --maxfail=250 -p warnings -p logging --strict-markers -n auto -m "not memory_intensive and not timing_intensive and not mypy" -o "filterwarnings=ignore::DeprecationWarning:sqlalchemy" test/

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
export PYTHONWARNINGS="ignore::DeprecationWarning:sqlalchemy.sql.sqltypes"; venv/bin/pytest -v --tb native -r sfxX --maxfail=250 -p warnings -p logging --strict-markers -n auto -m "not memory_intensive and not timing_intensive and not mypy" -o "filterwarnings=ignore::DeprecationWarning:sqlalchemy" test/

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
export PYTHONWARNINGS="ignore::DeprecationWarning:sqlalchemy.sql.sqltypes"; venv/bin/pytest -v --tb native -r sfxX --maxfail=250 -p warnings -p logging --strict-markers -n auto -m "not memory_intensive and not timing_intensive and not mypy" -o "filterwarnings=ignore::DeprecationWarning:sqlalchemy" test/

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


@Instance.register("sqlalchemy", "sqlalchemy_8496_to_7601")
class SQLALCHEMY_8496_TO_7601(Instance):
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
        # Parse the log content using regex
        pattern = re.compile(r'''(PASSED|FAILED|SKIPPED).*?(test/.*?)(?=\s|\()''')
        matches = pattern.findall(log)
        for status, test_name in matches:
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
