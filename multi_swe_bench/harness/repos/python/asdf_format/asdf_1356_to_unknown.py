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
        return "python:3.9-slim-bullseye"
    
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
pip install -e ".[tests]"
###ACTION_DELIMITER###
echo 'pytest -v -rA' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/ignore::asdf.exceptions.AsdfDeprecationWarning:asdf.asdftypes/ignore::DeprecationWarning:asdf.asdftypes/' pyproject.toml
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/:asdf.exceptions.AsdfDeprecationWarning/:DeprecationWarning/' pyproject.toml
###ACTION_DELIMITER###
sed -i '/filterwarnings =/a \    "ignore::DeprecationWarning:jsonschema.exceptions",' pyproject.toml
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pytest -v -rA/pytest -v -rA -W ignore::DeprecationWarning:jsonschema.exceptions/' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/    "error",/a \    "ignore::DeprecationWarning:jsonschema.exceptions",' pyproject.toml
###ACTION_DELIMITER###
sed -i '1i export PYTHONWARNINGS="ignore::DeprecationWarning:jsonschema.exceptions"' test_commands.sh
###ACTION_DELIMITER###
sed -i '2i import warnings\nwarnings.filterwarnings("ignore", category=DeprecationWarning, module="jsonschema.exceptions")' asdf/conftest.py
###ACTION_DELIMITER###
pip install 'jsonschema<4.18.0' && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
export PYTHONWARNINGS="ignore::DeprecationWarning:jsonschema.exceptions"
pytest -v -rA -W ignore::DeprecationWarning:jsonschema.exceptions

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
export PYTHONWARNINGS="ignore::DeprecationWarning:jsonschema.exceptions"
pytest -v -rA -W ignore::DeprecationWarning:jsonschema.exceptions

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
export PYTHONWARNINGS="ignore::DeprecationWarning:jsonschema.exceptions"
pytest -v -rA -W ignore::DeprecationWarning:jsonschema.exceptions

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim-bullseye with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.9-slim-bullseye

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


@Instance.register("asdf-format", "asdf_1356_to_unknown")
class ASDF_1356_TO_UNKNOWN(Instance):
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
        # Remove ANSI color codes
        log_clean = re.sub(r'\x1b\[[0-9;]*m', '', log)
        # Split into lines
        lines = log_clean.split('\n')
        for line in lines:
            # Remove leading line number (e.g., [  11] )
            cleaned_line = re.sub(r'^\[\s*\d+\]\s*', '', line).strip()
            if not cleaned_line:
                continue
            # Check for PASSED tests
            if 'PASSED' in cleaned_line:
                test_name = cleaned_line.split('PASSED')[0].strip()
                if '::' in test_name:
                    passed_tests.add(test_name)
            # Check for FAILED tests
            elif 'FAILED' in cleaned_line:
                # Extract test name using regex to handle '-' in parameters
                match = re.search(r' (.*?::.*?) - ', cleaned_line)
                if match:
                    test_part = match.group(1).strip()
                    failed_tests.add(test_part)
                else:
                    # Fallback in case the pattern doesn't match
                    parts = cleaned_line.split('FAILED', 1)
                    if len(parts) >= 2:
                        after_failed = parts[1].strip()
                        test_part = after_failed.split()[0]
                        if '::' in test_part:
                            failed_tests.add(test_part)
            # Check for SKIPPED tests
            elif 'SKIPPED' in cleaned_line:
                # Handle both 'test SKIPPED' and 'SKIPPED test' cases
                parts = cleaned_line.split('SKIPPED', 1)
                test_part = parts[0].strip() if parts[0].strip() else parts[1].strip()
                # If there's a reason after '-', split it off
                test_part = test_part.split('-', 1)[0].strip()
                if '::' in test_part:
                    skipped_tests.add(test_part)
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
