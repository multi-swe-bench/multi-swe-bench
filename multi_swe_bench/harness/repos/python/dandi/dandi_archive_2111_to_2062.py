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
apt-get update && apt-get install -y python3.11 python3.11-dev python3.11-pip build-essential
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.11 python3.11-dev build-essential && python3.11 -m ensurepip --upgrade
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget && wget https://bootstrap.pypa.io/get-pip.py && python3.11 get-pip.py
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.11-venv && python3.11 -m venv venv && . venv/bin/activate && pip install -e .[test]
###ACTION_DELIMITER###
apt-get update && apt-get install -y libpq-dev && . venv/bin/activate && pip install -e .[test]
###ACTION_DELIMITER###
echo 'venv/bin/pytest --verbose --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export DJANGO_DANDI_API_URL="http://localhost:8000"
venv/bin/pytest --verbose --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export DJANGO_DANDI_API_URL="http://localhost:8000"
export DJANGO_DANDI_DEV_EMAIL="test@example.com"
venv/bin/pytest --verbose --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export DJANGO_DANDI_API_URL="http://localhost:8000"
export DJANGO_DANDI_DEV_EMAIL="test@example.com"
export DJANGO_DANDI_WEB_APP_URL="http://localhost:3000"
venv/bin/pytest --verbose --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export DJANGO_DANDI_API_URL="http://localhost:8000"
export DJANGO_DANDI_DEV_EMAIL="test@example.com"
export DJANGO_DANDI_WEB_APP_URL="http://localhost:3000"
export DJANGO_DATABASE_URL="sqlite:///test.db"
venv/bin/pytest --verbose --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export DJANGO_DANDI_API_URL="http://localhost:8000"
export DJANGO_DANDI_DEV_EMAIL="test@example.com"
export DJANGO_DANDI_WEB_APP_URL="http://localhost:3000"
export DJANGO_DATABASE_URL="sqlite:///test.db"
export DJANGO_MINIO_STORAGE_ACCESS_KEY="minioadmin"
export DJANGO_MINIO_STORAGE_SECRET_KEY="minioadmin"
venv/bin/pytest --verbose --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export DJANGO_DANDI_API_URL="http://localhost:8000"
export DJANGO_DANDI_DEV_EMAIL="test@example.com"
export DJANGO_DANDI_WEB_APP_URL="http://localhost:3000"
export DJANGO_DATABASE_URL="sqlite:///test.db"
export DJANGO_MINIO_STORAGE_ACCESS_KEY="minioadmin"
export DJANGO_MINIO_STORAGE_SECRET_KEY="minioadmin"
export DJANGO_MINIO_STORAGE_ENDPOINT="localhost:9000"
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
./minio server /tmp/minio --console-address :9001 &
sleep 10
venv/bin/pytest --verbose --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export DJANGO_DANDI_API_URL="http://localhost:8000"
export DJANGO_DANDI_DEV_EMAIL="test@example.com"
export DJANGO_DANDI_WEB_APP_URL="http://localhost:3000"
export DJANGO_MINIO_STORAGE_ACCESS_KEY="minioadmin"
export DJANGO_MINIO_STORAGE_SECRET_KEY="minioadmin"
export DJANGO_MINIO_STORAGE_ENDPOINT="localhost:9000"
apt-get update && apt-get install -y postgresql postgresql-contrib && service postgresql start && su - postgres -c "createdb testdb" && su - postgres -c "createuser -s testuser"
export DJANGO_DATABASE_URL="postgres://testuser@localhost/testdb"
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
./minio server /tmp/minio --console-address :9001 &
sleep 10
venv/bin/pytest --verbose --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export DJANGO_DANDI_API_URL="http://localhost:8000"
export DJANGO_DANDI_DEV_EMAIL="test@example.com"
export DJANGO_DANDI_WEB_APP_URL="http://localhost:3000"
export DJANGO_MINIO_STORAGE_ACCESS_KEY="minioadmin"
export DJANGO_MINIO_STORAGE_SECRET_KEY="minioadmin"
export DJANGO_MINIO_STORAGE_ENDPOINT="localhost:9000"
apt-get update && apt-get install -y postgresql postgresql-contrib && service postgresql start
# Configure PostgreSQL to trust local connections
sed -i "s/local   all             all                                     peer/local   all             all                                     trust/" /etc/postgresql/15/main/pg_hba.conf
sed -i "s/host    all             all             127.0.0.1\/32            scram-sha-256/host    all             all             127.0.0.1\/32            trust/" /etc/postgresql/15/main/pg_hba.conf
service postgresql restart
su - postgres -c "createdb testdb"
su - postgres -c "createuser -s testuser"
export DJANGO_DATABASE_URL="postgres://testuser@localhost/testdb"
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
./minio server /tmp/minio --console-address :9001 &
sleep 10
venv/bin/pytest --verbose --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export DJANGO_DANDI_API_URL="http://localhost:8000"
export DJANGO_DANDI_DEV_EMAIL="test@example.com"
export DJANGO_DANDI_WEB_APP_URL="http://localhost:3000"
export DJANGO_MINIO_STORAGE_ACCESS_KEY="minioadmin"
export DJANGO_MINIO_STORAGE_SECRET_KEY="minioadmin"
export DJANGO_MINIO_STORAGE_ENDPOINT="localhost:9000"
export DJANGO_DATABASE_URL="postgres://testuser@localhost/testdb"
./minio server /tmp/minio --console-address :9001 &
sleep 10
venv/bin/pytest --verbose --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
export DJANGO_DANDI_API_URL="http://localhost:8000"
export DJANGO_DANDI_DEV_EMAIL="test@example.com"
export DJANGO_DANDI_WEB_APP_URL="http://localhost:3000"
export DJANGO_MINIO_STORAGE_ACCESS_KEY="minioadmin"
export DJANGO_MINIO_STORAGE_SECRET_KEY="minioadmin"
export DJANGO_MINIO_STORAGE_ENDPOINT="localhost:9000"
export DJANGO_DATABASE_URL="postgres://testuser@localhost/testdb"
./minio server /tmp/minio --console-address :9001 &
sleep 10
venv/bin/pytest --verbose --no-header -rA --tb=no -p no:cacheprovider

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
export DJANGO_DANDI_API_URL="http://localhost:8000"
export DJANGO_DANDI_DEV_EMAIL="test@example.com"
export DJANGO_DANDI_WEB_APP_URL="http://localhost:3000"
export DJANGO_MINIO_STORAGE_ACCESS_KEY="minioadmin"
export DJANGO_MINIO_STORAGE_SECRET_KEY="minioadmin"
export DJANGO_MINIO_STORAGE_ENDPOINT="localhost:9000"
export DJANGO_DATABASE_URL="postgres://testuser@localhost/testdb"
./minio server /tmp/minio --console-address :9001 &
sleep 10
venv/bin/pytest --verbose --no-header -rA --tb=no -p no:cacheprovider

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
export DJANGO_DANDI_API_URL="http://localhost:8000"
export DJANGO_DANDI_DEV_EMAIL="test@example.com"
export DJANGO_DANDI_WEB_APP_URL="http://localhost:3000"
export DJANGO_MINIO_STORAGE_ACCESS_KEY="minioadmin"
export DJANGO_MINIO_STORAGE_SECRET_KEY="minioadmin"
export DJANGO_MINIO_STORAGE_ENDPOINT="localhost:9000"
export DJANGO_DATABASE_URL="postgres://testuser@localhost/testdb"
./minio server /tmp/minio --console-address :9001 &
sleep 10
venv/bin/pytest --verbose --no-header -rA --tb=no -p no:cacheprovider

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
RUN git clone https://github.com/dandi/dandi-archive.git /home/dandi-archive

WORKDIR /home/dandi-archive
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("dandi", "dandi_archive_2111_to_2062")
class DANDI_ARCHIVE_2111_TO_2062(Instance):
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
        import re
        # Regex pattern to match test names and their statuses
        pattern = re.compile(r'(?:(PASSED|FAILED|SKIPPED)\s+([\w/]+\.py::[\w\[\]\-]+)|([\w/]+\.py::[\w\[\]\-]+)\s+(PASSED|FAILED|SKIPPED))')
        matches = pattern.findall(log)
        for match in matches:
            status1, test1, test2, status2 = match
            if status1:
                status = status1
                test_name = test1
            else:
                status = status2
                test_name = test2
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
