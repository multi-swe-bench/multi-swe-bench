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
        return "ubuntu:22.04"
    
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
python3 --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.10 python3-pip
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
cat install.sh
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
cat Makefile
###ACTION_DELIMITER###
hatch --version
###ACTION_DELIMITER###
pip install hatch
###ACTION_DELIMITER###
hatch run test
###ACTION_DELIMITER###
grep 'with_user_agent_extra' /home/ucx/.venv/lib/python3.10/site-packages/databricks/sdk/core.py
###ACTION_DELIMITER###
pip install --upgrade databricks-sdk==0.29.0
###ACTION_DELIMITER###
hatch run test
###ACTION_DELIMITER###
pip install databricks-labs-blueprint==0.10.0
###ACTION_DELIMITER###
pip install databricks-labs-blueprint==0.10.1
###ACTION_DELIMITER###
pip install databricks-sdk==0.28.0
###ACTION_DELIMITER###
cat pyproject.toml
###ACTION_DELIMITER###
pip install databricks-labs-blueprint==0.9.3
###ACTION_DELIMITER###
hatch run test
###ACTION_DELIMITER###
pip install databricks-labs-blueprint==0.8.3
###ACTION_DELIMITER###
pip install databricks-labs-blueprint==0.6.0
###ACTION_DELIMITER###
pytest tests/
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
pytest tests/
###ACTION_DELIMITER###
echo 'pytest --verbose --no-header -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest --verbose --no-header -rA --tb=no -p no:cacheprovider tests/

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
pytest --verbose --no-header -rA --tb=no -p no:cacheprovider tests/

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
pytest --verbose --no-header -rA --tb=no -p no:cacheprovider tests/

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:22.04 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:22.04

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
RUN git clone https://github.com/databrickslabs/ucx.git /home/ucx

WORKDIR /home/ucx
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("databrickslabs", "ucx_1953_to_1510")
class UCX_1953_TO_1510(Instance):
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
        # TODO: Implement the parse_log function
        # Implement the log parsing logic here
        # Compile regex patterns to match test lines
        pattern1 = re.compile(r'(?P<test_name>tests/.*)\s+(?P<status>SKIPPED|PASSED|FAILED|ERROR|XFAIL|xfailed)\s+\[\s*\d+%\s*\]')
        pattern2 = re.compile(r'(?P<status>SKIPPED|PASSED|FAILED|ERROR|XFAIL|xfailed)\s+(?P<test_name>tests/.*)')
        # Iterate through each line in the log content
        for line in log.split('\n'):
            line = line.strip()
            match1 = pattern1.search(line)
            match2 = pattern2.search(line)
            if match1:
                test_name = match1.group('test_name')
                status = match1.group('status')
            elif match2:
                test_name = match2.group('test_name')
                status = match2.group('status')
            else:
                continue  # Skip non-test lines
            # Categorize the test based on its status
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
            elif status == 'ERROR':
                # Treat ERROR as a failure (adjust if necessary)
                failed_tests.add(test_name)
            elif status in ['XFAIL', 'xfailed']:
                # XFAIL indicates expected failure, consider as passed
                passed_tests.add(test_name)
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
