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

###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
echo 'pytest -v' > test_commands.sh
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest-cov
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
pip install pytest-timeout
###ACTION_DELIMITER###
pip install pytest-flaky
###ACTION_DELIMITER###
sed -i '/avoid_ci/a \    "flaky: marks tests as flaky (may pass or fail randomly)",' pyproject.toml
###ACTION_DELIMITER###
pip install 'dask[dataframe]' requests
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest-xdist
###ACTION_DELIMITER###
sed -i 's/pytest -v/pytest -v -n auto/' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pytest -v -n auto/pytest -v -n auto -m "not slow"/' test_commands.sh
###ACTION_DELIMITER###
sed -i 's/-m "not slow"/-m "not slow and not avoid_ci and not extra_packages"/' test_commands.sh
###ACTION_DELIMITER###
sed -i 's/-n auto -m "not slow and not avoid_ci and not extra_packages"/-n 2 -m "not slow and not avoid_ci and not extra_packages and not gpu and not ipython"/' test_commands.sh
###ACTION_DELIMITER###
sed -i 's/-m "not slow and not avoid_ci and not extra_packages and not gpu and not ipython"/-m "ci1 and not slow and not avoid_ci and not extra_packages and not gpu and not ipython"/' test_commands.sh
###ACTION_DELIMITER###
sed -i 's/-m "ci1 and not slow and not avoid_ci and not extra_packages and not gpu and not ipython"/-m "not slow and not avoid_ci and not extra_packages and not gpu and not ipython"/' test_commands.sh
###ACTION_DELIMITER###
sed -i 's/-m "not slow and not avoid_ci and not extra_packages and not gpu and not ipython"/-m "ci1 and not slow and not avoid_ci and not extra_packages and not gpu and not ipython"/' test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pytest -v -n 2 -m "ci1 and not slow and not avoid_ci and not extra_packages and not gpu and not ipython"/pytest -v -n 2 -m "not slow and not avoid_ci and not extra_packages and not gpu and not ipython" distributed/tests/' test_commands.sh
###ACTION_DELIMITER###
sed -i 's|pytest -v -n 2 -m "ci1 and not slow and not avoid_ci and not extra_packages and not gpu and not ipython"|pytest -v -n 2 -m "not slow and not avoid_ci and not extra_packages and not gpu and not ipython" distributed/tests|' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|pytest -v -n 2 -m "not slow and not avoid_ci and not extra_packages and not gpu and not ipython" distributed/tests|pytest -v -n 1 -m "ci1 and not slow and not avoid_ci and not extra_packages and not gpu and not ipython" distributed/tests|' test_commands.sh
###ACTION_DELIMITER###
sed -i 's|ci1 and not slow and not avoid_ci and not extra_packages and not gpu and not ipython|ci1 and not slow and not avoid_ci and not extra_packages and not gpu and not ipython and not leaking and not workerstate|' test_commands.sh
###ACTION_DELIMITER###
pytest --collect-only -m "ci1 and not slow and not avoid_ci and not extra_packages and not gpu and not ipython and not leaking and not workerstate" distributed/tests
###ACTION_DELIMITER###
sed -i 's/timeout = 300/timeout = 120/' pyproject.toml
###ACTION_DELIMITER###
sed -i 's|ci1 and not slow and not avoid_ci and not extra_packages and not gpu and not ipython and not leaking and not workerstate|ci1 and not slow and not avoid_ci and not extra_packages and not gpu and not ipython and not leaking and not workerstate and not flaky|' test_commands.sh
###ACTION_DELIMITER###
sed -i 's|pytest -v -n 1 -m "ci1 and not slow and not avoid_ci and not extra_packages and not gpu and not ipython and not leaking and not workerstate and not flaky" distributed/tests|pytest -v distributed/tests/test_client.py distributed/tests/test_worker.py|' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v distributed/tests/test_client.py distributed/tests/test_worker.py

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
pytest -v distributed/tests/test_client.py distributed/tests/test_worker.py

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
pytest -v distributed/tests/test_client.py distributed/tests/test_worker.py

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
RUN git clone https://github.com/dask/distributed.git /home/distributed

WORKDIR /home/distributed
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("dask", "distributed_8261_to_7933")
class DISTRIBUTED_8261_TO_7933(Instance):
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
        # Remove ANSI escape codes and parse test names/statuses
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        # Combined pattern to match test name and status in either order
        test_status_pattern = re.compile(r'((distributed/tests/.*?\.py::test_\w+))\s+(PASSED|FAILED|SKIPPED|XFAILED|XPASSED)|(PASSED|FAILED|SKIPPED|XFAILED|XPASSED)\s+((distributed/tests/.*?\.py::test_\w+))')
        # Track the latest status for each test to avoid duplicates
        test_status = {}
        for line in log.splitlines():
            stripped_line = ansi_escape.sub('', line)
            match = test_status_pattern.search(stripped_line)
            if match:
                # Extract test name and status from either pattern group
                test_name = match.group(1) if match.group(1) else match.group(5)
                status = match.group(3) if match.group(3) else match.group(4)
                test_status[test_name] = status  # Overwrite with latest status
        # Populate sets based on the latest status
        for test_name, status in test_status.items():
            if status in ('PASSED', 'XPASSED'):
                passed_tests.add(test_name)
            elif status in ('FAILED', 'XFAILED'):
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
