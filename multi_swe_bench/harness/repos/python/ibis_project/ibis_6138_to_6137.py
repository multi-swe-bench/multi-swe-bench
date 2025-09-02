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
        return "python:3.10-slim"
    
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
ls -la .github/workflows
###ACTION_DELIMITER###
apt-get update && apt-get install -y just
###ACTION_DELIMITER###
curl -L https://github.com/casey/just/releases/latest/download/just-linux-x86_64 -o /usr/local/bin/just && chmod +x /usr/local/bin/just
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl -L https://github.com/casey/just/releases/latest/download/just-linux-x86_64 -o /usr/local/bin/just && chmod +x /usr/local/bin/just
###ACTION_DELIMITER###
curl -L https://github.com/casey/just/releases/latest/download/just-x86_64-unknown-linux-musl -o /usr/local/bin/just && chmod +x /usr/local/bin/just
###ACTION_DELIMITER###
curl -L https://github.com/casey/just/releases/download/v1.25.2/just-linux-x86_64 -o /usr/local/bin/just && chmod +x /usr/local/bin/just
###ACTION_DELIMITER###
curl -L https://github.com/casey/just/releases/download/v1.25.2/just-x86_64-unknown-linux-musl -o /usr/local/bin/just && chmod +x /usr/local/bin/just
###ACTION_DELIMITER###
apt-get update && apt-get install -y ca-certificates && curl -L https://github.com/casey/just/releases/download/v1.25.2/just-x86_64-unknown-linux-musl -o /usr/local/bin/just && chmod +x /usr/local/bin/just
###ACTION_DELIMITER###
curl -L https://github.com/casey/just/releases/download/v1.25.2/just-x86_64-unknown-linux-gnu -o /usr/local/bin/just && chmod +x /usr/local/bin/just
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget && wget https://github.com/casey/just/releases/download/v1.25.2/just-x86_64-unknown-linux-musl -O /usr/local/bin/just && chmod +x /usr/local/bin/just
###ACTION_DELIMITER###
wget https://github.com/casey/just/releases/download/v1.25.2/just-x86_64-unknown-linux-musl.tar.gz -O just.tar.gz && tar -xzf just.tar.gz && mv just-x86_64-unknown-linux-musl/just /usr/local/bin/just && chmod +x /usr/local/bin/just
###ACTION_DELIMITER###
pip install --upgrade pip 'poetry<1.4'
###ACTION_DELIMITER###
poetry install --with test
###ACTION_DELIMITER###
poetry run pytest -v --junitxml=junit.xml --cov=ibis --cov-report=xml:coverage.xml
###ACTION_DELIMITER###
poetry install --with test --extras "bigquery"
###ACTION_DELIMITER###
poetry run pytest -v --junitxml=junit.xml --cov=ibis --cov-report=xml:coverage.xml
###ACTION_DELIMITER###
poetry install --with test --extras "clickhouse"
###ACTION_DELIMITER###
poetry install --with test --extras "all"
###ACTION_DELIMITER###
apt-get update && apt-get install -y libpq-dev python3-dev
###ACTION_DELIMITER###
poetry install --with test --extras "all"
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
poetry install --with test --extras "all"
###ACTION_DELIMITER###
echo 'poetry run pytest -v --junitxml=junit.xml --cov=ibis --cov-report=xml:coverage.xml' > test_commands.sh
###ACTION_DELIMITER###
echo 'poetry run pytest -v -n auto --junitxml=junit.xml --cov=ibis --cov-report=xml:coverage.xml' > test_commands.sh
###ACTION_DELIMITER###
echo 'just check -v' > test_commands.sh
###ACTION_DELIMITER###
echo 'poetry run pytest -m core -v -n auto --junitxml=junit.xml --cov=ibis --cov-report=xml:coverage.xml' > test_commands.sh
###ACTION_DELIMITER###
echo 'just ci-check -m core -n auto' > test_commands.sh
###ACTION_DELIMITER###
echo 'just check -v -n auto' > test_commands.sh
###ACTION_DELIMITER###
echo 'just check -v -n auto' > test_commands.sh
###ACTION_DELIMITER###
echo 'poetry run pytest -m core -v -n auto --junitxml=junit.xml' > test_commands.sh
###ACTION_DELIMITER###
echo 'poetry run pytest -v -n auto --junitxml=junit.xml' > test_commands.sh
###ACTION_DELIMITER###
echo 'poetry run pytest -m core -v -n auto --junitxml=junit.xml' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
poetry run pytest -m core -v -n auto --junitxml=junit.xml

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
poetry run pytest -m core -v -n auto --junitxml=junit.xml

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
poetry run pytest -m core -v -n auto --junitxml=junit.xml

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
FROM python:3.10-slim

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
RUN git clone https://github.com/ibis-project/ibis.git /home/ibis

WORKDIR /home/ibis
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ibis-project", "ibis_6138_to_6137")
class IBIS_6138_TO_6137(Instance):
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
        import json
        # Use regex to find test cases and their statuses
        passed_pattern = re.compile(r'PASSED (ibis/.*?)(?=\s|$)')
        failed_pattern = re.compile(r'FAILED (ibis/.*?)(?=\s|$)')
        skipped_pattern = re.compile(r'SKIPPED (ibis/.*?)(?=\s|$)')
        passed_tests.update(passed_pattern.findall(log))
        failed_tests.update(failed_pattern.findall(log))
        skipped_tests.update(skipped_pattern.findall(log))
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
