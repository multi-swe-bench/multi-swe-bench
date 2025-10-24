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
        repo_name = self.pr.repo
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
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
ls elasticdl
###ACTION_DELIMITER###
pip install -r elasticdl/requirements.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y golang
###ACTION_DELIMITER###
pip install -r elasticdl/requirements.txt
###ACTION_DELIMITER###
pip install -v -r elasticdl/requirements.txt
###ACTION_DELIMITER###
go version
###ACTION_DELIMITER###
go env
###ACTION_DELIMITER###
go get -d github.com/elasticdl/pyrecordio
###ACTION_DELIMITER###
pip download pyrecordio --no-deps
###ACTION_DELIMITER###
tar -xzf pyrecordio-0.0.6.tar.gz
###ACTION_DELIMITER###
ls -la pyrecordio-0.0.6
###ACTION_DELIMITER###
cd pyrecordio-0.0.6
###ACTION_DELIMITER###
go mod init pyrecordio
###ACTION_DELIMITER###
go mod tidy
###ACTION_DELIMITER###
pip install .
###ACTION_DELIMITER###
cd /home/elasticdl
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
ln -s elasticdl/requirements.txt requirements.txt
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
echo 'make -f elasticdl/Makefile && K8S_TESTS=False pytest -v elasticdl/python/tests' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install tensorflow==2.0.0
###ACTION_DELIMITER###
pip install tensorflow==2.5.0
###ACTION_DELIMITER###
pip uninstall -y grpcio-tools && pip install grpcio-tools==1.34.1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install exceptiongroup==1.1.3
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###

###ACTION_DELIMITER###

###ACTION_DELIMITER###
""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
make -f elasticdl/Makefile && K8S_TESTS=False pytest -v elasticdl/python/tests

""".replace("[[REPO_NAME]]", repo_name),
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
make -f elasticdl/Makefile && K8S_TESTS=False pytest -v elasticdl/python/tests

""".replace("[[REPO_NAME]]", repo_name),
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
make -f elasticdl/Makefile && K8S_TESTS=False pytest -v elasticdl/python/tests

""".replace("[[REPO_NAME]]", repo_name),
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
RUN git clone https://github.com/sql-machine-learning/elasticdl.git /home/elasticdl

WORKDIR /home/elasticdl
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("sql-machine-learning", "elasticdl_856_to_809")
class ELASTICDL_856_TO_809(Instance):
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

        return "bash /home/run.sh"

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

        # Use regex to find all test cases and their statuses
        pattern = re.compile(
            r"^\s*(.*?)\s+(PASSED|FAILED|SKIPPED)\s+\[\s*\d+%\s*\]\s*$",
            re.MULTILINE | re.IGNORECASE,
        )
        matches = pattern.findall(log)
        for match in matches:
            test_name = match[0].strip() if match[0] else match[3].strip()
            status = match[1].strip().upper() if match[1] else match[2].strip().upper()
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status == "FAILED":
                failed_tests.add(test_name)
            elif status == "SKIPPED":
                skipped_tests.add(test_name)
        parsed_results = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
        }

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
