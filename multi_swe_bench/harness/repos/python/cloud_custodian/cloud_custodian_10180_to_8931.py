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
cat Makefile
###ACTION_DELIMITER###
python3 -m venv .venv
###ACTION_DELIMITER###
source .venv/bin/activate
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
pip install poetry
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
ls tools
###ACTION_DELIMITER###
cd tools/c7n_gcp && poetry install --all-extras && cd ../../
###ACTION_DELIMITER###
cd tools/c7n_awscc && poetry install --all-extras && cd ../../
###ACTION_DELIMITER###
pip install --upgrade build
###ACTION_DELIMITER###
cat build.py
###ACTION_DELIMITER###
mv build.py awscc_build.py
###ACTION_DELIMITER###
poetry install --all-extras
###ACTION_DELIMITER###
sed -i 's/build = "build.py"/build = "awscc_build.py"/' pyproject.toml
###ACTION_DELIMITER###
poetry install --all-extras
###ACTION_DELIMITER###
cat pyproject.toml
###ACTION_DELIMITER###
sed -i 's/script = "build.py"/script = "awscc_build.py"/' pyproject.toml
###ACTION_DELIMITER###
cat pyproject.toml
###ACTION_DELIMITER###
poetry install --all-extras
###ACTION_DELIMITER###
cd ../../tools/c7n_tencentcloud && poetry install --all-extras && cd ../../
###ACTION_DELIMITER###
cd tools/c7n_azure && poetry install --all-extras && cd ../../
###ACTION_DELIMITER###
cd tools/c7n_oci && poetry install --all-extras && cd ../../
###ACTION_DELIMITER###
cd tools/c7n_kube && poetry install --all-extras && cd ../../
###ACTION_DELIMITER###
echo 'poetry run pytest -v -n auto tests tools' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
poetry add python-hcl2
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
poetry add azure-functions
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
echo -e '. ./test.env
poetry run pytest -v -n auto tests tools' > test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
. ./test.env
poetry run pytest -v -n auto tests tools

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
. ./test.env
poetry run pytest -v -n auto tests tools

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
. ./test.env
poetry run pytest -v -n auto tests tools

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
RUN git clone https://github.com/cloud-custodian/cloud-custodian.git /home/cloud-custodian

WORKDIR /home/cloud-custodian
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("cloud-custodian", "cloud_custodian_10180_to_8931")
class CLOUD_CUSTODIAN_10180_TO_8931(Instance):
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
        # Regular expression patterns to match test names with their statuses
        passed_pattern = r'PASSED ([\w\-/]+/test_.*?\.py::.*?)(?:\s|$)'
        failed_pattern = r'FAILED ([\w\-/]+/test_.*?\.py::.*?)(?:\s|$)'
        skipped_pattern = r'SKIPPED.*?([\w\-/]+/test_.*?\.py::.*?)(?:\s|$)'
        # Extract passed tests
        passed_tests.update(re.findall(passed_pattern, log))
        # Extract failed tests
        failed_tests.update(re.findall(failed_pattern, log))
        # Extract skipped tests
        skipped_tests.update(re.findall(skipped_pattern, log))
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
