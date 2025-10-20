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
                """ls .github/workflows
###ACTION_DELIMITER###
pip install --upgrade 'pip>=21.3.1'
###ACTION_DELIMITER###
make install-python-ci-dependencies
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make install-python-ci-dependencies
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
wget https://dl.google.com/go/go1.17.7.linux-amd64.tar.gz && tar -C /usr/local -xzf go1.17.7.linux-amd64.tar.gz && export PATH=$PATH:/usr/local/go/bin
###ACTION_DELIMITER###
export PATH=$PATH:/usr/local/go/bin && make install-python-ci-dependencies
###ACTION_DELIMITER###
rm -rf /usr/local/go && wget https://dl.google.com/go/go1.18.linux-amd64.tar.gz && tar -C /usr/local -xzf go1.18.linux-amd64.tar.gz && export PATH=$PATH:/usr/local/go/bin && make install-python-ci-dependencies
###ACTION_DELIMITER###
pip install pip-tools
###ACTION_DELIMITER###
export PATH=$PATH:/usr/local/go/bin && make install-python-ci-dependencies
###ACTION_DELIMITER###
ls sdk/python/requirements
###ACTION_DELIMITER###
cd sdk/python && python -m piptools sync requirements/py3.9-ci-requirements.txt
###ACTION_DELIMITER###
cd /home/feast && FEAST_USAGE=False pytest -n 8 --verbose sdk/python/tests
###ACTION_DELIMITER###
make compile-protos-python
###ACTION_DELIMITER###
make install-python
###ACTION_DELIMITER###
pip install --upgrade pip==23.3.1
###ACTION_DELIMITER###
make install-python
###ACTION_DELIMITER###
pip install pip-tools==6.13.0
###ACTION_DELIMITER###
make install-python
###ACTION_DELIMITER###
make install-python PYTHON=3.9
###ACTION_DELIMITER###
cd sdk/python && pip install -r requirements/py3.9-requirements.txt && python setup.py develop
###ACTION_DELIMITER###
FEAST_USAGE=False pytest -n 8 --verbose sdk/python/tests
###ACTION_DELIMITER###
echo 'FEAST_USAGE=False pytest -n 8 --verbose sdk/python/tests' > /home/feast/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
FEAST_USAGE=False pytest -n 8 --verbose sdk/python/tests

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
FEAST_USAGE=False pytest -n 8 --verbose sdk/python/tests

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
FEAST_USAGE=False pytest -n 8 --verbose sdk/python/tests

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
RUN git clone https://github.com/feast-dev/feast.git /home/feast

WORKDIR /home/feast
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("feast-dev", "feast_2556_to_2225")
class FEAST_2556_TO_2225(Instance):
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
        # Regex pattern to match test status and name
        # Captures status (PASSED, FAILED, SKIPPED, ERROR) and test name
        # Adjusted pattern to handle test names with spaces/hyphens (e.g., 'test_on_demand_features_type_inference')
        pattern = r'.*(PASSED|FAILED|SKIPPED|ERROR)\s+([\w/.-]+\.py(?:::[\w_-]+)?)'
        matches = re.findall(pattern, log)
        for status, test_name in matches:
            test_name = test_name.strip()
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ('FAILED', 'ERROR'):
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
