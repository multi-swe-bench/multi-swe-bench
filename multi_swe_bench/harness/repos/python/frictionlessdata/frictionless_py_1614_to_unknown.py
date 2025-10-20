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
                """ls
###ACTION_DELIMITER###
pip install hatch
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3-pip
###ACTION_DELIMITER###
pip3 install hatch
###ACTION_DELIMITER###
echo 'hatch run test' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libpq-dev
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/"ruff frictionless tests"/"ruff check frictionless tests"/' pyproject.toml
###ACTION_DELIMITER###
grep 'ruff' pyproject.toml
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
hatch run format
###ACTION_DELIMITER###
sed -i 's/"ruff frictionless tests --fix"/"ruff fix frictionless tests --fix"/' pyproject.toml
###ACTION_DELIMITER###
sed -i 's/"ruff frictionless tests --fix"/"ruff check frictionless tests --fix"/' pyproject.toml
###ACTION_DELIMITER###
sed -i 's/"ruff check frictionless tests --fix"/"ruff fix frictionless tests"/' pyproject.toml
###ACTION_DELIMITER###
hatch run format
###ACTION_DELIMITER###
sed -i 's/"ruff fix frictionless tests --fix"/"ruff check frictionless tests --fix"/' pyproject.toml
###ACTION_DELIMITER###
sed -i 's/"ruff fix frictionless tests --fix"/"ruff check frictionless tests --fix"/' pyproject.toml
###ACTION_DELIMITER###
sed -i 's/"ruff frictionless tests --fix"/"ruff check frictionless tests --fix"/' pyproject.toml
###ACTION_DELIMITER###
sed -i 's/"ruff frictionless tests --fix"/"ruff check frictionless tests --fix"/' pyproject.toml
###ACTION_DELIMITER###
hatch run format
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/exclude = \["frictionless\/vendors"\]/exclude = \["frictionless\/vendors", "tests\/schemes\/aws\/loaders\/test_s3.py"\]/' pyproject.toml
###ACTION_DELIMITER###
hatch run lint
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/"pytest"/"pytest<8.0.0"/' pyproject.toml
###ACTION_DELIMITER###
hatch env prune && hatch env create
###ACTION_DELIMITER###
sed -i 's/"pytest<8.0.0"/"pytest==7.0.0"/' pyproject.toml
###ACTION_DELIMITER###
hatch env prune && hatch env create
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from moto import mock_s3/from moto.s3 import mock_s3/' tests/schemes/aws/loaders/test_s3.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from moto.s3 import mock_s3/from moto import mock_s3/' tests/schemes/aws/loaders/test_s3.py
###ACTION_DELIMITER###
sed -i 's/"moto"/"moto==4.0.0"/' pyproject.toml
###ACTION_DELIMITER###
sed -i 's/"moto==4.0.0"/"moto==3.0.0"/' pyproject.toml
###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i 's/from moto import mock_s3/from moto import mock_aws/' tests/schemes/aws/loaders/test_s3.py
###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i 's/from moto import mock_s3/from moto import mock_aws/' tests/schemes/aws/loaders/test_s3.py
###ACTION_DELIMITER###
sed -i 's/@mock_s3/@mock_aws/' tests/schemes/aws/loaders/test_s3.py
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
hatch run test

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
hatch run test

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
hatch run test

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
RUN git clone https://github.com/frictionlessdata/frictionless-py.git /home/frictionless-py

WORKDIR /home/frictionless-py
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("frictionlessdata", "frictionless_py_1614_to_unknown")
class FRICTIONLESS_PY_1614_TO_UNKNOWN(Instance):
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
        # Extract test cases using regex patterns
        # Passed tests
        passed_pattern = re.compile(r'PASSED (tests/.*)')
        passed_tests.update(passed_pattern.findall(log))
        # Failed tests
        failed_pattern = re.compile(r'FAILED (tests/.*)')
        failed_tests.update(failed_pattern.findall(log))
        # Skipped tests
        skipped_pattern = re.compile(r'SKIPPED \[\d+\] (tests/[^:]+:\d+)')
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
