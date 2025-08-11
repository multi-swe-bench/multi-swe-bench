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
                """pip install -e ".[tests]"
###ACTION_DELIMITER###
grep -A 10 'filterwarnings' pyproject.toml
###ACTION_DELIMITER###
sed -i "/ignore:numpy.ndarray size changed:RuntimeWarning/a \    'ignore::DeprecationWarning:jsonschema.exceptions'" pyproject.toml
###ACTION_DELIMITER###
grep -A 10 'filterwarnings' pyproject.toml
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
PYTHONWARNINGS="ignore::DeprecationWarning:jsonschema.exceptions" pytest -v
###ACTION_DELIMITER###
sed -i "s/'ignore::asdf.exceptions.AsdfDeprecationWarning:asdf.asdftypes'/'ignore::asdf.exceptions.AsdfDeprecationWarning'" pyproject.toml
###ACTION_DELIMITER###
sed -i "s/'ignore::asdf.exceptions.AsdfDeprecationWarning:asdf.asdftypes'/'ignore::asdf.exceptions.AsdfDeprecationWarning'/" pyproject.toml
###ACTION_DELIMITER###
grep -A 10 'filterwarnings' pyproject.toml
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###

###ACTION_DELIMITER###
PYTHONWARNINGS="ignore::asdf.exceptions.AsdfDeprecationWarning:ignore::DeprecationWarning:jsonschema.exceptions" pytest -v
###ACTION_DELIMITER###
sed -i '/error/d' pyproject.toml
###ACTION_DELIMITER###
grep -A 10 'filterwarnings' pyproject.toml
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install jsonschema==4.17.3
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
echo 'pytest -v' > /home/asdf/test_commands.sh
###ACTION_DELIMITER###
cat /home/asdf/test_commands.sh"""
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
RUN git clone https://github.com/asdf-format/asdf.git /home/asdf

WORKDIR /home/asdf
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("asdf-format", "asdf_1257_to_unknown")
class ASDF_1257_TO_UNKNOWN(Instance):
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
        import json
        # TODO: Implement the parse_log function
        # Implement the log parsing logic here
        # Strip ANSI escape codes
        log_clean = re.sub(r'\x1b\[.*?m', '', log)
        lines = log_clean.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Check for PASSED tests
            if 'PASSED' in line:
                parts = line.split(' PASSED ', 1)
                if len(parts) >= 2:
                    test_name = parts[0].strip()
                    passed_tests.add(test_name)
            # Check for FAILED tests
            elif 'FAILED' in line:
                parts = line.split(' - ', 1)
                if len(parts) >= 2:
                    test_part = parts[0].strip()
                    if test_part.startswith('FAILED '):
                        test_name = test_part[len('FAILED '):].strip()
                        failed_tests.add(test_name)
            # Check for SKIPPED tests
            elif 'SKIPPED' in line:
                # Handle cases where SKIPPED is at the start with a hyphen
                parts = line.split(' - ', 1)
                if len(parts) >= 2:
                    test_part = parts[0].strip()
                    if test_part.startswith('SKIPPED '):
                        test_name = test_part[len('SKIPPED '):].strip()
                        skipped_tests.add(test_name)
                # Handle cases where SKIPPED is at the end
                else:
                    parts = line.split(' SKIPPED ', 1)
                    if len(parts) >= 2:
                        test_name = parts[0].strip()
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
