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
        return "python:3.9.6"

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
                """ls
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
pip check
###ACTION_DELIMITER###
pip list | grep pytest
###ACTION_DELIMITER###
pip install -r test_requirements.txt
###ACTION_DELIMITER###
echo 'pytest -v -p no:cov' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install cssutils
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install dj-database-url
###ACTION_DELIMITER###
pip install dj-database-url==0.5.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install celery==5.2.2
###ACTION_DELIMITER###
pip install -r requirements.txt -r test_requirements.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'export SECRET_KEY="django-insecure-test-key"; pytest -v -p no:cov' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
apt-get update && apt-get install -y nodejs npm
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
yarn build
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'export SECRET_KEY="django-insecure-test-key"; export MITX_ONLINE_BASE_URL="http://localhost"; export MAILGUN_SENDER_DOMAIN="example.com"; export MAILGUN_KEY="dummy_key"; export MITX_ONLINE_ADMIN_EMAIL="admin@example.com"; pytest -v -p no:cov' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'export SECRET_KEY="django-insecure-test-key"; export MITX_ONLINE_BASE_URL="http://localhost"; export MAILGUN_SENDER_DOMAIN="example.com"; export MAILGUN_KEY="dummy_key"; export MITX_ONLINE_ADMIN_EMAIL="admin@example.com"; pytest -v -p no:cov -o addopts=""' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y postgresql postgresql-contrib
###ACTION_DELIMITER###
pg_ctlcluster 13 main start
###ACTION_DELIMITER###
su - postgres -c 'createdb mitxonline && createuser -s mitxonline'
###ACTION_DELIMITER###
python manage.py migrate
###ACTION_DELIMITER###
export SECRET_KEY="django-insecure-test-key"; export MITX_ONLINE_BASE_URL="http://localhost"; export MAILGUN_SENDER_DOMAIN="example.com"; export MAILGUN_KEY="dummy_key"; export MITX_ONLINE_ADMIN_EMAIL="admin@example.com"; python manage.py migrate
###ACTION_DELIMITER###
export SECRET_KEY="django-insecure-test-key"; export MITX_ONLINE_BASE_URL="http://localhost"; export MAILGUN_SENDER_DOMAIN="example.com"; export MAILGUN_KEY="dummy_key"; export MITX_ONLINE_ADMIN_EMAIL="admin@example.com"; export OPENEDX_API_CLIENT_ID="dummy_id"; export OPENEDX_API_CLIENT_SECRET="dummy_secret"; export OPENEDX_API_KEY="dummy_key"; python manage.py migrate
###ACTION_DELIMITER###
export SECRET_KEY="django-insecure-test-key"; export MITX_ONLINE_BASE_URL="http://localhost"; export MAILGUN_SENDER_DOMAIN="example.com"; export MAILGUN_KEY="dummy_key"; export MITX_ONLINE_ADMIN_EMAIL="admin@example.com"; export OPENEDX_API_CLIENT_ID="dummy_id"; export OPENEDX_API_CLIENT_SECRET="dummy_secret"; export OPENEDX_API_KEY="dummy_key"; export DATABASE_URL="postgres://mitxonline@localhost/mitxonline"; python manage.py migrate
###ACTION_DELIMITER###
su - postgres -c "psql -c \"ALTER USER mitxonline PASSWORD 'dummy_password';\"" && export SECRET_KEY="django-insecure-test-key"; export MITX_ONLINE_BASE_URL="http://localhost"; export MAILGUN_SENDER_DOMAIN="example.com"; export MAILGUN_KEY="dummy_key"; export MITX_ONLINE_ADMIN_EMAIL="admin@example.com"; export OPENEDX_API_CLIENT_ID="dummy_id"; export OPENEDX_API_CLIENT_SECRET="dummy_secret"; export OPENEDX_API_KEY="dummy_key"; export DATABASE_URL="postgres://mitxonline:dummy_password@localhost/mitxonline"; python manage.py migrate
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'export SECRET_KEY="django-insecure-test-key"; export MITX_ONLINE_BASE_URL="http://localhost"; export MAILGUN_SENDER_DOMAIN="example.com"; export MAILGUN_KEY="dummy_key"; export MITX_ONLINE_ADMIN_EMAIL="admin@example.com"; export OPENEDX_API_CLIENT_ID="dummy_id"; export OPENEDX_API_CLIENT_SECRET="dummy_secret"; export OPENEDX_API_KEY="dummy_key"; export DATABASE_URL="postgres://mitxonline:dummy_password@localhost/mitxonline"; pytest -v -p no:cov -o addopts=""' > test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
export SECRET_KEY="django-insecure-test-key"; export MITX_ONLINE_BASE_URL="http://localhost"; export MAILGUN_SENDER_DOMAIN="example.com"; export MAILGUN_KEY="dummy_key"; export MITX_ONLINE_ADMIN_EMAIL="admin@example.com"; export OPENEDX_API_CLIENT_ID="dummy_id"; export OPENEDX_API_CLIENT_SECRET="dummy_secret"; export OPENEDX_API_KEY="dummy_key"; export DATABASE_URL="postgres://mitxonline:dummy_password@localhost/mitxonline"; pytest -v -p no:cov -o addopts=""

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
export SECRET_KEY="django-insecure-test-key"; export MITX_ONLINE_BASE_URL="http://localhost"; export MAILGUN_SENDER_DOMAIN="example.com"; export MAILGUN_KEY="dummy_key"; export MITX_ONLINE_ADMIN_EMAIL="admin@example.com"; export OPENEDX_API_CLIENT_ID="dummy_id"; export OPENEDX_API_CLIENT_SECRET="dummy_secret"; export OPENEDX_API_KEY="dummy_key"; export DATABASE_URL="postgres://mitxonline:dummy_password@localhost/mitxonline"; pytest -v -p no:cov -o addopts=""

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
export SECRET_KEY="django-insecure-test-key"; export MITX_ONLINE_BASE_URL="http://localhost"; export MAILGUN_SENDER_DOMAIN="example.com"; export MAILGUN_KEY="dummy_key"; export MITX_ONLINE_ADMIN_EMAIL="admin@example.com"; export OPENEDX_API_CLIENT_ID="dummy_id"; export OPENEDX_API_CLIENT_SECRET="dummy_secret"; export OPENEDX_API_KEY="dummy_key"; export DATABASE_URL="postgres://mitxonline:dummy_password@localhost/mitxonline"; pytest -v -p no:cov -o addopts=""

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
FROM python:3.9.6

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
RUN git clone https://github.com/mitodl/mitxonline.git /home/mitxonline

WORKDIR /home/mitxonline
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("mitodl", "mitxonline_1311_to_1017")
class MITXONLINE_1311_TO_1017(Instance):
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

        # Regex patterns to match test cases with leading line numbers
        # Pattern 1: [line_num] test_name STATUS [percentage]
        pattern1 = re.compile(
            r"""^\s*([\w\/\.\:\s\[\]()'"\-]+)\s+(ERROR|FAILED|PASSED|SKIPPED)\s+(\[\s*\d+%\s*\])?""",
            re.IGNORECASE,
        )
        # Pattern 2: STATUS test_name - message (matches status followed by test name)
        pattern2 = re.compile(
            r"""^\s*(ERROR|FAILED|PASSED|SKIPPED)\s+([\w\/\.\:\s\[\]()'"\-]+)\s+\-?""",
            re.IGNORECASE,
        )
        for line in log.split("\n"):
            # Check pattern 1
            match = pattern1.search(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
            else:
                # Check pattern 2
                match = pattern2.search(line)
                if match:
                    status = match.group(1)
                    test_name = match.group(2)
                else:
                    continue  # No match
            # Categorize based on status
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status in ("FAILED", "ERROR"):
                failed_tests.add(test_name)
            elif status == "SKIPPED":
                skipped_tests.add(test_name)
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
