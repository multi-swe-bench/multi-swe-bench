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
                """ls -la
###ACTION_DELIMITER###
ls gulp
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
cp config.json.example config.json
###ACTION_DELIMITER###
bower install -f
###ACTION_DELIMITER###
./node_modules/.bin/bower install -f
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
###ACTION_DELIMITER###
nvm install 6.9.1
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
npm install -g npm@4
###ACTION_DELIMITER###
./node_modules/.bin/bower install -f
###ACTION_DELIMITER###
./node_modules/.bin/bower install -f --allow-root
###ACTION_DELIMITER###
npm install -g bower@1.8.8
###ACTION_DELIMITER###
bower install -f --allow-root
###ACTION_DELIMITER###
npm test -- --verbose
###ACTION_DELIMITER###
apt-get update && apt-get install -y mongodb && mongod --fork --logpath /var/log/mongodb.log
###ACTION_DELIMITER###
apt-get update && apt-get install -y mongodb-server && service mongodb start
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget && wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - && echo 'deb http://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main' > /etc/apt/sources.list.d/mongodb-org-6.0.list && apt-get update && apt-get install -y mongodb-org && mongod --fork --logpath /var/log/mongodb.log
###ACTION_DELIMITER###
wget http://security.debian.org/debian-security/pool/updates/main/o/openssl/libssl1.1_1.1.1w-0+deb11u1_amd64.deb && dpkg -i libssl1.1_1.1.1w-0+deb11u1_amd64.deb && apt-get update && apt-get install -y mongodb-org && mongod --fork --logpath /var/log/mongodb.log
###ACTION_DELIMITER###
echo 'deb http://security.debian.org/debian-security bullseye-security main' > /etc/apt/sources.list.d/bullseye-security.list && apt-get update && apt-get install -y libssl1.1 && apt-get install -y mongodb-org && mongod --fork --logpath /var/log/mongodb.log
###ACTION_DELIMITER###
mkdir -p /data/db && chown -R mongodb:mongodb /data/db && mongod --dbpath /data/db --fork --logpath /var/log/mongodb.log
###ACTION_DELIMITER###
npm test -- --verbose
###ACTION_DELIMITER###
echo 'npm test -- --verbose' > test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npm test -- --verbose

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
npm test -- --verbose

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
npm test -- --verbose

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
RUN git clone https://github.com/HabitRPG/habitica.git /home/habitica

WORKDIR /home/habitica
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("HabitRPG", "habitica_8440_to_8419")
class HABITICA_8440_TO_8419(Instance):
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
        import json
        import os

        # Clean ANSI color codes from the log
        clean_log = re.sub(r"\x1b\[\d+;\d+m|\x1b\[\d+m", "", log)
        # Extract passed tests (✓ or ✔)
        passed_tests = set()
        for line in clean_log.split("\n"):
            if "✓" in line or "✔" in line:
                match = re.search(r"^\s{4,}[✓✔]\s+(.*)", line)
                if match:
                    test_name = match.group(1).strip()
                    passed_tests.add(test_name)
        # Extract failed tests (✖)
        failed_tests = set()
        for line in clean_log.split("\n"):
            if "✖" in line:
                match = re.search(r"✖\s+(.*)", line)
                if match:
                    test_name = match.group(1).strip()
                    failed_tests.add(test_name)
        # Extract skipped tests (from "skipped mocha test" warnings)
        skipped_tests = set()
        lines = clean_log.split("\n")
        for i, line in enumerate(lines):
            if "skipped mocha test" in line:
                if i > 0:
                    file_line = lines[i - 1].strip()
                    # Extract file path by removing the line number prefix
                    file_path = re.sub(r"^\[\s*\d+\]\s*", "", file_line)
                    # Extract test name from the file path
                    test_name = os.path.basename(file_path)
                    # Remove .test.js or .js extensions
                    test_name = re.sub(r"\.test\.js$", "", test_name)
                    test_name = re.sub(r"\.js$", "", test_name)
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
