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
                """ls
###ACTION_DELIMITER###
pip install -e .[test]
###ACTION_DELIMITER###
apt-get update && apt-get install -y gcc python3-dev
###ACTION_DELIMITER###
pip install -e .[test]
###ACTION_DELIMITER###
python setup.py test --pytest-args="-v"
###ACTION_DELIMITER###
pip install attrs==18.2.0
###ACTION_DELIMITER###
python setup.py test --pytest-args="-v"
###ACTION_DELIMITER###
pip install pytest-sanic
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip list | grep pytest-sanic
###ACTION_DELIMITER###
pip show pytest-sanic
###ACTION_DELIMITER###
ls /usr/local/lib/python3.9/site-packages | grep pytest_sanic
###ACTION_DELIMITER###
pip install --force-reinstall pytest-sanic
###ACTION_DELIMITER###
pip install pytest-sanic==1.2.0 websockets==6.0 --force-reinstall
###ACTION_DELIMITER###
pip install multidict==4.7.6 --force-reinstall
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip uninstall -y pytest-sanic pytest && pip install pytest-sanic==1.2.0 pytest==4.6.11
###ACTION_DELIMITER###
ls /usr/local/lib/python3.9/site-packages | grep pytest_sanic
###ACTION_DELIMITER###
pip install --force-reinstall --no-cache-dir pytest-sanic==1.2.0
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
pip install attrs==18.2.0 --force-reinstall
###ACTION_DELIMITER###
pip install pytest==4.1.0 attrs==18.2.0 pytest-sanic==1.2.0 --force-reinstall
###ACTION_DELIMITER###
pip install multidict==4.7.6 --force-reinstall
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install aiohttp<=3.2.1 && pip install --force-reinstall pytest-sanic==1.2.0
###ACTION_DELIMITER###
pip install 'aiohttp<=3.2.1' && pip install --force-reinstall pytest-sanic==1.2.0
###ACTION_DELIMITER###
pip install 'aiohttp<=3.2.1' multidict==4.7.6 pytest-sanic==0.1.0 pytest==4.1.0 attrs==18.2.0 --force-reinstall
###ACTION_DELIMITER###
pip install 'aiohttp<=3.2.1' multidict==4.7.6 pytest-sanic==1.0.0 pytest==4.1.0 attrs==18.2.0 --force-reinstall
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install setuptools==41.0.0 --force-reinstall
###ACTION_DELIMITER###
pytest -v -p no:typeguard
###ACTION_DELIMITER###
echo 'pytest -v -p no:typeguard' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v -p no:typeguard

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
pytest -v -p no:typeguard

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
pytest -v -p no:typeguard

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim with actual base image
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
RUN git clone https://github.com/sanic-org/sanic.git /home/sanic

WORKDIR /home/sanic
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("sanic-org", "sanic_1482_to_unknown")
class SANIC_1482_TO_UNKNOWN(Instance):
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
        passed_tests = set[str]() # Tests that passed successfully
        failed_tests = set[str]() # Tests that failed
        skipped_tests = set[str]() # Tests that were skipped
        import re
        # Regex to match test lines with status, handling both test-first and status-first formats
        pattern = re.compile(
            r'(\btests/[^:]+::[^ ]+)\s+(PASSED|FAILED|SKIPPED|ERROR)\b|'
            r'(PASSED|FAILED|SKIPPED|ERROR)\s+(\btests/[^:]+::[^ ]+)\b',
            re.MULTILINE
        )
        test_status = {}  # Track the latest status for each test
        for match in pattern.finditer(log):
            if match.group(1) and match.group(2):
                test_name = match.group(1)
                status = match.group(2)
            elif match.group(3) and match.group(4):
                test_name = match.group(4)
                status = match.group(3)
            else:
                continue  # Skip invalid matches
            # Update to the latest status
            test_status[test_name] = status
        # Populate the sets based on the latest status
        for test, status in test_status.items():
            if status == 'PASSED':
                passed_tests.add(test)
            elif status in ('FAILED', 'ERROR'):
                failed_tests.add(test)
            elif status == 'SKIPPED':
                skipped_tests.add(test)
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
