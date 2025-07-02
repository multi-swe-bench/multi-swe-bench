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
        return "python:3.10-bullseye"
    
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
python --version
###ACTION_DELIMITER###
which python3.8 || which python3.9
###ACTION_DELIMITER###
python3.9 -m pip --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.9-distutils && curl -sS https://bootstrap.pypa.io/get-pip.py | python3.9
###ACTION_DELIMITER###
python3.9 -m pip install -U setuptools pip && python3.9 -m pip install -U -r requirements.txt && SKIP_CYTHON=1 python3.9 -m pip install -e .
###ACTION_DELIMITER###
echo 'python3.9 -m pytest --cov=pydantic --disable-warnings
python3.9 tests/try_assert.py' > /home/pydantic/test_commands.sh && chmod +x /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
python3.9 -m pytest --cov=pydantic --disable-warnings -rA
###ACTION_DELIMITER###
python3.9 -m pytest --cov=pydantic --disable-warnings -p no:warnings
###ACTION_DELIMITER###
echo 'python3.9 -m pytest --cov=pydantic --disable-warnings -p no:warnings
python3.9 tests/try_assert.py' > /home/pydantic/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python3.9 -m pytest --cov=pydantic --disable-warnings -p no:warnings
python3.9 tests/try_assert.py

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
python3.9 -m pytest --cov=pydantic --disable-warnings -p no:warnings
python3.9 tests/try_assert.py

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
python3.9 -m pytest --cov=pydantic --disable-warnings -p no:warnings
python3.9 tests/try_assert.py

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
FROM python:3.10-bullseye

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
RUN git checkout 3cd8b1ee2d5aac76528dbe627f40fe1c27bf59f6

RUN git checkout {pr.base.sha}"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pydantic", "pydantic_v1_5")
class PYDANTIC_V1_5(Instance):
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

        # Improved parser for pytest logs
        import re
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        # 1. Parse progress lines: file, status string (handle multiline status)
        file_status = []  # List of (filename, status_string)
        lines = log.splitlines()
        current_file = None
        current_status = ''
        for line in lines:
            if line.startswith('tests/') and '[' in line:
                # Save previous file's status
                if current_file is not None:
                    file_status.append((current_file, current_status))
                current_file = line.split()[0]
                # Find the part before the [xx%]
                if '[' in line:
                    status_part = line[:line.rfind('[')].split()[-1]
                    current_status = status_part
                else:
                    current_status = ''
            elif re.match(r'^[.FEs]+\s*$', line):
                if current_file is not None:
                    current_status += line.strip()
            else:
                # If we hit a blank or unrelated line, just continue
                continue
        # Save last file's status
        if current_file is not None:
            file_status.append((current_file, current_status))
        # 2. Parse failed test names from separator lines
        fail_sep_re = re.compile(r'^_{5,}\s+([\w\[\]\-.,: =]+)\s+_{5,}$', re.MULTILINE)
        failed_names = [m.group(1).strip() for m in fail_sep_re.finditer(log)]
        failed_names_set = set(failed_names)
        # 3. Try to map test names to status for each file
        #    We don't have the full list of test names, so we can only assign failed names to F's,
        #    and infer passed/skipped by position (best effort)
        #    This is a limitation of the log format.
        #    For now, we will:
        #    - Assign failed_names to failed_tests
        #    - For each file, count the number of ., F, s and add placeholders for passed/skipped
        for name in failed_names:
            failed_tests.add(name)
        # 4. Count passed/skipped/failed per file and add placeholders for passed/skipped
        for filename, status_string in file_status:
            idx = 0
            for c in status_string:
                if c == '.':
                    passed_tests.add(f"{filename}::test_passed_{idx}")
                elif c in 'F':
                    # Already handled by failed_names
                    pass
                elif c in 'sS':
                    skipped_tests.add(f"{filename}::test_skipped_{idx}")
                idx += 1
        # Debug: print total number of status characters
        total_status_chars = sum(len(status) for _, status in file_status)
        print(f"DEBUG: total status chars: {total_status_chars}")
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
