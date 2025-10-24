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
        return "python:3.10-slim"

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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y postgresql postgresql-contrib libpq-dev build-essential redis-server
###ACTION_DELIMITER###
pg_ctlcluster 15 main start
###ACTION_DELIMITER###
sudo -u postgres psql -c "CREATE DATABASE openslides;" && sudo -u postgres psql -c "CREATE USER openslides WITH PASSWORD 'openslides';" && sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE openslides TO openslides;"
###ACTION_DELIMITER###
su - postgres -c "psql -c 'CREATE DATABASE openslides;'" && su - postgres -c "psql -c 'CREATE USER openslides WITH PASSWORD \'openslides\';'" && su - postgres -c "psql -c 'GRANT ALL PRIVILEGES ON DATABASE openslides TO openslides;'"
###ACTION_DELIMITER###
su - postgres -c "psql -c \"CREATE DATABASE openslides;\"" && su - postgres -c "psql -c \"CREATE USER openslides WITH PASSWORD 'openslides';\"" && su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE openslides TO openslides;\""
###ACTION_DELIMITER###
su - postgres -c "psql -c \"CREATE USER IF NOT EXISTS openslides WITH PASSWORD 'openslides';\"" && su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE openslides TO openslides;\""
###ACTION_DELIMITER###
psql -U postgres -c "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'openslides') THEN CREATE USER openslides WITH PASSWORD 'openslides'; END IF; $$;" && psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE openslides TO openslides;"
###ACTION_DELIMITER###
su - postgres -c "psql -c 'CREATE USER IF NOT EXISTS openslides WITH PASSWORD \'openslides\';'" && su - postgres -c "psql -c 'GRANT ALL PRIVILEGES ON DATABASE openslides TO openslides;'"
###ACTION_DELIMITER###
su postgres -c "psql -c \"CREATE USER IF NOT EXISTS openslides WITH PASSWORD 'openslides';\"" && su postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE openslides TO openslides;\""
###ACTION_DELIMITER###
su postgres -c "psql -c \"CREATE USER openslides WITH PASSWORD 'openslides';\"" || true && su postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE openslides TO openslides;\""
###ACTION_DELIMITER###
git clone https://github.com/OpenSlides/openslides-datastore-service.git /home/openslides-datastore-service
###ACTION_DELIMITER###
pip install -r /home/openslides-datastore-service/requirements.txt
###ACTION_DELIMITER###
ls /home/openslides-datastore-service
###ACTION_DELIMITER###
ls /home/openslides-datastore-service/requirements
###ACTION_DELIMITER###
pip install -r /home/openslides-datastore-service/requirements/requirements-general.txt
###ACTION_DELIMITER###
cd /home/openslides-datastore-service && export DATABASE_HOST=localhost DATABASE_USER=openslides DATABASE_PASSWORD=openslides DATABASE_NAME=openslides && nohup python -m datastore.reader & nohup python -m datastore.writer &
###ACTION_DELIMITER###
cat /home/openslides-datastore-service/nohup.out
###ACTION_DELIMITER###
ls /home/openslides-datastore-service/datastore/reader
###ACTION_DELIMITER###
cd /home/openslides-datastore-service && export DATABASE_HOST=localhost DATABASE_USER=openslides DATABASE_PASSWORD=openslides DATABASE_NAME=openslides && nohup gunicorn -w 4 -b 0.0.0.0:9010 datastore.reader.app:app &
###ACTION_DELIMITER###
ls /home/openslides-datastore-service/datastore/writer
###ACTION_DELIMITER###
cd /home/openslides-datastore-service && export DATABASE_HOST=localhost DATABASE_USER=openslides DATABASE_PASSWORD=openslides DATABASE_NAME=openslides && nohup gunicorn -w 4 -b 0.0.0.0:9011 datastore.writer.app:app &
###ACTION_DELIMITER###
ps aux | grep gunicorn
###ACTION_DELIMITER###
apt-get install -y procps
###ACTION_DELIMITER###
ps aux | grep gunicorn
###ACTION_DELIMITER###
cat /home/openslides-datastore-service/nohup.out
###ACTION_DELIMITER###
echo 'openslides' > /tmp/db_password && export DATABASE_PASSWORD_FILE=/tmp/db_password && cd /home/openslides-datastore-service && nohup gunicorn -w 4 -b 0.0.0.0:9010 datastore.reader.app:app & nohup gunicorn -w 4 -b 0.0.0.0:9011 datastore.writer.app:app &
###ACTION_DELIMITER###
ps aux | grep gunicorn
###ACTION_DELIMITER###
redis-server --daemonize yes && sleep 2 && redis-cli ping
###ACTION_DELIMITER###
cat /home/openslides-datastore-service/nohup.out
###ACTION_DELIMITER###
echo 'openslides' > /tmp/db_password && export DATABASE_HOST=localhost DATABASE_USER=openslides DATABASE_NAME=openslides DATABASE_PASSWORD_FILE=/tmp/db_password && cd /home/openslides-datastore-service && nohup gunicorn -w 4 -b 0.0.0.0:9010 datastore.reader.app:app & nohup gunicorn -w 4 -b 0.0.0.0:9011 datastore.writer.app:app &
###ACTION_DELIMITER###
cat /home/openslides-datastore-service/nohup.out
###ACTION_DELIMITER###
cat /home/openslides-datastore-service/datastore/reader/app.py
###ACTION_DELIMITER###
echo 'openslides' > /tmp/db_password && export DATABASE_HOST=localhost DATABASE_USER=openslides DATABASE_NAME=openslides DATABASE_PASSWORD_FILE=/tmp/db_password && cd /home/openslides-datastore-service && nohup gunicorn -w 4 -b 0.0.0.0:9010 datastore.reader.app:application & nohup gunicorn -w 4 -b 0.0.0.0:9011 datastore.writer.app:application &
###ACTION_DELIMITER###
ps aux | grep gunicorn
###ACTION_DELIMITER###
pip install --requirement requirements/requirements_development.txt
###ACTION_DELIMITER###
. requirements/export_datastore_commit.sh && pip install --requirement requirements/requirements_development.txt
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
export DATASTORE_READER_HOST=localhost DATASTORE_READER_PORT=9010 DATASTORE_WRITER_HOST=localhost DATASTORE_WRITER_PORT=9011 DATASTORE_DATABASE_HOST=localhost DATASTORE_DATABASE_USER=openslides DATASTORE_DATABASE_PASSWORD=openslides DATASTORE_DATABASE_NAME=openslides AUTH_HOST=localhost && bash test_commands.sh
###ACTION_DELIMITER###
export DATASTORE_READER_HOST=localhost DATASTORE_READER_PORT=9010 DATASTORE_WRITER_HOST=localhost DATASTORE_WRITER_PORT=9011 DATASTORE_DATABASE_HOST=localhost DATASTORE_DATABASE_USER=openslides DATASTORE_DATABASE_NAME=openslides DATABASE_PASSWORD_FILE=/tmp/db_password AUTH_HOST=localhost && bash test_commands.sh
###ACTION_DELIMITER###
export DATASTORE_READER_HOST=localhost DATASTORE_READER_PORT=9010 DATASTORE_WRITER_HOST=localhost DATASTORE_WRITER_PORT=9011 DATASTORE_DATABASE_HOST=localhost DATASTORE_DATABASE_USER=openslides DATASTORE_DATABASE_NAME=openslides DATABASE_PASSWORD_FILE=/tmp/db_password REDIS_URL=redis://localhost:6379 AUTH_HOST=localhost && bash test_commands.sh
###ACTION_DELIMITER###
export DATASTORE_READER_HOST=localhost DATASTORE_READER_PORT=9010 DATASTORE_WRITER_HOST=localhost DATASTORE_WRITER_PORT=9011 DATASTORE_DATABASE_HOST=localhost DATASTORE_DATABASE_USER=openslides DATASTORE_DATABASE_PASSWORD=openslides DATASTORE_DATABASE_NAME=openslides AUTH_HOST=localhost AUTH_PORT=9004 REDIS_URL=redis://localhost:6379 OPENSLIDES_DEVELOPMENT=1 && bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v --no-header -rA --tb=no -p no:cacheprovider

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider

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
FROM python:3.10-slim

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
RUN git clone https://github.com/OpenSlides/openslides-backend.git /home/openslides-backend

WORKDIR /home/openslides-backend
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("OpenSlides", "openslides_backend_1288_to_1223")
class OPENSLIDES_BACKEND_1288_TO_1223(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re

        # Pattern for PASSED tests (e.g., "tests/... PASSED [  0%]")
        passed_pattern = re.compile(r"^(tests/.*?) PASSED\s+\[\s*\d+%\]", re.MULTILINE)
        passed_matches = passed_pattern.findall(log)
        for test in passed_matches:
            passed_tests.add(test.strip())
        # Pattern for FAILED tests (case 1: "tests/... FAILED [  0%]")
        failed_pattern1 = re.compile(r"^(tests/.*?) FAILED\s+\[\s*\d+%\]", re.MULTILINE)
        failed_matches1 = failed_pattern1.findall(log)
        for test in failed_matches1:
            failed_tests.add(test.strip())
        # Pattern for FAILED tests (case 2: "FAILED tests/...")
        failed_pattern2 = re.compile(r"^FAILED (tests/.*)$", re.MULTILINE)
        failed_matches2 = failed_pattern2.findall(log)
        for test in failed_matches2:
            failed_tests.add(test.strip())
        # Pattern for SKIPPED tests (e.g., "tests/... SKIPPED [  0%]")
        skipped_pattern = re.compile(
            r"^(tests/.*?) SKIPPED\s+\[\s*\d+%\]", re.MULTILINE
        )
        skipped_matches = skipped_pattern.findall(log)
        for test in skipped_matches:
            skipped_tests.add(test.strip())
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
