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
        return "ubuntu:latest"
    
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
                """ls
###ACTION_DELIMITER###
pip install --editable .
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3-pip
###ACTION_DELIMITER###
pip install --editable .
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install --editable .
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo '/home/scout/venv/bin/pytest --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0 wkhtmltopdf
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y mongodb && service mongodb start
###ACTION_DELIMITER###
apt-get update && apt-get install -y mongodb-server && service mongodb start
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository universe && apt-get update && apt-get install -y mongodb
###ACTION_DELIMITER###
apt-cache search mongodb
###ACTION_DELIMITER###
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | apt-key add -
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg
###ACTION_DELIMITER###
echo 'deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/7.0 multiverse' | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
###ACTION_DELIMITER###
apt-get update && apt-get install -y mongodb-org && systemctl start mongod
###ACTION_DELIMITER###
echo 'deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse' | tee /etc/apt/sources.list.d/mongodb-org-7.0.list && apt-get update
###ACTION_DELIMITER###
apt-get install -y mongodb-org && systemctl start mongod
###ACTION_DELIMITER###
mongod --fork --logpath /var/log/mongodb.log
###ACTION_DELIMITER###
mongod --logpath /var/log/mongodb.log
###ACTION_DELIMITER###
cat /var/log/mongodb.log
###ACTION_DELIMITER###
mkdir -p /data/db && chown -R mongodb:mongodb /data/db
###ACTION_DELIMITER###
mongod --fork --logpath /var/log/mongodb.log
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo '/home/scout/venv/bin/pytest --no-header -rA --tb=no -p no:cacheprovider --maxfail=0' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
/home/scout/venv/bin/pytest --no-header -rA --tb=no -p no:cacheprovider --maxfail=0

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
/home/scout/venv/bin/pytest --no-header -rA --tb=no -p no:cacheprovider --maxfail=0

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
/home/scout/venv/bin/pytest --no-header -rA --tb=no -p no:cacheprovider --maxfail=0

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:latest with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:latest

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


@Instance.register("Clinical-Genomics", "scout_4230_to_4027")
class SCOUT_4230_TO_4027(Instance):
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
        passed_tests = set() # Tests that passed successfully
        failed_tests = set() # Tests that failed
        skipped_tests = set() # Tests that were skipped
        import re
        import json
        # TODO: Implement the parse_log function
        # Pattern for PASSED tests: captures test name followed by PASSED
        passed_pattern = re.compile(r'(?<=PASSED\s)tests/[^\s]+|tests/[^\s]+(?=\s+PASSED)')
        # Pattern for FAILED tests: captures test name preceded by FAILED
        failed_pattern = re.compile(r'FAILED\s+(tests/[^\s]+)')
        # Find all passed tests
        passed_tests.update(passed_pattern.findall(log))
        # Find all failed tests
        failed_tests.update(failed_pattern.findall(log))
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
