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
        return "python:3.12-slim"
    
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
                """ls -al
###ACTION_DELIMITER###
pdm --version
###ACTION_DELIMITER###
pip install pdm
###ACTION_DELIMITER###
pdm install --group :all
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
FROM python:3.12-slim

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
RUN git checkout a25e0286de98ff6f011cdbea264952eba5a86dc3

RUN git checkout {pr.base.sha}"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pydantic", "pydantic_v2_10_0b1")
class PYDANTIC_V2_10_0B1(Instance):
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
        # Extract failed test names from the 'FAILURES' section and lines like 'tests/xxx.py:NNN test_func_name'
        failure_section = False
        last_failed_func = None
        for line in log.splitlines():
            # Detect start of failures section
            if re.match(r'=+ FAILURES =+', line):
                failure_section = True
                continue
            # Detect end of failures section
            if failure_section and line.strip() == '':
                failure_section = False
            # Capture function name from header line
            if failure_section:
                m_func = re.match(r'^_{5,}\s*(\w+)\s*_{5,}$', line)
                if m_func:
                    last_failed_func = m_func.group(1)
            # Catch summary lines like 'tests/xxx.py:NNN: Failed'
            m2 = re.match(r'^(tests/\S+):(\d+): Failed', line)
            if m2 and last_failed_func:
                failed_tests.add(f"{m2.group(1)}::{last_failed_func}")
                last_failed_func = None
            # Extract passed and skipped test names from summary lines like 'tests/xxx.py ...s..'
        test_line_re = re.compile(r'^(tests/\S+\.py) ([.sx]+)')
        for line in log.splitlines():
            m = test_line_re.match(line)
            if m:
                test_file = m.group(1)
                symbols = m.group(2)
                for idx, symbol in enumerate(symbols):
                    test_name = f"{test_file}::test_{idx+1}"
                    if symbol == '.':
                        passed_tests.add(test_name)
                    elif symbol == 's':
                        skipped_tests.add(test_name)
                    elif symbol == 'x':
                        # Could be expected failure or similar, not counted as passed/failed/skipped
                        pass
                    elif symbol == 'F':
                        # Already handled in failures section
                        pass
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
