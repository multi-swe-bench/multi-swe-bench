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
        return "python:3.11-slim"
    
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
pip install pdm
###ACTION_DELIMITER###
pdm install --group :all
###ACTION_DELIMITER###
pdm lock --update-reuse
###ACTION_DELIMITER###
pdm install --group :all
###ACTION_DELIMITER###
pdm update --update-reuse --group :all
###ACTION_DELIMITER###
pdm install --group testing
###ACTION_DELIMITER###
echo 'pdm run coverage run -m pytest --durations=10' > /home/pydantic/test_commands.sh && chmod +x /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pdm run coverage run -m pytest --durations=10

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
pdm run coverage run -m pytest --durations=10

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
pdm run coverage run -m pytest --durations=10

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
FROM python:3.11-slim

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
RUN git checkout 6aab43e47e32f667319aaf63c6345a6525ba2e09

RUN git checkout {pr.base.sha}"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pydantic", "pydantic_v2_7_0")
class PYDANTIC_V2_7_0(Instance):
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
        passed_tests = set() # Tests that passed successfully
        failed_tests = set() # Tests that failed
        skipped_tests = set() # Tests that were skipped
        import re
        import json
        # Implementation: parse pytest log output
        # 1. Extract failed test names from error headers
        # Match lines like: _____________________________ test_func_name ______________________________
        # Require at least 10 underscores on both sides, and no brackets or spaces in the name
        # Only match lines with a single function name (letters, numbers, underscores, possibly brackets)
        # Only match lines with a single function name (letters, numbers, underscores, brackets, hyphens)
        failed_test_pattern = re.compile(r'^_{10,}\s*([\w\[\]\-]+)\s*_{10,}$', re.MULTILINE)
        for match in failed_test_pattern.finditer(log):
            name = match.group(1).strip()
            # Exclude lines with spaces, dots, or colons (not a function name)
            if name and all(c not in name for c in ' .:'):
                failed_tests.add(name)
        # 2. Parse compact output for passed/skipped tests
        # Example: tests/test_abc.py .s
        # Match lines that start with a file path and are immediately followed by result characters, ignoring trailing content
        # Match lines that start with a file path and are immediately followed by result characters, ignoring trailing content
        compact_line_pattern = re.compile(r'^(tests/[^:]+\.py)\s+([.sFx]+)\s*(\[\s*\d+%\])?\s*$', re.MULTILINE)
        for match in compact_line_pattern.finditer(log):
            file_path = match.group(1)
            results = match.group(2)
            # Extract only the contiguous sequence of result characters (., s, F, x) at the start
            m = re.match(r'^([.sFx]+)', results)
            if m:
                results = m.group(1)
            else:
                results = ''
            for idx, ch in enumerate(results):
                test_name = f"{file_path}::test_{idx+1}"
                if ch == '.':
                    passed_tests.add(test_name)
                elif ch == 's':
                    skipped_tests.add(test_name)
                # 'F' and 'x' are not added here; 'F' is handled by error headers, 'x' is xfail
        # Debug print for passed_tests
        print("DEBUG passed_tests sample:", list(passed_tests)[:10])
        # 3. Optionally, extract more precise test names from lines like:
        # tests/test_config.py:347 TestsBaseConfig.test_config_class_is_deprecated
        detailed_name_pattern = re.compile(r'^(tests/[^:]+\.py):(\d+)\s+([\w\[\].:-]+)', re.MULTILINE)
        for match in detailed_name_pattern.finditer(log):
            file_path = match.group(1)
            # line_no = match.group(2)  # Not used
            test_func = match.group(3)
            # If this test is in failed_tests, update its name to be more precise
            for failed in list(failed_tests):
                if failed in test_func or test_func in failed:
                    failed_tests.remove(failed)
                    failed_tests.add(f"{file_path}::{test_func}")
        # Remove any overlap (shouldn't happen, but just in case)
        passed_tests -= failed_tests
        skipped_tests -= failed_tests
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
