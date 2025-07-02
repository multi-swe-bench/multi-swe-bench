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
                """ls -al
###ACTION_DELIMITER###
echo 'make test
pip uninstall -y ujson email-validator
make test' > /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
apt-get install -y make
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
apt-get install -y gcc
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
apt-get install -y python3.8-dev
###ACTION_DELIMITER###
apt-get install -y python3-dev build-essential
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
pip install -r tests/requirements.txt
###ACTION_DELIMITER###
pytest --version
###ACTION_DELIMITER###
which python3 && python3 --version && which pip && pip --version
###ACTION_DELIMITER###
pip list
###ACTION_DELIMITER###
pip install attrs==18.2.0 black==18.9b0 coverage==4.5.2 flake8==3.7.4 isort==4.3.4 pycodestyle==2.5.0 pyflakes==2.1.0 pytest==4.2.0 pytest-cov==2.6.1 pytest-isort==0.2.1 pytest-mock==1.10.0 pytest-sugar==0.9.2
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
pip show typeguard
###ACTION_DELIMITER###
pip install setuptools==44.0.0
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
make test
pip uninstall -y ujson email-validator
make test

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
make test
pip uninstall -y ujson email-validator
make test

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
make test
pip uninstall -y ujson email-validator
make test

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
RUN git checkout e77bc00d6e52a4ea13fb467c163ca67468c7d02c

RUN git checkout {pr.base.sha}"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pydantic", "pydantic_v0_20")
class PYDANTIC_V0_20(Instance):
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
        # 1. Parse FAILURES section for actual test function names and their files
        # Build a list of (filename, function_name) for failed tests, in order
        failures = []
        in_failures = False
        failure_func_re = re.compile(r'^_{5,}\s*(\w+(?:\[.*?\])?)\s*_{5,}$')
        failure_file_re = re.compile(r'^(tests/[^:]+):(\d+): Failed')
        current_fail = None
        for line in log.splitlines():
            if 'FAILURES' in line:
                in_failures = True
                continue
            if in_failures:
                m_func = failure_func_re.match(line)
                if m_func:
                    current_fail = {'func': m_func.group(1), 'file': None}
                m_file = failure_file_re.match(line)
                if m_file and current_fail:
                    current_fail['file'] = m_file.group(1)
                    failures.append((current_fail['file'], current_fail['func']))
                    current_fail = None
                if line.startswith('=') or line.startswith('-') or line.startswith('----------'):
                    in_failures = False
                    current_fail = None
        # 2. Parse per-file test result lines
        file_line_re = re.compile(r'^(tests/[^\s]+)\s+([.sF]+)')
        test_index = {}
        # Build a mapping of (filename, fail_index) -> real failed test name
        fail_map = {}
        fail_counts = {}
        for file, func in failures:
            if file not in fail_counts:
                fail_counts[file] = 0
            file_only = file.split(':')[0]  # Remove line number if present
            fail_map[(file_only, fail_counts[file_only] if file_only in fail_counts else 0)] = func
            fail_counts[file_only] = fail_counts.get(file_only, 0) + 1
        # Parse per-file lines and assign real names to failed tests
        for line in log.splitlines():
            m = file_line_re.match(line)
            if m:
                filename, results = m.groups()
                file_only = filename.split(':')[0]  # Remove line number if present
                if file_only not in test_index:
                    test_index[file_only] = 0
                fail_idx = 0
                for c in results:
                    test_name = f"{file_only}::test_{test_index[file_only]}"
                    if c == '.':
                        passed_tests.add(test_name)
                    elif c == 's':
                        skipped_tests.add(test_name)
                    elif c == 'F':
                        # Use real name if available
                        real_name = fail_map.get((file_only, fail_idx))
                        if real_name:
                            failed_tests.add(f"{file_only}::{real_name}")  # Use file and real function name
                        else:
                            failed_tests.add(test_name)
                        fail_idx += 1
                    test_index[file_only] += 1
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
