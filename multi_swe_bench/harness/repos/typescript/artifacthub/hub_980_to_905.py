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
        return "golang:1.21"
    
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
apt-get update
###ACTION_DELIMITER###
apt-get install -y postgresql postgresql-contrib
###ACTION_DELIMITER###
pg_ctlcluster 15 main start
###ACTION_DELIMITER###
go install github.com/jackc/tern/v2@latest
###ACTION_DELIMITER###
wget https://github.com/jackc/tern/releases/download/v2.3.3/tern_2.3.3_linux_amd64.tar.gz && tar -xzf tern_2.3.3_linux_amd64.tar.gz && mv tern_2.3.3_linux_amd64/tern /usr/local/bin/ && chmod +x /usr/local/bin/tern
###ACTION_DELIMITER###
wget https://github.com/jackc/tern/releases/download/v2.2.0/tern_2.2.0_linux_amd64.tar.gz && tar -xzf tern_2.2.0_linux_amd64.tar.gz && mv tern_2.2.0_linux_amd64/tern /usr/local/bin/ && chmod +x /usr/local/bin/tern
###ACTION_DELIMITER###
tar -xzf tern_2.2.0_linux_amd64.tar.gz && mv tern_*/tern /usr/local/bin/ && chmod +x /usr/local/bin/tern
###ACTION_DELIMITER###
tar -tzf tern_2.2.0_linux_amd64.tar.gz
###ACTION_DELIMITER###
tar -xzf tern_2.2.0_linux_amd64.tar.gz && mv tern /usr/local/bin/ && chmod +x /usr/local/bin/tern
###ACTION_DELIMITER###
mkdir -p ~/.cfg && echo -e '[database]\nhost = localhost\nport = 5432\ndatabase = hub\nuser = postgres\n\n[data]\nloadSampleData = true' > ~/.cfg/tern.conf
###ACTION_DELIMITER###
tern migrate --config ~/.cfg/tern.conf --migrations database/migrations
###ACTION_DELIMITER###
sed -i 's/local   all             postgres                                peer/local   all             postgres                                trust/' /etc/postgresql/15/main/pg_hba.conf && pg_ctlcluster 15 main restart
###ACTION_DELIMITER###
tern migrate --config ~/.cfg/tern.conf --migrations database/migrations
###ACTION_DELIMITER###
createdb -U postgres hub && tern migrate --config ~/.cfg/tern.conf --migrations database/migrations
###ACTION_DELIMITER###
cat /etc/postgresql/15/main/pg_hba.conf | grep -A 2 'local   all             postgres'
###ACTION_DELIMITER###
echo 'host    hub             postgres        127.0.0.1/32            trust' >> /etc/postgresql/15/main/pg_hba.conf && echo 'host    hub             postgres        ::1/128                 trust' >> /etc/postgresql/15/main/pg_hba.conf && pg_ctlcluster 15 main restart
###ACTION_DELIMITER###
psql -U postgres -c 'CREATE DATABASE hub;' && tern migrate --config ~/.cfg/tern.conf --migrations database/migrations --verbose
###ACTION_DELIMITER###
tail -n 50 /var/log/postgresql/postgresql-15-main.log
###ACTION_DELIMITER###
sed -i '/host    all             all             127.0.0.1\/32            scram-sha-256/i host    hub             postgres        127.0.0.1/32            trust' /etc/postgresql/15/main/pg_hba.conf && sed -i '/host    all             all             ::1\/128                 scram-sha-256/i host    hub             postgres        ::1/128                 trust' /etc/postgresql/15/main/pg_hba.conf && pg_ctlcluster 15 main restart
###ACTION_DELIMITER###
psql -U postgres -h localhost -d hub -c 'SELECT 1;' && tern migrate --config ~/.cfg/tern.conf --migrations database/migrations
###ACTION_DELIMITER###
ls -ld database/migrations && ls -l database/migrations
###ACTION_DELIMITER###
ls -l database/migrations/schema
###ACTION_DELIMITER###
tern migrate --config ~/.cfg/tern.conf --migrations database/migrations/schema
###ACTION_DELIMITER###
apt-get install -y postgresql-15-pgtap libtap-parser-sourcehandler-pgtap-perl
###ACTION_DELIMITER###
mkdir -p ~/.cfg && echo -e '[database]\nhost = localhost\nport = 5432\ndatabase = hub_tests\nuser = postgres\n\n[data]\nloadSampleData = false' > ~/.cfg/tern-tests.conf
###ACTION_DELIMITER###
createdb -U postgres hub_tests && tern migrate --config ~/.cfg/tern-tests.conf --migrations database/migrations/schema
###ACTION_DELIMITER###
sed -i '/host    all             all             127.0.0.1\/32            scram-sha-256/i host    hub_tests        postgres        127.0.0.1/32            trust' /etc/postgresql/15/main/pg_hba.conf && sed -i '/host    all             all             ::1\/128                 scram-sha-256/i host    hub_tests        postgres        ::1/128                 trust' /etc/postgresql/15/main/pg_hba.conf && pg_ctlcluster 15 main restart
###ACTION_DELIMITER###
psql -U postgres -h localhost -d hub_tests -c 'SELECT 1;' && tern migrate --config ~/.cfg/tern-tests.conf --migrations database/migrations/schema
###ACTION_DELIMITER###
echo 'go test -v -count=1 ./...' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
go test -v -count=1 ./...

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
go test -v -count=1 ./...

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
go test -v -count=1 ./...

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
FROM golang:1.21

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
RUN git clone https://github.com/artifacthub/hub.git /home/hub

WORKDIR /home/hub
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("artifacthub", "hub_980_to_905")
class HUB_980_TO_905(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        import json
            # Regex patterns to match test results
        passed_pattern = re.compile(r'--- PASS: (.*?) \(\d+\.\d+s\)')
        failed_pattern = re.compile(r'--- FAIL: (.*?) \(\d+\.\d+s\)')
        skipped_pattern = re.compile(r'--- SKIP: (.*?) \(\d+\.\d+s\)')
        # Split log into lines and process each line
        for line in log.split('\n'):
            # Check for passed tests
            pass_match = passed_pattern.search(line)
            if pass_match:
                test_name = pass_match.group(1).strip()
                passed_tests.add(test_name)
            # Check for failed tests
            fail_match = failed_pattern.search(line)
            if fail_match:
                test_name = fail_match.group(1).strip()
                failed_tests.add(test_name)
            # Check for skipped tests
            skip_match = skipped_pattern.search(line)
            if skip_match:
                test_name = skip_match.group(1).strip()
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
