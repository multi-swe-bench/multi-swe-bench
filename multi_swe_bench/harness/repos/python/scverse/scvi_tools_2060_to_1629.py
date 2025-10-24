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
pip install --upgrade pip
###ACTION_DELIMITER###
pip install -e .[dev]
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install --upgrade chex
###ACTION_DELIMITER###
pip install numpy==1.23.5
###ACTION_DELIMITER###
pip install --upgrade numba
###ACTION_DELIMITER###
pip install --upgrade tiledbsoma
###ACTION_DELIMITER###
pip install --upgrade cellxgene-census
###ACTION_DELIMITER###
pip install s3fs==2024.6.1 fsspec==2024.6.1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install --upgrade mudata
###ACTION_DELIMITER###
pip install anndata==0.9.2
###ACTION_DELIMITER###
pip install mudata==0.3.0
###ACTION_DELIMITER###
pip install anndata==0.10.8
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -e .[hub]
###ACTION_DELIMITER###
pip install --upgrade aiobotocore
###ACTION_DELIMITER###
pip install boto3==1.27.59
###ACTION_DELIMITER###
pip install boto3==1.40.18
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=short -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'pip install scvi-tools==0.9.0 torch==1.13.1 pyro-ppl==1.8.4
pytest -v --no-header -rA --tb=short --junitxml=test_results.xml -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=short --junitxml=test_results.xml -p no:cacheprovider' > test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v --no-header -rA --tb=short --junitxml=test_results.xml -p no:cacheprovider

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
pytest -v --no-header -rA --tb=short --junitxml=test_results.xml -p no:cacheprovider

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
pytest -v --no-header -rA --tb=short --junitxml=test_results.xml -p no:cacheprovider

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
RUN git clone https://github.com/scverse/scvi-tools.git /home/scvi-tools

WORKDIR /home/scvi-tools
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("scverse", "scvi_tools_2060_to_1629")
class SCVI_TOOLS_2060_TO_1629(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re

        # Regex pattern to identify test names (tests/...py::test_...)
        test_pattern = re.compile(r"tests/.*?\.py::(?:[^:]+::)*test_\w+")
        lines = log.split("\n")
        for line in lines:
            line = line.strip()
            # Determine the status from the line
            if "PASSED" in line:
                status = "PASSED"
            elif "FAILED" in line:
                status = "FAILED"
            elif "SKIPPED" in line:
                status = "SKIPPED"
            else:
                continue  # No relevant status in this line
            # Extract the test name using the regex pattern
            test_match = test_pattern.search(line)
            if test_match:
                test_name = test_match.group()
                # Add the test name to the appropriate set
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
