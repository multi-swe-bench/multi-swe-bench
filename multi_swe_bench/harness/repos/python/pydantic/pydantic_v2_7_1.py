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

    def dependency(self) -> Image | None:
        return "python:3.8-slim"
    
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
                """
###ACTION_DELIMITER###
ls -a
###ACTION_DELIMITER###
ls -a .github/workflows
###ACTION_DELIMITER###
python3 --version && python3.10 --version && python3.11 --version && python3.12 --version || true
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.10 python3.10-venv python3.10-distutils
###ACTION_DELIMITER###
apt-cache search python3.1
###ACTION_DELIMITER###
apt-get install -y python3.11 python3.11-venv python3.11-distutils
###ACTION_DELIMITER###
python3.11 -m ensurepip
###ACTION_DELIMITER###
apt-get install -y python3-pip
###ACTION_DELIMITER###
pip3.11 --version
###ACTION_DELIMITER###
pip3.11 install pdm
###ACTION_DELIMITER###
python3.11 -m venv .venv
###ACTION_DELIMITER###
.venv/bin/pip install pdm
###ACTION_DELIMITER###
.venv/bin/pdm install --group :all
###ACTION_DELIMITER###
.venv/bin/pdm lock --update-reuse
###ACTION_DELIMITER###
.venv/bin/pdm install --group :all
###ACTION_DELIMITER###
echo '.venv/bin/pdm run pytest --no-header -rA --tb=no -p no:cacheprovider' > /home/pydantic/test_commands.sh && chmod +x /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
.venv/bin/pip install pytest
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
.venv/bin/pip install pydantic-core==2.19.0
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
.venv/bin/pip install pytest-benchmark
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
.venv/bin/pytest tests/test_typing.py -v
###ACTION_DELIMITER###
.venv/bin/pip install annotated-types
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
.venv/bin/pytest tests/test_aliases.py -v
###ACTION_DELIMITER###
.venv/bin/pip install dirty-equals
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
.venv/bin/pytest tests/test_annotated.py -v
###ACTION_DELIMITER###
.venv/bin/pip install pytz
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
.venv/bin/pytest tests/test_docs.py -v
###ACTION_DELIMITER###
.venv/bin/pip install pytest-examples
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
.venv/bin/pytest tests/test_pickle.py -v
###ACTION_DELIMITER###
.venv/bin/pip install cloudpickle
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
.venv/bin/pip install email-validator
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
.venv/bin/pdm run pytest --no-header -rA --tb=no -p no:cacheprovider

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
.venv/bin/pdm run pytest --no-header -rA --tb=no -p no:cacheprovider

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
.venv/bin/pdm run pytest --no-header -rA --tb=no -p no:cacheprovider

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
FROM python:3.8-slim

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
RUN git clone https://github.com/pydantic/pydantic.git /home/pydantic

WORKDIR /home/pydantic
RUN git reset --hard
RUN git checkout 20b9176fa2ca18fd0b568bf3a119fa4b8e0bc08e

RUN git checkout {pr.base.sha}"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pydantic", "pydantic_v2_7_1")
class PYDANTIC_V2_7_1(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re
        import json
        # Improved regex patterns for test results (robust for parameterized names)
        result_pattern = re.compile(r"^(PASSED|FAILED|XFAIL|XPASS) +([^\s]+\.py::[^\s]+)", re.MULTILINE)
        skip_pattern = re.compile(r"^SKIPPED \[\d+\] ([^:]+\.py):(\d+)", re.MULTILINE)
        # Temporary sets
        passed_tests = set()
        failed_tests = set()
        xfail_tests = set()
        xpass_tests = set()
        # Parse result lines
        for match in result_pattern.finditer(log):
            status, testname = match.groups()
            testname = testname.strip()
            if status == 'PASSED':
                passed_tests.add(testname)
            elif status == 'FAILED':
                failed_tests.add(testname)
            elif status == 'XFAIL':
                xfail_tests.add(testname)
            elif status == 'XPASS':
                xpass_tests.add(testname)
        # Parse skipped tests (file:line)
        for file, line in skip_pattern.findall(log):
            skipped_tests.add(f"{file}:{line}")
        # Remove any overlap: a test cannot be both passed and failed
        failed_tests -= passed_tests
        # Optionally, treat xfail as failed (or keep separate)
        failed_tests |= xfail_tests
        # Optionally, treat xpass as passed (or keep separate)
        passed_tests |= xpass_tests
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
