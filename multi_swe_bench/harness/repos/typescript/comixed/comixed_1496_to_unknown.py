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
        return "eclipse-temurin:17-jdk-focal"
    
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
apt-get update && apt-get install -y maven
###ACTION_DELIMITER###
echo 'mvn clean test -Dstyle.color=never' > test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y nodejs npm && npm install -g yarn
###ACTION_DELIMITER###
echo -e 'mvn clean test -Dstyle.color=never
cd comixed-webui && yarn test --verbose' > test_commands.sh
###ACTION_DELIMITER###
cd comixed-webui && yarn install
###ACTION_DELIMITER###
curl -sL https://deb.nodesource.com/setup_14.x | bash - && apt-get install -y nodejs
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo -e 'mvn clean test -Dstyle.color=never
cd comixed-webui && yarn test --verbose' > /home/comixed/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
mvn clean test -Dstyle.color=never
cd comixed-webui && yarn test --verbose

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
mvn clean test -Dstyle.color=never
cd comixed-webui && yarn test --verbose

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
mvn clean test -Dstyle.color=never
cd comixed-webui && yarn test --verbose

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

# Choose an appropriate base image based on the project's requirements - replace eclipse-temurin:17-jdk-focal with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM eclipse-temurin:17-jdk-focal

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
RUN git clone https://github.com/comixed/comixed.git /home/comixed

WORKDIR /home/comixed
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("comixed", "comixed_1496_to_unknown")
class COMIXED_1496_TO_UNKNOWN(Instance):
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
        # Pattern to match test status lines
        status_pattern = r"\[INFO\] Tests run: \d+, Failures: (\d+), Errors: (\d+), Skipped: (\d+), .* - in (.*)"
        status_matches = re.findall(status_pattern, log)
        for failures, errors, skipped, test_name in status_matches:
            failures = int(failures)
            errors = int(errors)
            skipped = int(skipped)
            if skipped > 0:
                skipped_tests.add(test_name)
            elif failures > 0 or errors > 0:
                failed_tests.add(test_name)
            else:
                passed_tests.add(test_name)
        # Pattern to match error lines in test files
        error_pattern = r"src/test/java/([\w/]+Test)\.java"
        error_matches = re.findall(error_pattern, log)
        for path in error_matches:
            full_test_name = path.replace('/', '.')
            # Add to failed_tests if not already in another set
            if full_test_name not in passed_tests and full_test_name not in skipped_tests:
                failed_tests.add(full_test_name)
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
