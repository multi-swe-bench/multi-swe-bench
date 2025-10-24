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
        repo_name = self.pr.repo
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
ls -la fidesctl
###ACTION_DELIMITER###
pip install -r fidesctl/requirements.txt
###ACTION_DELIMITER###
pip install -r fidesctl/dev-requirements.txt
###ACTION_DELIMITER###
echo 'pytest -v' > test_commands.sh
###ACTION_DELIMITER###
echo 'pytest --no-header -rA --tb=no -p no:cacheprovider -v' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -e fidesctl/
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
fidesctl init-db
###ACTION_DELIMITER###
export FIDESCTL_CONFIG_PATH=fidesctl/fidesctl.toml && fidesctl init-db
###ACTION_DELIMITER###
make init-db
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make init-db
###ACTION_DELIMITER###
apt-get update && apt-get install -y docker-compose
###ACTION_DELIMITER###
make init-db
###ACTION_DELIMITER###
export DATABASE_URL=sqlite:///fides.db && fidesctl init-db
###ACTION_DELIMITER###
sed -i 's/postgresql+psycopg2:\/\/fidesctl:fidesctl@fidesctl-db:5432\/fidesctl/sqlite:\/\/\/fides.db/' fidesctl/fidesctl.toml
###ACTION_DELIMITER###
cat fidesctl/fidesctl.toml
###ACTION_DELIMITER###
export FIDESCTL_CONFIG_PATH=fidesctl/fidesctl.toml && fidesctl init-db
###ACTION_DELIMITER###
apt-get update && apt-get install -y postgresql postgresql-contrib
###ACTION_DELIMITER###
service postgresql start
###ACTION_DELIMITER###
su - postgres -c "psql -c 'CREATE USER fidesctl WITH PASSWORD 'fidesctl'; CREATE DATABASE fidesctl OWNER fidesctl;'"
###ACTION_DELIMITER###
su - postgres -c "psql -c \"CREATE USER fidesctl WITH PASSWORD 'fidesctl'; CREATE DATABASE fidesctl OWNER fidesctl;\""
###ACTION_DELIMITER###

###ACTION_DELIMITER###
su - postgres -c "psql -c \"CREATE USER fidesctl WITH PASSWORD 'fidesctl';\""
###ACTION_DELIMITER###
su - postgres -c "psql -c \"CREATE DATABASE fidesctl OWNER fidesctl;\""
###ACTION_DELIMITER###
sed -i 's/sqlite:\/\/\/fides.db/postgresql+psycopg2:\/\/fidesctl:fidesctl@localhost:5432\/fidesctl/' fidesctl/fidesctl.toml && export FIDESCTL_CONFIG_PATH=fidesctl/fidesctl.toml && fidesctl init-db
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'fidesctl webserver &\nSERVER_PID=$!\nsleep 5\npytest --no-header -rA --tb=no -p no:cacheprovider -v\nkill $SERVER_PID' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/server_url = "http:\/\/fidesctl:8080"/server_url = "http:\/\/localhost:8080"/' fidesctl/fidesctl.toml
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
fidesctl webserver &
SERVER_PID=$!
sleep 5
pytest --no-header -rA --tb=no -p no:cacheprovider -v
kill $SERVER_PID

""".replace("[[REPO_NAME]]", repo_name),
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
fidesctl webserver &
SERVER_PID=$!
sleep 5
pytest --no-header -rA --tb=no -p no:cacheprovider -v
kill $SERVER_PID

""".replace("[[REPO_NAME]]", repo_name),
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
fidesctl webserver &
SERVER_PID=$!
sleep 5
pytest --no-header -rA --tb=no -p no:cacheprovider -v
kill $SERVER_PID

""".replace("[[REPO_NAME]]", repo_name),
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
RUN git clone https://github.com/ethyca/fides.git /home/fides

WORKDIR /home/fides
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ethyca", "fides_119_to_60")
class FIDES_119_TO_60(Instance):
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

        return "bash /home/run.sh"

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

        lines = log.split("\n")
        for i, line in enumerate(lines):
            # Pattern 1: Test name followed by status and percentage (e.g., "test_name PASSED [  0%]")
            match1 = re.match(r"^(.*?::test_.+?)\s+(PASSED|FAILED)\s+\[\s*\d+%\]", line)
            if match1:
                test_name = match1.group(1).strip()
                status = match1.group(2)
                if status == "PASSED":
                    passed_tests.add(test_name)
                elif status == "FAILED":
                    failed_tests.add(test_name)
                continue
            # Pattern 2: Status followed by test name (e.g., "FAILED test_name")
            match2 = re.match(r"^(FAILED|PASSED)\s+(.+?::test_.+?)(?:\s|-|$)", line)
            if match2:
                status = match2.group(1)
                test_name = match2.group(2).strip()
                if status == "PASSED":
                    passed_tests.add(test_name)
                elif status == "FAILED":
                    failed_tests.add(test_name)
                continue
            # Pattern 3: Test name in current line, status in next line (e.g., "test_name INFO: ..." followed by "PASSED [  0%]")
            if "::test_" in line and not re.search(r"PASSED|FAILED", line):
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    match3_status = re.match(
                        r"^(PASSED|FAILED)\s+\[\s*\d+%\]", next_line
                    )
                    if match3_status:
                        test_name = (
                            re.match(r"^(.*?::test_.+?)\s+", line).group(1).strip()
                        )
                        status = match3_status.group(1)
                        if status == "PASSED":
                            passed_tests.add(test_name)
                        elif status == "FAILED":
                            failed_tests.add(test_name)
                        continue
        parsed_results = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
        }

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
