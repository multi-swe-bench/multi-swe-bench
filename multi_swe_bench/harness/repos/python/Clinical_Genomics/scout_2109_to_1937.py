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
apt-get update && apt-get install -y libcairo2 libpango1.0-0 libpangocairo-1.0-0 mongodb
###ACTION_DELIMITER###
apt-cache search mongodb
###ACTION_DELIMITER###
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - && echo 'deb http://repo.mongodb.org/apt/debian bookworm/mongodb-org/6.0 main' > /etc/apt/sources.list.d/mongodb-org-6.0.list && apt-get update && apt-get install -y mongodb-org
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget gnupg
###ACTION_DELIMITER###
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-6.0.gpg && echo 'deb [signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg] http://repo.mongodb.org/apt/debian bookworm/mongodb-org/6.0 main' | tee /etc/apt/sources.list.d/mongodb-org-6.0.list && apt-get update && apt-get install -y mongodb-org
###ACTION_DELIMITER###
echo 'deb [signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg] http://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main' | tee /etc/apt/sources.list.d/mongodb-org-6.0.list && apt-get update && apt-get install -y mongodb-org
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye main' | tee /etc/apt/sources.list.d/bullseye.list && apt-get update && apt-get install -y libssl1.1
###ACTION_DELIMITER###
apt-get install -y mongodb-org
###ACTION_DELIMITER###
mkdir -p /var/lib/mongodb /var/log/mongodb && chown -R mongodb:mongodb /var/lib/mongodb /var/log/mongodb && mongod --fork --logpath /var/log/mongodb/mongod.log
###ACTION_DELIMITER###
cat /var/log/mongodb/mongod.log
###ACTION_DELIMITER###
mongod --dbpath /var/lib/mongodb --fork --logpath /var/log/mongodb/mongod.log
###ACTION_DELIMITER###
pip install --editable .
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential zlib1g-dev libbz2-dev liblzma-dev libhts-dev
###ACTION_DELIMITER###
pip install --editable .
###ACTION_DELIMITER###
pip install cython
###ACTION_DELIMITER###
pip install --editable .
###ACTION_DELIMITER###
pip install Cython==0.29.36 && pip install cyvcf2==0.9.0
###ACTION_DELIMITER###
pip install --editable .
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install mongomock
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install Flask==1.1.4
###ACTION_DELIMITER###
pip install --upgrade Flask>=2.3.0 Flask-Markdown>=0.11.1
###ACTION_DELIMITER###
pip install --upgrade Flask>=2.3.0 Flask-Markdown>=0.11.1 flask-debugtoolbar>=0.16.0 flask-babel>=4.0.0
###ACTION_DELIMITER###
pip install --upgrade Flask Flask-Markdown flask-debugtoolbar flask-babel
###ACTION_DELIMITER###
pip install --upgrade Flask-Markdown
###ACTION_DELIMITER###
pip install Flask-Markdown==0.11.1
###ACTION_DELIMITER###
sed -i 's/from flask import Markup/from markupsafe import Markup/' /usr/local/lib/python3.9/site-packages/flaskext/markdown.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libcairo2
###ACTION_DELIMITER###
apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install WTForms==2.3.3
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install --upgrade mongomock
###ACTION_DELIMITER###
pip install mongomock==3.20.0
###ACTION_DELIMITER###
pip install pymongo==3.12.3
###ACTION_DELIMITER###
pip install mongomock==4.0.0
###ACTION_DELIMITER###
echo 'export SCOUT_DB_URI=mongodb://localhost:27017/test
pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.19.5
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y ca-certificates && update-ca-certificates
###ACTION_DELIMITER###
echo -n | openssl s_client -connect compbio.charite.de:443 | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > /usr/local/share/ca-certificates/compbio.charite.de.crt && update-ca-certificates
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
export SCOUT_DB_URI=mongodb://localhost:27017/test
pytest -v --no-header -rA --tb=no -p no:cacheprovider

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
export SCOUT_DB_URI=mongodb://localhost:27017/test
pytest -v --no-header -rA --tb=no -p no:cacheprovider

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
export SCOUT_DB_URI=mongodb://localhost:27017/test
pytest -v --no-header -rA --tb=no -p no:cacheprovider

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
RUN git clone https://github.com/Clinical-Genomics/scout.git /home/scout

WORKDIR /home/scout
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Clinical-Genomics", "scout_2109_to_1937")
class SCOUT_2109_TO_1937(Instance):
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
        # Compile regex pattern to match test cases and their status
        pattern = re.compile(
            r'(tests/[\w/]+\.py::\w+)\s+(PASSED|FAILED|SKIPPED)|(PASSED|FAILED|SKIPPED)\s+(tests/[\w/]+\.py::\w+)'
        )
        # Iterate through each line in the log
        for line in log.splitlines():
            match = pattern.search(line)
            if match:
                # Extract test name and status from the matched groups
                if match.group(1) and match.group(2):
                    test_name = match.group(1)
                    status = match.group(2)
                else:
                    test_name = match.group(4)
                    status = match.group(3)
                # Add to the corresponding set
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
