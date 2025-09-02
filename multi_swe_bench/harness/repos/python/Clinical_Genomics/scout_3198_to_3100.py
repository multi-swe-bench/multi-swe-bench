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
cat README.md
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo 'pytest -v' > test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install 'pydantic<2.0'
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install Flask==1.1.4
###ACTION_DELIMITER###
pip install flask-debugtoolbar==0.13.1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install markupsafe==1.1.1
###ACTION_DELIMITER###
pip install --force-reinstall markupsafe==1.1.1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libcairo2
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y mongodb-server && service mongodb start
###ACTION_DELIMITER###
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - && echo 'deb http://repo.mongodb.org/apt/debian bookworm/mongodb-org/6.0 main' | tee /etc/apt/sources.list.d/mongodb-org-6.0.list && apt-get update && apt-get install -y mongodb-org-server && service mongod start
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget gnupg && wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - && echo 'deb http://repo.mongodb.org/apt/debian bookworm/mongodb-org/6.0 main' | tee /etc/apt/sources.list.d/mongodb-org-6.0.list && apt-get update && apt-get install -y mongodb-org-server && service mongod start
###ACTION_DELIMITER###
echo 'deb http://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main' | tee /etc/apt/sources.list.d/mongodb-org-6.0.list && apt-get update && apt-get install -y mongodb-org-server && service mongod start
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye main' | tee /etc/apt/sources.list.d/bullseye-main.list && apt-get update && apt-get install -y libssl1.1 && apt-get install -y mongodb-org-server && service mongod start
###ACTION_DELIMITER###
mkdir -p /data/db && chown -R mongodb:mongodb /data/db && su - mongodb -c 'mongod --dbpath /data/db --fork --logpath /var/log/mongodb.log'
###ACTION_DELIMITER###
mkdir -p /data/db && chown -R mongodb:mongodb /data/db && mongod --dbpath /data/db --fork --logpath /var/log/mongodb.log --user mongodb
###ACTION_DELIMITER###
mkdir -p /home/mongodb && chown mongodb:mongodb /home/mongodb && su mongodb -s /bin/bash -c 'mongod --dbpath /data/db --fork --logpath /var/log/mongodb.log'
###ACTION_DELIMITER###
cat /var/log/mongodb.log
###ACTION_DELIMITER###
mongod --dbpath /data/db
###ACTION_DELIMITER###
export SCOUT_DB_URI=mongomock://localhost && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y mongodb && mkdir -p /var/lib/mongodb /var/log/mongodb && chown -R mongodb:mongodb /var/lib/mongodb /var/log/mongodb && mongod --dbpath /var/lib/mongodb --fork --logpath /var/log/mongodb/mongod.log && bash test_commands.sh
###ACTION_DELIMITER###
export SCOUT_DB_URI=mongomock://localhost && bash test_commands.sh
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye main' | tee /etc/apt/sources.list.d/bullseye-main.list && apt-get update && apt-get install -y libssl1.1 mongodb-org-server && mkdir -p /data/db /var/log/mongodb && chown -R mongodb:mongodb /data/db /var/log/mongodb && mongod --dbpath /data/db --fork --logpath /var/log/mongodb/mongod.log && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y wkhtmltopdf && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
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


@Instance.register("Clinical-Genomics", "scout_3198_to_3100")
class SCOUT_3198_TO_3100(Instance):
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
        lines = log.split('\n')
        pattern1 = re.compile(r'^(?:\[\s*\d+\]\s+)?(tests/[\w/]+\.py::\w+)\s+(PASSED|FAILED|SKIPPED)\b')
        pattern2 = re.compile(r'^(?:\[\s*\d+\]\s+)?(PASSED|FAILED|SKIPPED)\s+(tests/[\w/]+\.py::\w+)\b')
        for line in lines:
            line = line.strip()
            match1 = pattern1.match(line)
            if match1:
                test_name = match1.group(1)
                status = match1.group(2)
            else:
                match2 = pattern2.match(line)
                if match2:
                    status = match2.group(1)
                    test_name = match2.group(2)
                else:
                    continue
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
