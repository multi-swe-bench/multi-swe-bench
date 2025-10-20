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
        return "registry.opensuse.org/opensuse/leap:15.4"
    
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
                """ls .github/workflows
###ACTION_DELIMITER###
./docker/develop/scripts/setup-supervisor.sh
###ACTION_DELIMITER###
ln -s /home/cobbler /code
###ACTION_DELIMITER###
./docker/develop/scripts/setup-supervisor.sh
###ACTION_DELIMITER###
zypper install -y apache2 hostname make supervisor openldap2-client && mkdir -p /etc/supervisord.d/ /var/lib/dhcp/db/
###ACTION_DELIMITER###
./docker/develop/scripts/setup-supervisor.sh
###ACTION_DELIMITER###
pip install sphinx && zypper install -y iproute2 && useradd -r nobody
###ACTION_DELIMITER###
zypper install -y python3-pip iproute2 && useradd -r nobody && pip3 install sphinx
###ACTION_DELIMITER###
zypper install -y openldap2
###ACTION_DELIMITER###
zypper install -y dnf
###ACTION_DELIMITER###
./docker/develop/scripts/setup-supervisor.sh
###ACTION_DELIMITER###
pip3 install coverage
###ACTION_DELIMITER###
./docker/develop/scripts/setup-supervisor.sh
###ACTION_DELIMITER###
pip3 install distro
###ACTION_DELIMITER###
pip3 install Cheetah3 dnspython file-magic gunicorn netaddr pymongo python-ldap pyyaml schema
###ACTION_DELIMITER###
zypper install -y gcc python3-devel openldap2-devel
###ACTION_DELIMITER###
pip3 install Cheetah3 dnspython file-magic gunicorn netaddr pymongo python-ldap pyyaml schema
###ACTION_DELIMITER###
zypper install -y cyrus-sasl-devel
###ACTION_DELIMITER###
pip3 install Cheetah3 dnspython file-magic gunicorn netaddr pymongo python-ldap pyyaml schema
###ACTION_DELIMITER###
pip3 install pytest
###ACTION_DELIMITER###
echo 'pytest -v --cov=./cobbler --benchmark-skip' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip3 install pytest-cov pytest-benchmark
###ACTION_DELIMITER###
echo 'pytest -v -p pytest_cov -p pytest_benchmark --cov=cobbler --benchmark-skip' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cobblerd start && sleep 5 && cobblerd status
###ACTION_DELIMITER###
cobblerd -F & sleep 5 && ps aux | grep cobblerd
###ACTION_DELIMITER###
mkdir -p /srv/tftpboot && cobblerd -F & sleep 5 && ps aux | grep cobblerd
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
systemctl start mongodb apache2 && cobbler check && cobbler sync && bash test_commands.sh
###ACTION_DELIMITER###
apache2ctl start && mongod --fork --logpath /var/log/mongodb.log && cobbler check && cobbler sync && bash test_commands.sh
###ACTION_DELIMITER###
pkill mongod; mongod --fork --logpath /var/log/mongodb.log; cobbler check; cobbler sync; bash test_commands.sh
###ACTION_DELIMITER###
mkdir -p /data/db && chown -R mongodb:mongodb /data/db && mongod --fork --logpath /var/log/mongodb.log && apache2ctl start && cobblerd -F & sleep 10 && cobbler check && cobbler sync && bash test_commands.sh
###ACTION_DELIMITER###
useradd -r mongodb && mkdir -p /data/db && chown -R mongodb:mongodb /data/db && mongod --fork --logpath /var/log/mongodb.log && a2enmod proxy proxy_http && cp /home/cobbler/docker/develop/apache/cobbler.conf /etc/apache2/conf.d/ && apache2ctl start && cobblerd -F & sleep 10 && cobbler check && cobbler sync && bash test_commands.sh
###ACTION_DELIMITER###
groupadd -r mongodb && useradd -r -g mongodb mongodb && mkdir -p /data/db && chown -R mongodb:mongodb /data/db && mongod --fork --logpath /var/log/mongodb.log && a2enmod proxy proxy_http && cp /home/cobbler/docker/develop/apache/cobbler.conf /etc/apache2/conf.d/ && apache2ctl restart && cobblerd -F & sleep 15 && cobbler check && cobbler sync && bash test_commands.sh
###ACTION_DELIMITER###
chown -R mongodb:mongodb /data/db; mongod --fork --logpath /var/log/mongodb.log; a2enmod proxy proxy_http; cp /home/cobbler/docker/develop/apache/cobbler.conf /etc/apache2/conf.d/; apache2ctl restart; cobblerd -F & sleep 15; cobbler check; cobbler sync; bash test_commands.sh
###ACTION_DELIMITER###
pkill mongod; rm -rf /data/db/*; mkdir -p /data/db /var/www/cobbler; chown -R mongodb:mongodb /data/db; mongod --fork --logpath /var/log/mongodb.log; cobblerd -F & sleep 10; bash test_commands.sh
###ACTION_DELIMITER###
mkdir -p /var/lib/tftpboot /var/www/cobbler; chown -R mongodb:mongodb /data/db; pkill mongod; rm -f /data/db/mongod.lock; mongod --fork --logpath /var/log/mongodb.log; cobblerd -F & sleep 10; cobbler check; cobbler sync; bash test_commands.sh
###ACTION_DELIMITER###
zypper install -y wget; pkill -f cobblerd; fuser -k 25151/tcp; rm -rf /data/db/*; mongod --fork --logpath /var/log/mongodb.log; cobblerd -F & sleep 10; cobbler check; cobbler sync; bash test_commands.sh
###ACTION_DELIMITER###
zypper install -y psmisc; pkill -f mongod; rm -rf /data/db/*; mongod --fork --logpath /var/log/mongodb.log; pkill -f cobblerd; fuser -k 25151/tcp; cobblerd -F & sleep 10; cobbler check; cobbler sync; bash test_commands.sh
###ACTION_DELIMITER###
chown -R mongodb:mongodb /data/db; rm -f /data/db/mongod.lock; mongod --logpath /var/log/mongodb.log --fork; sleep 5; cobblerd -F & sleep 10; apache2ctl start; cobbler check; cobbler sync; bash test_commands.sh
###ACTION_DELIMITER###
pkill mongod; rm -rf /data/db; mkdir -p /data/db; chown -R mongodb:mongodb /data/db; mongod --fork --logpath /var/log/mongodb.log; sleep 5; fuser -k 25151/tcp; cobblerd -F & sleep 10; apache2ctl start; cobbler check; cobbler sync; bash test_commands.sh
###ACTION_DELIMITER###
pkill -f 'mongod|cobblerd|httpd'; rm -rf /data/db /var/lib/mongodb; mkdir -p /data/db /var/www/cobbler /srv/tftpboot; chown -R mongodb:mongodb /data/db; mongod --fork --logpath /var/log/mongodb.log; sleep 5; cobblerd -F & sleep 10; apache2ctl start; cobbler check; cobbler sync; bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v -p pytest_cov -p pytest_benchmark --cov=cobbler --benchmark-skip

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
pytest -v -p pytest_cov -p pytest_benchmark --cov=cobbler --benchmark-skip

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
pytest -v -p pytest_cov -p pytest_benchmark --cov=cobbler --benchmark-skip

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
FROM registry.opensuse.org/opensuse/leap:15.4

## Set noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Install basic requirements
# For example: RUN apt-get update && apt-get install -y git
# For example: RUN yum install -y git
# For example: RUN apk add --no-cache git
RUN zypper install --no-recommends -y git

# Ensure bash is available
RUN if [ ! -f /bin/bash ]; then         if command -v apk >/dev/null 2>&1; then             apk add --no-cache bash;         elif command -v apt-get >/dev/null 2>&1; then             apt-get update && apt-get install -y bash;         elif command -v yum >/dev/null 2>&1; then             yum install -y bash;         else             exit 1;         fi     fi

WORKDIR /home/
COPY fix.patch /home/
COPY test.patch /home/
RUN git clone https://github.com/cobbler/cobbler.git /home/cobbler

WORKDIR /home/cobbler
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("cobbler", "cobbler_3363_to_3240")
class COBBLER_3363_TO_3240(Instance):
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
        # Regex patterns to match test lines
        # Pattern 1: Test name followed by status and percentage (e.g., "tests/... PASSED [  0%]")
        pattern1 = re.compile(r'^(tests/.+?) (PASSED|FAILED|SKIPPED)\s+\[\s*\d+%\s*\]$', re.IGNORECASE)
        # Pattern 2: Status followed by test name (e.g., "ERROR tests/... - ..." or "ERROR tests/...")
        pattern2 = re.compile(r'^(ERROR|FAILED) (tests/.+?)(?: - .*)?$')
        for line in log.split('\n'):
            line = line.strip()
            if not line:
                continue
            # Check pattern 1
            match = pattern1.match(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
                continue
            # Check pattern 2
            match = pattern2.match(line)
            if match:
                test_name = match.group(2)
                failed_tests.add(test_name)
                continue
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
