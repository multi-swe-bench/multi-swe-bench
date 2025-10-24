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
        return "node:18"

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
                """npm install
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg
###ACTION_DELIMITER###
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/7.0 main" | tee /etc/apt/sources.list.d/mongodb.list
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y mongodb-org
###ACTION_DELIMITER###
mkdir -p /data/db && chown -R mongodb:mongodb /data/db
###ACTION_DELIMITER###
mongod --fork --logpath /var/log/mongodb.log
###ACTION_DELIMITER###
cp .env.sample .env
###ACTION_DELIMITER###
sed -i 's|MONGO_DB_URL=|MONGO_DB_URL=mongodb://localhost:27017/talawa-api|' .env
###ACTION_DELIMITER###
ACCESS_TOKEN=$(openssl rand -hex 32) && sed -i "s/ACCESS_TOKEN_SECRET=/ACCESS_TOKEN_SECRET=$ACCESS_TOKEN/" .env && REFRESH_TOKEN=$(openssl rand -hex 32) && sed -i "s/REFRESH_TOKEN_SECRET=/REFRESH_TOKEN_SECRET=$REFRESH_TOKEN/" .env
###ACTION_DELIMITER###
echo 'npm test -- --reporter verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npm test -- --reporter verbose

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
npm test -- --reporter verbose

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
npm test -- --reporter verbose

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

# Choose an appropriate base image based on the project's requirements - replace node:18 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:18

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


@Instance.register("PalisadoesFoundation", "talawa_api_1139_to_756")
class TALAWA_API_1139_TO_756(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        import json

        # Split log into lines
        lines = log.split("\n")
        current_status = None
        current_test = []
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue  # Skip empty lines
            # Check if line starts with a status symbol (✓ for passed, × for failed)
            if stripped_line.startswith(("✓", "×")):
                # Process previous test if it exists
                if current_status:
                    test_name = " ".join(current_test).strip()
                    if current_status == "passed":
                        passed_tests.add(test_name)
                    elif current_status == "failed":
                        failed_tests.add(test_name)
                    current_test = []
                # Set current status and start collecting test parts
                current_status = "passed" if stripped_line.startswith("✓") else "failed"
                test_part = stripped_line[
                    1:
                ].strip()  # Remove status symbol and leading space
                current_test.append(test_part)
            # Check if line is an error message (ends current test)
            elif stripped_line.startswith("→"):
                if current_status:
                    test_name = " ".join(current_test).strip()
                    if current_status == "passed":
                        passed_tests.add(test_name)
                    elif current_status == "failed":
                        failed_tests.add(test_name)
                    current_test = []
                    current_status = None
            # If line is part of the current test name (multi-line)
            elif current_status is not None:
                current_test.append(stripped_line)
        # Process the last test if it exists
        if current_status:
            test_name = " ".join(current_test).strip()
            if current_status == "passed":
                passed_tests.add(test_name)
            elif current_status == "failed":
                failed_tests.add(test_name)
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
