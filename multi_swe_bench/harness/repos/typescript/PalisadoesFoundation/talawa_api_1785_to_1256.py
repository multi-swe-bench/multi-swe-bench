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
        return "node:18-bullseye"
    
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
                """echo 'npm test -- --reporter verbose' > /home/talawa-api/test_commands.sh
###ACTION_DELIMITER###
cp .env.sample .env && ACCESS_TOKEN_SECRET=$(openssl rand -hex 32) && REFRESH_TOKEN_SECRET=$(openssl rand -hex 32) && sed -i 's/^MONGO_DB_URL=.*/MONGO_DB_URL=mongodb:\/\/localhost:27017\/talawa-api/' .env && sed -i 's/^REDIS_HOST=.*/REDIS_HOST=localhost/' .env && sed -i 's/^REDIS_PORT=.*/REDIS_PORT=6379/' .env && sed -i "s/^ACCESS_TOKEN_SECRET=.*/ACCESS_TOKEN_SECRET=$ACCESS_TOKEN_SECRET/" .env && sed -i "s/^REFRESH_TOKEN_SECRET=.*/REFRESH_TOKEN_SECRET=$REFRESH_TOKEN_SECRET/" .env
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
service mongod start && service redis-server start
###ACTION_DELIMITER###
mongod --fork --logpath /var/log/mongodb.log && redis-server --daemonize yes
###ACTION_DELIMITER###
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - && echo "deb http://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list && apt-get update && apt-get install -y mongodb-org redis-server && mongod --fork --logpath /var/log/mongodb.log && redis-server --daemonize yes
###ACTION_DELIMITER###
mkdir -p /data/db && chown -R mongodb:mongodb /data/db && mongod --fork --logpath /var/log/mongodb.log && redis-server --daemonize yes
###ACTION_DELIMITER###
npm run setup
###ACTION_DELIMITER###
apt-get install -y expect && printf '#!/usr/bin/expect -f
set timeout 60
spawn npm run setup
expect "Select Node environment:"
send "development\r"
expect "Would you like to generate a new access token secret? (y/N)"
send "n\r"
expect "Would you like to generate a new refresh token secret? (y/N)"
send "n\r"
expect "Would you like to enable logging for the database transactions? (Y/n)"
send "n\r"
expect "Are you setting up this project using Docker? (y/N)"
send "n\r"
expect "Would you like to change the existing Redis URL? (y/N)"
send "n\r"
expect "Would you like to change the existing Mongo DB URL? (y/N)"
send "n\r"
expect "Would you like to set up a reCAPTCHA secret key? (Y/n)"
send "n\r"
expect "Would you like to setup the mail username and password? (Y/n)"
send "n\r"
expect "Would you like to configure SMTP for Talawa to send emails? (Y/n)"
send "n\r"
expect "Would you like to setup a Super Admin email of last resort? (Y/n)"
send "n\r"
expect "Do you want to import sample data? (y/N)"
send "n\r"
expect "Enter the maximum size limit of Images uploaded (in MB) max: 20 (3)"
send "3\r"
expect eof' > setup_automator.exp && chmod +x setup_automator.exp && ./setup_automator.exp"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npm test -- --reporter verbose

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
npm test -- --reporter verbose

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
npm test -- --reporter verbose

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
FROM node:18-bullseye

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
RUN git clone https://github.com/PalisadoesFoundation/talawa-api.git /home/talawa-api

WORKDIR /home/talawa-api
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("PalisadoesFoundation", "talawa_api_1785_to_1256")
class TALAWA_API_1785_TO_1256(Instance):
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
        # Pattern for passed tests (handles leading characters and multi-line names)
        passed_pattern = re.compile(r'^\s*✓\s+(.*?)(?=\n\s*[✓FAIL]|$)', re.DOTALL | re.MULTILINE)
        passed_tests.update(m.group(1).replace('\n', ' ').strip() for m in passed_pattern.finditer(log))
        # Pattern for failed tests (handles leading characters and multi-line names)
        failed_pattern = re.compile(r'^\s*FAIL\s+(tests/.+?spec\.ts > .+?)(?=\s+(AssertionError:|Error:|$))', re.DOTALL | re.MULTILINE)
        failed_tests.update(m.group(1).replace('\n', ' ').strip() for m in failed_pattern.finditer(log))
        # Pattern for skipped tests (handles leading characters and multi-line names)
        skipped_pattern = re.compile(r'^\s*SKIPPED\s+(.*?)(?=\n\s*[✓FAILSKIPPED]|$)', re.DOTALL | re.MULTILINE)
        skipped_tests.update(m.group(1).replace('\n', ' ').strip() for m in skipped_pattern.finditer(log))
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
