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
                """sed -i '36s/\'pytest\'/\'pytest>=7.0.0\'/' setup.py
###ACTION_DELIMITER###
sed -i "s/'pytest'/'pytest>=7.0.0'/" setup.py
###ACTION_DELIMITER###
pip install -e .[test]
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip install -e .[test]
###ACTION_DELIMITER###
sed -i 's/python-rapidjson==0.0.6/python-rapidjson>=1.0.0/' setup.py
###ACTION_DELIMITER###
pip install -e .[test]
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
pkill rethinkdb || true
rm -rf rethinkdb_test_data || true
rethinkdb --daemon --directory rethinkdb_test_data --no-http-admin
for i in {1..60}; do nc -z localhost 28015 && break; sleep 1; done
pytest -v --tb=line -p no:cacheprovider --timeout 300' > /home/bigchaindb/test_commands.sh && chmod +x /home/bigchaindb/test_commands.sh
###ACTION_DELIMITER###
bash /home/bigchaindb/test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y procps
###ACTION_DELIMITER###
echo 'deb https://download.rethinkdb.com/repository/debian-bookworm bookworm main' > /etc/apt/sources.list.d/rethinkdb.list && wget -qO- https://download.rethinkdb.com/repository/raw/pubkey.gpg | gpg --dearmor -o /etc/apt/trusted.gpg.d/rethinkdb.gpg && apt-get update && apt-get install -y rethinkdb
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 1D85E93F801BB43F
###ACTION_DELIMITER###
apt-get update && apt-get install -y rethinkdb
###ACTION_DELIMITER###
bash /home/bigchaindb/test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y netcat-openbsd
###ACTION_DELIMITER###
sed -i 's/pytest-cov==2.2.1/pytest-cov>=4.0.0/' setup.py
###ACTION_DELIMITER###
pip install -e .[test]
###ACTION_DELIMITER###
bash /home/bigchaindb/test_commands.sh
###ACTION_DELIMITER###
pip install pytest-timeout
###ACTION_DELIMITER###
bash /home/bigchaindb/test_commands.sh
###ACTION_DELIMITER###
pip install Jinja2==2.11.3
###ACTION_DELIMITER###
bash /home/bigchaindb/test_commands.sh
###ACTION_DELIMITER###
pip install markupsafe==1.1.1
###ACTION_DELIMITER###
pip install Werkzeug==0.10.4
###ACTION_DELIMITER###
pip install rethinkdb==2.3.0.post6
###ACTION_DELIMITER###
sed -i 's/pytest>=7.0.0/pytest<5.0/' setup.py && pip install -e .[test] && pip install pytest-timeout==1.4.2
###ACTION_DELIMITER###
bash /home/bigchaindb/test_commands.sh
###ACTION_DELIMITER###
pip install itsdangerous==0.24
###ACTION_DELIMITER###
bash /home/bigchaindb/test_commands.sh
###ACTION_DELIMITER###
pip install pytest-cov==2.12.1
###ACTION_DELIMITER###
pip install pytest-cov==2.5.1
###ACTION_DELIMITER###
pip install pytest-cov==1.8.1
###ACTION_DELIMITER###
pip install pytest-cov==2.5.1 coverage==4.5.4
###ACTION_DELIMITER###
pip install pytest-cov==2.10.1
###ACTION_DELIMITER###
bash /home/bigchaindb/test_commands.sh
###ACTION_DELIMITER###
pip install pytest==3.6.0
###ACTION_DELIMITER###
pip install pytest-xdist==1.20.0 pytest-forked==1.0.2 pytest-cov==2.5.1
###ACTION_DELIMITER###
bash /home/bigchaindb/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
pkill rethinkdb || true
rm -rf rethinkdb_test_data || true
rethinkdb --daemon --directory rethinkdb_test_data --cache-size 512 --no-http-admin
for i in {1..60}; do nc -z localhost 28015 && break; sleep 1; done
sleep 5
pytest -v --tb=line -p no:cacheprovider --timeout 600 -n 1' > /home/bigchaindb/test_commands.sh && chmod +x /home/bigchaindb/test_commands.sh
###ACTION_DELIMITER###
bash /home/bigchaindb/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
pkill rethinkdb || true
rm -rf rethinkdb_test_data || true
rethinkdb --daemon --directory rethinkdb_test_data --cache-size 1024 --no-http-admin
for i in {1..60}; do nc -z localhost 28015 && break; sleep 1; done
sleep 10
pytest -v --tb=line -p no:cacheprovider --timeout 600' > /home/bigchaindb/test_commands.sh && chmod +x /home/bigchaindb/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e
pkill rethinkdb || true
rm -rf rethinkdb_test_data || true
rethinkdb --daemon --directory rethinkdb_test_data --cache-size 1024 --no-http-admin
for i in {1..60}; do nc -z localhost 28015 && break; sleep 1; done
sleep 10
pytest -v --tb=line -p no:cacheprovider --timeout 600

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
#!/bin/bash
set -e
pkill rethinkdb || true
rm -rf rethinkdb_test_data || true
rethinkdb --daemon --directory rethinkdb_test_data --cache-size 1024 --no-http-admin
for i in {1..60}; do nc -z localhost 28015 && break; sleep 1; done
sleep 10
pytest -v --tb=line -p no:cacheprovider --timeout 600

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
#!/bin/bash
set -e
pkill rethinkdb || true
rm -rf rethinkdb_test_data || true
rethinkdb --daemon --directory rethinkdb_test_data --cache-size 1024 --no-http-admin
for i in {1..60}; do nc -z localhost 28015 && break; sleep 1; done
sleep 10
pytest -v --tb=line -p no:cacheprovider --timeout 600

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim with actual base image
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
RUN git clone https://github.com/bigchaindb/bigchaindb.git /home/bigchaindb

WORKDIR /home/bigchaindb
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("bigchaindb", "bigchaindb_515_to_471")
class BIGCHAINDB_515_TO_471(Instance):
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
        # Regex pattern to match test lines
        pattern = re.compile(r'.*?(tests/[\w/\.]+::[^\s]+)\s+(PASSED|FAILED|SKIPPED|ERROR)')
        matches = pattern.findall(log)
        for test_name, status in matches:
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
            else:
                # Handle ERROR, FAILED, Timeout, etc. as failed
                failed_tests.add(test_name)
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
