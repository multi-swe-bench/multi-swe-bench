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
                """ls -la
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH"
###ACTION_DELIMITER###
poetry install --with dev
###ACTION_DELIMITER###
echo 'poetry run pytest -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y postgresql
###ACTION_DELIMITER###
service postgresql start
###ACTION_DELIMITER###
su postgres -c 'createdb fractal_test' && export DATABASE_URL='postgresql://postgres@localhost/fractal_test'
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
su postgres -c 'psql -c "CREATE USER fractal_user WITH PASSWORD \'fractal_password\';"' && su postgres -c 'psql -c "GRANT ALL PRIVILEGES ON DATABASE fractal_test TO fractal_user;"' && export DATABASE_URL='postgresql://fractal_user:fractal_password@localhost/fractal_test'
###ACTION_DELIMITER###
su postgres -c "psql -c 'CREATE USER fractal_user WITH PASSWORD \'fractal_password\';'" && su postgres -c "psql -c 'GRANT ALL PRIVILEGES ON DATABASE fractal_test TO fractal_user;'" && export DATABASE_URL='postgresql://fractal_user:fractal_password@localhost/fractal_test'
###ACTION_DELIMITER###
su postgres -c "psql -c \"CREATE USER fractal_user WITH PASSWORD 'fractal_password';\"" && su postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE fractal_test TO fractal_user;\"" && export DATABASE_URL='postgresql://fractal_user:fractal_password@localhost/fractal_test'
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
psql postgresql://fractal_user:fractal_password@localhost/fractal_test -c 'SELECT 1;'
###ACTION_DELIMITER###
poetry run alembic upgrade head
###ACTION_DELIMITER###
ls fractal_server
###ACTION_DELIMITER###
poetry run alembic --config fractal_server/alembic.ini upgrade head
###ACTION_DELIMITER###
export POSTGRES_DB=fractal_test POSTGRES_USER=fractal_user POSTGRES_PASSWORD=fractal_password && poetry run alembic --config fractal_server/alembic.ini upgrade head
###ACTION_DELIMITER###
su postgres -c "psql -d fractal_test -c 'GRANT CREATE ON SCHEMA public TO fractal_user;'"
###ACTION_DELIMITER###
export POSTGRES_DB=fractal_test POSTGRES_USER=fractal_user POSTGRES_PASSWORD=fractal_password && poetry run alembic --config fractal_server/alembic.ini upgrade head
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
export POSTGRES_DB=fractal_test POSTGRES_USER=fractal_user POSTGRES_PASSWORD=fractal_password DATABASE_URL='postgresql://fractal_user:fractal_password@localhost/fractal_test' && bash test_commands.sh
###ACTION_DELIMITER###
su postgres -c "sed -i 's/local   all             all                                     peer/local   all             all                                     md5/' /etc/postgresql/15/main/pg_hba.conf" && service postgresql restart && export POSTGRES_DB=fractal_test POSTGRES_USER=fractal_user POSTGRES_PASSWORD=fractal_password DATABASE_URL='postgresql://fractal_user:fractal_password@localhost/fractal_test' && bash test_commands.sh
###ACTION_DELIMITER###
echo 'DATABASE_URL=postgresql+asyncpg://fractal_user:fractal_password@localhost/fractal_test
POSTGRES_DB=fractal_test
POSTGRES_USER=fractal_user
POSTGRES_PASSWORD=fractal_password' > .env && bash test_commands.sh
###ACTION_DELIMITER###
echo 'DATABASE_URL=postgresql+asyncpg://fractal_user:fractal_password@localhost/fractal_test
POSTGRES_DB=fractal_test
POSTGRES_USER=fractal_user
POSTGRES_PASSWORD=fractal_password' > .env && bash test_commands.sh
###ACTION_DELIMITER###
sed -i "s/^#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/15/main/postgresql.conf && echo 'host all all 127.0.0.1/32 md5' >> /etc/postgresql/15/main/pg_hba.conf && service postgresql restart && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export POSTGRES_DB=fractal_test\nexport POSTGRES_USER=fractal_user\nexport POSTGRES_PASSWORD=fractal_password\nexport DATABASE_URL=postgresql+asyncpg://fractal_user:fractal_password@localhost/fractal_test\npoetry run pytest -v' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
poetry add --dev asyncpg && echo -e 'export POSTGRES_DB=fractal_test\nexport POSTGRES_USER=fractal_user\nexport POSTGRES_PASSWORD=fractal_password\nexport DATABASE_URL=postgresql+asyncpg://fractal_user:fractal_password@localhost/fractal_test\npoetry run pytest -v' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'DATABASE_URL=postgresql+asyncpg://fractal_user:fractal_password@/fractal_test?host=/var/run/postgresql
POSTGRES_DB=fractal_test
POSTGRES_USER=fractal_user
POSTGRES_PASSWORD=fractal_password' > .env && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source .env
poetry run pytest -v --log-level=DEBUG' > test_commands.sh && echo 'DATABASE_URL=postgresql+asyncpg://fractal_user:fractal_password@localhost/fractal_test
POSTGRES_DB=fractal_test
POSTGRES_USER=fractal_user
POSTGRES_PASSWORD=fractal_password' > .env && bash test_commands.sh
###ACTION_DELIMITER###
echo 'DATABASE_URL=postgresql://fractal_user:fractal_password@localhost/fractal_test
POSTGRES_DB=fractal_test
POSTGRES_USER=fractal_user
POSTGRES_PASSWORD=fractal_password' > .env && echo -e 'source .env
poetry run pytest -v' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'DATABASE_URL=postgresql://fractal_user:fractal_password@127.0.0.1/fractal_test
POSTGRES_DB=fractal_test
POSTGRES_USER=fractal_user
POSTGRES_PASSWORD=fractal_password' > .env && echo -e 'source .env
poetry run pytest -v' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
tail -n 50 /var/log/postgresql/postgresql-15-main.log
###ACTION_DELIMITER###
su postgres -c "sed -i 's/host    all             all             127.0.0.1\/32            scram-sha-256/host    all             all             127.0.0.1\/32            trust/' /etc/postgresql/15/main/pg_hba.conf" && su postgres -c "sed -i 's/host    all             all             ::1\/128                 scram-sha-256/host    all             all             ::1\/128                 trust/' /etc/postgresql/15/main/pg_hba.conf" && service postgresql restart && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source .env
poetry run pytest -v -m "not docker"' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source .env
poetry run pytest -v --ignore=tests/v2/test_08_backends/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source .env
poetry run pytest -v --ignore=tests/v2/test_06_tasks_lifecycle/ --ignore=tests/v2/test_07_full_workflow/ --ignore=tests/v2/test_08_backends/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source .env
poetry run pytest -v --ignore=tests/no_version/ --ignore=tests/v2/test_00_ssh/ --ignore=tests/v2/test_06_tasks_lifecycle/ --ignore=tests/v2/test_07_full_workflow/ --ignore=tests/v2/test_08_backends/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source .env
poetry run pytest -v -k "not test_read_log_file" --ignore=tests/no_version/ --ignore=tests/v2/test_00_ssh/ --ignore=tests/v2/test_06_tasks_lifecycle/ --ignore=tests/v2/test_07_full_workflow/ --ignore=tests/v2/test_08_backends/' > test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
source .env
poetry run pytest -v -k "not test_read_log_file" --ignore=tests/no_version/ --ignore=tests/v2/test_00_ssh/ --ignore=tests/v2/test_06_tasks_lifecycle/ --ignore=tests/v2/test_07_full_workflow/ --ignore=tests/v2/test_08_backends/

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
source .env
poetry run pytest -v -k "not test_read_log_file" --ignore=tests/no_version/ --ignore=tests/v2/test_00_ssh/ --ignore=tests/v2/test_06_tasks_lifecycle/ --ignore=tests/v2/test_07_full_workflow/ --ignore=tests/v2/test_08_backends/

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
source .env
poetry run pytest -v -k "not test_read_log_file" --ignore=tests/no_version/ --ignore=tests/v2/test_00_ssh/ --ignore=tests/v2/test_06_tasks_lifecycle/ --ignore=tests/v2/test_07_full_workflow/ --ignore=tests/v2/test_08_backends/

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
RUN git clone https://github.com/fractal-analytics-platform/fractal-server.git /home/fractal-server

WORKDIR /home/fractal-server
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("fractal-analytics-platform", "fractal_server_2692_to_2549")
class FRACTAL_SERVER_2692_TO_2549(Instance):
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
        passed_tests = set[str]() # Tests that passed successfully
        failed_tests = set[str]() # Tests that failed
        skipped_tests = set[str]() # Tests that were skipped
        import re
        # Extract test names and statuses using regex
        passed_tests = set(re.findall(r'(tests/[^:]+::[^ ]+) PASSED', log))
        failed_tests = set(re.findall(r'FAILED (tests/[^:]+::[^ \n-]+)', log))
        skipped_tests = set(re.findall(r'SKIPPED (tests/[^:]+::[^ ]+)', log))
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
