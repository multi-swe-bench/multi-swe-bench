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
apt-get update && apt-get install -y build-essential python3-dev libuv1-dev
###ACTION_DELIMITER###
apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa -y && apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.8 python3.8-dev python3.8-venv
###ACTION_DELIMITER###
python3.8 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
sed -i 's/requests-async==0.5.0/requests-async==0.2.2/' setup.py
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install pytest==5.2.1 multidict>=4.0,<5.0 gunicorn pytest-cov httpcore==0.3.0 beautifulsoup4 uvloop ujson pytest-sanic pytest-sugar pytest-benchmark
###ACTION_DELIMITER###
pip install pytest==5.2.1 'multidict>=4.0,<5.0' gunicorn pytest-cov httpcore==0.3.0 beautifulsoup4 uvloop ujson pytest-sanic pytest-sugar pytest-benchmark
###ACTION_DELIMITER###
pip install websockets==8.1
###ACTION_DELIMITER###
pip install pytest-sanic==1.7.0
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider tests' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest-benchmark==3.2.3
###ACTION_DELIMITER###
pip install --force-reinstall pytest==5.2.1
###ACTION_DELIMITER###
pytest
###ACTION_DELIMITER###
pip install httpx==0.13.3
###ACTION_DELIMITER###
pip install httpx==0.23.0
###ACTION_DELIMITER###
pip install httpx==0.24.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
grep -r 'ASGISession' venv/lib/python3.8/site-packages/requests_async/
###ACTION_DELIMITER###
pip install requests-async==0.6.0
###ACTION_DELIMITER###
pip install git+https://github.com/encode/requests-async.git
###ACTION_DELIMITER###
sed -i 's/requests-async==0.5.0/requests-async>=0.6.2/' setup.py
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
sed -i 's/requests-async==0.2.2/requests-async>=0.6.2/' setup.py
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install git+https://github.com/encode/requests-async.git && pip install -e .
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/ --no-header//' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest-asyncio==0.14.0
###ACTION_DELIMITER###
pip install pytest-asyncio==0.23.2
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/def protocol(transport, loop):/def protocol(transport):/' tests/test_asgi.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/^import uvicorn/a @pytest.fixture\ndef app():\n    return Sanic("test_app")' tests/test_asgi.py
###ACTION_DELIMITER###
pip install uvicorn==0.11.8
###ACTION_DELIMITER###
pip install pytest==5.2.1 pytest-asyncio==0.14.0
###ACTION_DELIMITER###
pip install pytest==5.2.1 pytest-asyncio==0.10.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/--tb=no//' test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v -rA  -p no:cacheprovider tests

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
pytest -v -rA  -p no:cacheprovider tests

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
pytest -v -rA  -p no:cacheprovider tests

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
RUN git clone https://github.com/sanic-org/sanic.git /home/sanic

WORKDIR /home/sanic
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("sanic-org", "sanic_1708_to_unknown")
class SANIC_1708_TO_UNKNOWN(Instance):
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
        # Pattern for test lines with status and progress
        test_pattern = re.compile(r"^(tests/.*?) (PASSED|FAILED|SKIPPED)\s+\[\s*\d+%\]", re.MULTILINE)
        # Pattern for failed tests listed at the end
        failed_pattern = re.compile(r"^FAILED (tests/.*?) -", re.MULTILINE)
        # Extract tests from main test lines
        for match in test_pattern.finditer(log):
            test_name = match.group(1)
            status = match.group(2)
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status == "FAILED":
                failed_tests.add(test_name)
            elif status == "SKIPPED":
                skipped_tests.add(test_name)
        # Extract failed tests from the end section
        for match in failed_pattern.finditer(log):
            test_name = match.group(1)
            failed_tests.add(test_name)
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
