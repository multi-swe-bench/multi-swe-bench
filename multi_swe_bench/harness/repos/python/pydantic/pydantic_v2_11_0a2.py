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
                """ls -la
###ACTION_DELIMITER###
uv sync --frozen --group all --all-extras
###ACTION_DELIMITER###
pip install uv
###ACTION_DELIMITER###
uv sync --frozen --group all --all-extras
###ACTION_DELIMITER###
echo 'uv run coverage run -m pytest --durations=10' > /home/pydantic/test_commands.sh && chmod +x /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
uv run coverage run -m pytest --durations=10

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
uv run coverage run -m pytest --durations=10

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
uv run coverage run -m pytest --durations=10

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
RUN git clone https://github.com/pydantic/pydantic.git /home/pydantic

WORKDIR /home/pydantic
RUN git reset --hard
RUN git checkout 7ccad67149c3b97b7aa7d7c892a3e64db0d80e10

RUN git checkout {pr.base.sha}"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pydantic", "pydantic_v2_11_0a2")
class PYDANTIC_V2_11_0A2(Instance):
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
        # Strategy:
        # 1. Extract failed test names from the 'FAILURES' section and summary.
        # 2. Extract test names and their status from duration lines (e.g., 'call     tests/benchmarks/test_model_schema_generation.py::test_lots_of_models_with_lots_of_fields').
        # 3. Optionally, infer test status from per-file lines with symbols (., s, x, F) if test names can be reconstructed.
        # 4. Only clean test names should be extracted, without error messages or extra info.
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re
        import json
        # Extract failed test names from traceback and summary
        # Pattern: tests/<path>.py:<line> <test_function_name> - ...
        fail_pattern = re.compile(r'^(tests/\S+\.py):(\d+)\s+([\w\[\]\-]+)')
        for line in log.splitlines():
            m = fail_pattern.match(line)
            if m:
                # Compose test name as file::function
                test_name = f"{m.group(1)}::{m.group(3)}"
                failed_tests.add(test_name)
            # Extract test names from duration lines (slowest durations, etc.)
            # Example: '3.78s call     tests/benchmarks/test_model_schema_generation.py::test_lots_of_models_with_lots_of_fields'
            dur_pattern = re.compile(r'\d+\.\d+s\s+(call|setup|teardown)\s+(tests/\S+\.py::\S+)')
            m2 = dur_pattern.match(line)
            if m2:
                test_name = m2.group(2)
                # Only add to passed if not failed
                if test_name not in failed_tests:
                    passed_tests.add(test_name)
            # Extract skipped tests from per-file lines with symbols
            # Example: tests/test_abc.py .s [  3%]
            fileline_pattern = re.compile(r'^(tests/\S+\.py)\s+([.sxF]+)')
            m3 = fileline_pattern.match(line)
            if m3:
                testfile = m3.group(1)
                symbols = m3.group(2)
                # Try to reconstruct test names for skipped tests
                for idx, sym in enumerate(symbols):
                    if sym == 's':
                        # Name as testfile::SKIPPED_TEST_{idx+1}
                        skipped_tests.add(f"{testfile}::SKIPPED_TEST_{idx+1}")
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
