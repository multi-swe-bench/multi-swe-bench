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
                """ls
###ACTION_DELIMITER###
cat requirements.txt
###ACTION_DELIMITER###
cat setup.py
###ACTION_DELIMITER###
cat setup.cfg
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
echo 'pytest -v -rsxfE --durations=20' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy websockets highlevelgraph
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
pip install numpy websockets dask-highlevelgraph
###ACTION_DELIMITER###
pip install numpy websockets==9.1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.26.4
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -rsxfE --durations=20 --ignore=distributed/comm/tests/test_comms.py --ignore=distributed/comm/tests/test_ws.py --ignore=distributed/protocol/tests/test_collection_cuda.py --ignore=distributed/protocol/tests/test_highlevelgraph.py' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest-asyncio
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install cryptography
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v -rsxfE --durations=20 --ignore=distributed/comm/tests/test_comms.py --ignore=distributed/comm/tests/test_ws.py --ignore=distributed/protocol/tests/test_collection_cuda.py --ignore=distributed/protocol/tests/test_highlevelgraph.py

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
pytest -v -rsxfE --durations=20 --ignore=distributed/comm/tests/test_comms.py --ignore=distributed/comm/tests/test_ws.py --ignore=distributed/protocol/tests/test_collection_cuda.py --ignore=distributed/protocol/tests/test_highlevelgraph.py

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
pytest -v -rsxfE --durations=20 --ignore=distributed/comm/tests/test_comms.py --ignore=distributed/comm/tests/test_ws.py --ignore=distributed/protocol/tests/test_collection_cuda.py --ignore=distributed/protocol/tests/test_highlevelgraph.py

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

# Choose an appropriate base image based on the project's requirements - replace python:3.10-slim with actual base image
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
RUN git clone https://github.com/dask/distributed.git /home/distributed

WORKDIR /home/distributed
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("dask", "distributed_5033_to_4799")
class DISTRIBUTED_5033_TO_4799(Instance):
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
        import json
        # Regex pattern to match test cases with their statuses
        test_pattern = re.compile(r'([\w\/]+\.py::[\w_-]+)(?: <- .+?)? (PASSED|FAILED|SKIPPED|XFAIL|XPASSED)')
        # Regex pattern to match FAILED test cases in summary lines
        failed_summary_pattern = re.compile(r'FAILED ([\w\/]+\.py::[\w_-]+)')
        # Extract all test matches
        test_matches = test_pattern.findall(log)
        failed_summary_matches = failed_summary_pattern.findall(log)
        # Process test matches
        for test_name, status in test_matches:
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
            elif status == 'XFAIL':
                # XFAIL is an expected failure, consider it as failed for this context
                failed_tests.add(test_name)
            elif status == 'XPASSED':
                # XPASSED is an unexpected pass, consider it as passed
                passed_tests.add(test_name)
        # Process failed summary matches
        for test_name in failed_summary_matches:
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
