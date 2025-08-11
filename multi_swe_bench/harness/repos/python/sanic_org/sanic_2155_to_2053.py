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
pip install -e .
###ACTION_DELIMITER###
pip install sanic-testing coverage==5.3 pytest==5.2.1 pytest-cov pytest-sanic pytest-sugar pytest-benchmark chardet==3.* beautifulsoup4 gunicorn==20.0.4 uvicorn "websockets>=8.1,<9.0"
###ACTION_DELIMITER###
pip freeze | grep pytest
###ACTION_DELIMITER###
pytest tests --cov sanic -v
###ACTION_DELIMITER###
pip install pytest-benchmark==3.2.3
###ACTION_DELIMITER###
pytest tests --cov sanic -v
###ACTION_DELIMITER###
pip install sanic-testing==0.8.0
###ACTION_DELIMITER###
pytest tests --cov sanic -v
###ACTION_DELIMITER###
pip install sanic-testing==0.6.0
###ACTION_DELIMITER###
pip install sanic-testing==0.7.0 && pip install 'websockets>=8.1,<9.0'
###ACTION_DELIMITER###
pip install sanic-testing==0.5.0
###ACTION_DELIMITER###
pip install sanic-testing==0.4.0
###ACTION_DELIMITER###
pytest tests --cov sanic -v
###ACTION_DELIMITER###
echo 'SANIC_PORT=0 pytest tests --cov sanic -v' > /home/sanic/test_commands.sh
###ACTION_DELIMITER###
bash /home/sanic/test_commands.sh
###ACTION_DELIMITER###
echo -e 'lsof -ti:8000 | xargs kill -9 || true
SANIC_PORT=0 pytest tests --cov sanic -v' > /home/sanic/test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y lsof
###ACTION_DELIMITER###
bash /home/sanic/test_commands.sh
###ACTION_DELIMITER###
echo -e 'lsof -ti:8000 | xargs kill -9 || true
SANIC_PORT=8001 pytest tests --cov sanic -v' > /home/sanic/test_commands.sh
###ACTION_DELIMITER###
echo -e 'export SANIC_PORT=0
pytest tests --cov sanic -v' > /home/sanic/test_commands.sh
###ACTION_DELIMITER###
bash /home/sanic/test_commands.sh
###ACTION_DELIMITER###
echo 'env SANIC_PORT=0 pytest tests --cov sanic -v' > /home/sanic/test_commands.sh
###ACTION_DELIMITER###
bash /home/sanic/test_commands.sh
###ACTION_DELIMITER###
echo -e 'lsof -ti :8000 | xargs kill -9 || true
env SANIC_PORT=8001 pytest tests --cov sanic -v' > /home/sanic/test_commands.sh
###ACTION_DELIMITER###
echo -e 'lsof -ti :8000 | xargs kill -9 || true
sleep 2
env SANIC_PORT=8001 pytest tests --cov sanic -v' > /home/sanic/test_commands.sh
###ACTION_DELIMITER###
bash /home/sanic/test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y iproute2
###ACTION_DELIMITER###
echo -e 'ss -lntp | grep :8000 | awk "{print \$7}" | cut -d "/" -f 1 | xargs kill -9 || true
sleep 2
env SANIC_PORT=8001 pytest tests --cov sanic -v' > /home/sanic/test_commands.sh
###ACTION_DELIMITER###
echo -e 'ss -lntp | grep :8000 | awk "{print \$7}" | cut -d "/" -f 1 | xargs kill -9 || true
sleep 2
env SANIC_PORT=0 SANIC_NO_UVLOOP=1 pytest tests --cov sanic -v' > /home/sanic/test_commands.sh
###ACTION_DELIMITER###
bash /home/sanic/test_commands.sh
###ACTION_DELIMITER###
echo -e 'env SANIC_PORT=0 SANIC_REUSE_PORT=True pytest tests --cov sanic -v' > /home/sanic/test_commands.sh
###ACTION_DELIMITER###
echo 'pytest tests --cov sanic -v -k "not test_create_server_main and not test_create_server_main_convenience"' > /home/sanic/test_commands.sh
###ACTION_DELIMITER###
bash /home/sanic/test_commands.sh
###ACTION_DELIMITER###
echo 'env SANIC_PORT=0 SANIC_NO_UVLOOP=1 pytest tests --cov sanic -v' > /home/sanic/test_commands.sh
###ACTION_DELIMITER###
bash /home/sanic/test_commands.sh
###ACTION_DELIMITER###
echo 'env SANIC_PORT=0 SANIC_REUSE_PORT=True SANIC_NO_UVLOOP=1 pytest tests --cov sanic -v' > /home/sanic/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
env SANIC_PORT=0 SANIC_REUSE_PORT=True SANIC_NO_UVLOOP=1 pytest tests --cov sanic -v

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
env SANIC_PORT=0 SANIC_REUSE_PORT=True SANIC_NO_UVLOOP=1 pytest tests --cov sanic -v

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
env SANIC_PORT=0 SANIC_REUSE_PORT=True SANIC_NO_UVLOOP=1 pytest tests --cov sanic -v

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


@Instance.register("sanic-org", "sanic_2155_to_2053")
class SANIC_2155_TO_2053(Instance):
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
        # Regular expression to match test cases and their statuses
        pattern = re.compile(r'(?:\[\s*\d+\]\s+)?((?:tests/)?[\w/\.]+::[\w_\-\[\]]+)\s+(PASSED|FAILED|SKIPPED)(?:\s+\[\s*\d+%\s*\])?', re.IGNORECASE)
        matches = pattern.findall(log)
        for test_name, status in matches:
            if status.upper() == "PASSED":
                passed_tests.add(test_name)
            elif status.upper() == "FAILED":
                failed_tests.add(test_name)
            elif status.upper() == "SKIPPED":
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
