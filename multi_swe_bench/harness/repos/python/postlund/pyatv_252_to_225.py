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
        return "python:3.11-slim"
    
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
./scripts/setup_dev_env.sh
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
sed -i 's/PYTHON="python3.8 python3.7 python3.6 python3.5"/PYTHON="python3.11 python3.8 python3.7 python3.6 python3.5"/' scripts/setup_dev_env.sh
###ACTION_DELIMITER###
./scripts/setup_dev_env.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y virtualenv
###ACTION_DELIMITER###
./scripts/setup_dev_env.sh
###ACTION_DELIMITER###
sed -i 's/python setup.py develop/pip install -e ./' scripts/setup_dev_env.sh
###ACTION_DELIMITER###
./scripts/setup_dev_env.sh
###ACTION_DELIMITER###
sed -i 's/typed-ast==1.4.0/typed-ast==1.5.4/' requirements_test.txt
###ACTION_DELIMITER###
./scripts/setup_dev_env.sh
###ACTION_DELIMITER###
sed -i 's/mypy==0.730/mypy==0.990/' requirements_test.txt
###ACTION_DELIMITER###
./scripts/setup_dev_env.sh
###ACTION_DELIMITER###
sed -i 's/pytest==5.1.2/pytest==7.0.0/' requirements_test.txt
###ACTION_DELIMITER###
./scripts/setup_dev_env.sh
###ACTION_DELIMITER###
sed -i 's/pip install tox/pip install tox==3.24.5/' scripts/setup_dev_env.sh
###ACTION_DELIMITER###
./scripts/setup_dev_env.sh
###ACTION_DELIMITER###
sed -i 's/pytest-aiohttp==0.3.0/pytest-aiohttp==1.0.5/' requirements_test.txt
###ACTION_DELIMITER###
sed -i 's/pytest-cov==2.7.1/pytest-cov==4.0.0/' requirements_test.txt && sed -i 's/pytest-timeout==1.3.3/pytest-timeout==2.1.0/' requirements_test.txt
###ACTION_DELIMITER###
./scripts/setup_dev_env.sh
###ACTION_DELIMITER###
sed -i 's/coveralls==1.8.2/coveralls==3.3.1/' requirements_test.txt
###ACTION_DELIMITER###
./scripts/setup_dev_env.sh
###ACTION_DELIMITER###
sed -i 's/pytest==7.0.0/pytest==7.4.0/' requirements_test.txt && sed -i 's/pytest-aiohttp==0.3.0/pytest-aiohttp==1.0.5/' requirements_test.txt && sed -i 's/pytest-cov==2.7.1/pytest-cov==4.0.0/' requirements_test.txt && sed -i 's/pytest-timeout==1.3.3/pytest-timeout==2.1.0/' requirements_test.txt
###ACTION_DELIMITER###
sed -i 's/python setup.py test/pytest/' scripts/setup_dev_env.sh
###ACTION_DELIMITER###
./scripts/setup_dev_env.sh
###ACTION_DELIMITER###
echo 'import asyncio
import sys
if sys.version_info >= (3, 10):
    asyncio.coroutine = lambda f: f' > tests/conftest.py
###ACTION_DELIMITER###
pytest
###ACTION_DELIMITER###
source bin/activate && pytest
###ACTION_DELIMITER###
sed -i 's/asynctest==0.13.0/asynctest==0.14.0/' requirements_test.txt
###ACTION_DELIMITER###
echo 'from asyncio import coroutines
if not hasattr(coroutines, "CoroWrapper"):
    class CoroWrapper:
        pass
    coroutines.CoroWrapper = CoroWrapper' >> tests/conftest.py
###ACTION_DELIMITER###
source bin/activate && pip install -r requirements_test.txt && pytest
###ACTION_DELIMITER###
sed -i 's/asynctest==0.14.0/asynctest==0.13.0/' requirements_test.txt && echo 'import asyncio
from asyncio import coroutines
if not hasattr(asyncio, "coroutine"):
    asyncio.coroutine = lambda f: f
if not hasattr(coroutines, "CoroWrapper"):
    class CoroWrapper:
        def __init__(self, coro, ctx):
            self.coro = coro
            self.ctx = ctx
        def __await__(self):
            return (yield from self.coro)
    coroutines.CoroWrapper = CoroWrapper' > tests/conftest.py
###ACTION_DELIMITER###
source bin/activate && pip install -r requirements_test.txt && pytest
###ACTION_DELIMITER###
sed -i 's/def fake_asyncio_sleep(self):/def fake_asyncio_sleep(self, seconds):/' tests/airplay/test_airplay.py
###ACTION_DELIMITER###
echo 'pytest -v' > /home/pyatv/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v

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
pytest -v

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
pytest -v

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
FROM python:3.11-slim

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
RUN git clone https://github.com/postlund/pyatv.git /home/pyatv

WORKDIR /home/pyatv
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("postlund", "pyatv_252_to_225")
class PYATV_252_TO_225(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        # Parse passed tests
        passed_matches = re.findall(r'^(tests/.*?) PASSED', log, re.MULTILINE)
        passed_tests = set(passed_matches)
        # Parse failed tests
        failed_matches = re.findall(r'^FAILED (tests/.*?)(?: - .*)?$', log, re.MULTILINE)
        failed_tests = set(failed_matches)
        # Parse skipped tests
        skipped_matches = re.findall(r'^\s*(tests/.*?)\s+SKIPPED', log, re.MULTILINE)
        skipped_tests = set(skipped_matches)
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
