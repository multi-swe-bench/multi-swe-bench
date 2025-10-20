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
                """ls -la
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
echo -e 'npm test -- --verbose
npm run test:integration -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y mongodb
###ACTION_DELIMITER###
curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-6.0.gpg && echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main" > /etc/apt/sources.list.d/mongodb-org-6.0.list && apt-get update && apt-get install -y mongodb-org
###ACTION_DELIMITER###
mkdir -p /data/db && chown -R mongodb:mongodb /data/db && mongod --fork --logpath /var/log/mongodb.log"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npm test -- --verbose
npm run test:integration -- --verbose

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
npm test -- --verbose
npm run test:integration -- --verbose

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
npm test -- --verbose
npm run test:integration -- --verbose

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
RUN git clone https://github.com/CVEProject/cve-services.git /home/cve-services

WORKDIR /home/cve-services
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("CVEProject", "cve_services_1086_to_1008")
class CVE_SERVICES_1086_TO_1008(Instance):
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
        test_status = {}
        # Pattern for passed tests: Capture indented test names (exclude duration)
        passed_pattern = re.compile(r'^\s{6,}✔\s*(.*?)\s*(?:\(\d+ms\))?\s*$', re.MULTILINE)  # Matches indented ✔
        for match in passed_pattern.finditer(log):
            test_name = match.group(1).strip()
            if test_name:
                test_status[test_name] = 'passed'
        # Pattern for failed tests: Match indented test cases (6+ spaces)
        failed_pattern = re.compile(r'^\s{6,}\d+\)\s*(?!.*hook)(?!.*Error:)(?!.*at )(.*?)\s*$', re.MULTILINE)  # Matches indented failed tests
        for match in failed_pattern.finditer(log):
            test_name = match.group(1).strip()
            if test_name:
                test_status[test_name] = 'failed'
        # Skipped tests: Disabled (no valid markers observed)
        # skipped_pattern = re.compile(r'^\s*SKIPPED\s*(.*?)\s*$', re.MULTILINE)  # Placeholder for future use
        # for match in skipped_pattern.finditer(log):
        #     test_name = match.group(1).strip()
        #     if test_name:
        #         test_status[test_name] = 'skipped'
        passed_tests = set(name for name, status in test_status.items() if status == 'passed')
        failed_tests = set(name for name, status in test_status.items() if status == 'failed')
        skipped_tests = set(name for name, status in test_status.items() if status == 'skipped')
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
