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
                """ls -l
###ACTION_DELIMITER###
ls tests
###ACTION_DELIMITER###
ls tests/core
###ACTION_DELIMITER###
echo 'poetry run pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
poetry install -E dev
###ACTION_DELIMITER###
pip install poetry
###ACTION_DELIMITER###
poetry install -E dev
###ACTION_DELIMITER###
poetry lock
###ACTION_DELIMITER###
sed -i '35s/version = ">=2.0.8"/version = ">=2.1.12"/' pyproject.toml
###ACTION_DELIMITER###
poetry lock
###ACTION_DELIMITER###
poetry install -E dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y llvm-10 llvm-10-dev && ln -s /usr/bin/llvm-config-10 /usr/bin/llvm-config
###ACTION_DELIMITER###
apt-cache search llvm
###ACTION_DELIMITER###
apt-get install -y llvm-13 llvm-13-dev && ln -s /usr/bin/llvm-config-13 /usr/bin/llvm-config
###ACTION_DELIMITER###
poetry install -E dev
###ACTION_DELIMITER###
sed -i '49s/numba = ">=0.41.0"/numba = ">=0.56.0"/' pyproject.toml && poetry lock
###ACTION_DELIMITER###
poetry install -E dev
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'VENV=$(poetry env info --path)
$VENV/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'VENV=$(poetry env info --path)
source $VENV/bin/activate
pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
echo 'poetry run pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
poetry run pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/

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
poetry run pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/

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
poetry run pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/

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


@Instance.register("scverse", "scvi_tools_1009_to_705")
class SCVI_TOOLS_1009_TO_705(Instance):
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
        import json

        # Extract PASSED tests
        passed_pattern1 = r".*PASSED\s+(tests/[\w/\.]+\.py::[\w:]+)"
        passed_pattern2 = r".*(tests/[\w/\.]+\.py::[\w:]+)\s+PASSED"
        passed1 = re.findall(passed_pattern1, log)
        passed2 = re.findall(passed_pattern2, log)
        passed_tests.update(passed1 + passed2)
        # Extract FAILED tests
        failed_pattern = r".*FAILED\s+(tests/[\w/\.]+\.py::[\w:]+)"
        failed_tests.update(re.findall(failed_pattern, log))
        # Extract SKIPPED tests
        skipped_pattern = r".*SKIPPED\s+\[\d+\]\s+(tests/[\w/\.]+\.py:\d+)"
        skipped_tests.update(re.findall(skipped_pattern, log))
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
