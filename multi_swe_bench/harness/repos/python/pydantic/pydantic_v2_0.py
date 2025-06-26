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
                """ls -la
###ACTION_DELIMITER###
ls -la tests
###ACTION_DELIMITER###
pdm --version || pip install pdm
###ACTION_DELIMITER###
pdm install --group :all
###ACTION_DELIMITER###
pdm lock --update-reuse && pdm install --group :all
###ACTION_DELIMITER###
echo 'pdm run coverage run -m pytest --durations=10' > /home/pydantic/test_commands.sh && chmod +x /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
pdm add --dev coverage
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
pdm add --dev toml
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
pdm add --dev 'coverage[toml]'
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
pdm add --dev pytest
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
pdm add --dev pydantic-core==2.0.1
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
pdm add --dev annotated-types
###ACTION_DELIMITER###
pdm add --dev dirty-equals
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
pdm add --dev pytest-examples
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
RUN git checkout 1943e9da182de1d9172b40b165d64e720da4f041

RUN git checkout {pr.base.sha}"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pydantic", "pydantic_v2_0")
class PYDANTIC_V2_0(Instance):
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
        # 1. Parse the summary section for failed, error, and skipped tests
        # Find the summary section
        summary_start = log.rfind('short test summary info')
        if summary_start != -1:
            summary = log[summary_start:]
            # Failed tests
            for m in re.finditer(r'^FAILED (.+?)(?: -|$)', summary, re.MULTILINE):
                failed_tests.add(m.group(1).strip())
            # Error tests
            for m in re.finditer(r'^ERROR (.+?)(?: -|$)', summary, re.MULTILINE):
                failed_tests.add(m.group(1).strip())
            # Skipped tests are not listed by name in summary, only counted
        # 2. Parse the main test output for passed/skipped tests
        # Each test file line: tests/test_abc.py ..s.x
        for m in re.finditer(r'^(tests/[^\s:]+\.py) ([.sx]+)', log, re.MULTILINE):
            testfile = m.group(1)
            results = m.group(2)
            # Find all test results in this line
            for idx, ch in enumerate(results):
                # We don't know the test function name, so we use file + index
                # But if the file has only one test, it's likely just the file name
                # We'll skip adding ambiguous names here
                pass
        # Instead, try to extract test function names from detailed error/failure reports
        # Example: tests/test_utils.py::test_smart_deepcopy_immutable_non_sequence[len]
        # These are already handled above for failed tests
        # 3. Parse for skipped tests in the main output
        # Look for lines like: sssssssssssssssssssssssssssssssssssssssssssssssssssss
        # But we can't get test names from these lines
        # Instead, look for 'SKIPPED' in detailed output (if any)
        for m in re.finditer(r'^SKIPPED (.+?)(?: -|$)', log, re.MULTILINE):
            skipped_tests.add(m.group(1).strip())
        # 4. Parse for passed tests: not listed by name in summary, but can be found in timing lines
        # Example: 0.24s call     tests/test_json_schema.py::test_dataclass
        for m in re.finditer(r'\d+\.\d+s \w+\s+(tests/[^\s:]+\.py::[\w\[\]\-]+)', log):
            testname = m.group(1).strip()
            if testname not in failed_tests:
                passed_tests.add(testname)
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
