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
                """apt-get update
###ACTION_DELIMITER###
ls
###ACTION_DELIMITER###
cat requirements.txt
###ACTION_DELIMITER###
cat setup.py
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
echo 'pytest --no-header -rA --tb=no -p no:cacheprovider -v' > /home/PyBaMM/test_commands.sh
###ACTION_DELIMITER###
cat /home/PyBaMM/test_commands.sh
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
apt-get install -y python3.9
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye main' >> /etc/apt/sources.list
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.9 -t bullseye
###ACTION_DELIMITER###
pip3.9 install -e .
###ACTION_DELIMITER###
apt-get install -y python3.9-pip -t bullseye
###ACTION_DELIMITER###
apt-get install -y python3-pip -t bullseye
###ACTION_DELIMITER###
pip3 install -e .
###ACTION_DELIMITER###
python3.9 -m pip install -e .
###ACTION_DELIMITER###
echo 'python3.9 -m pytest --no-header -rA --tb=no -p no:cacheprovider -v' > /home/PyBaMM/test_commands.sh
###ACTION_DELIMITER###
bash /home/PyBaMM/test_commands.sh
###ACTION_DELIMITER###
python3.9 -m pip install pytest
###ACTION_DELIMITER###
bash /home/PyBaMM/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python3.9 -m pytest --no-header -rA --tb=no -p no:cacheprovider -v

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
python3.9 -m pytest --no-header -rA --tb=no -p no:cacheprovider -v

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
python3.9 -m pytest --no-header -rA --tb=no -p no:cacheprovider -v

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

# Choose an appropriate base image based on the project's requirements - replace python:3.10-slim with actual base image
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
RUN git clone https://github.com/pybamm-team/PyBaMM.git /home/PyBaMM

WORKDIR /home/PyBaMM
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pybamm-team", "PyBaMM_2672_to_2385")
class PYBAMM_2672_TO_2385(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        # Implement the log parsing logic here
        lines = log.split('\n')
        # Patterns for PASSED tests
        passed_patterns = [
            re.compile(r'^(tests/.*?) PASSED \[\s*\d+%\]'),  # Format 1: test ... PASSED [ X%]
            re.compile(r'^PASSED (tests/.*)$')  # Format 2: PASSED test ...
        ]
        # Patterns for SKIPPED tests
        skipped_patterns = [
            re.compile(r'^\[\s*\d+\s*\]\s+SKIPPED\s+\[\d+\]\s+(tests/.*?\.py)\:\d+\:.*'),  # Format 1: [line] SKIPPED [1] test...: ...
            re.compile(r'^\[\s*\d+\s*\]\s+(tests/.*?)\s+SKIPPED\s+\[\d+%\]')  # Format 2: test ... SKIPPED [ X%]
        ]
        # Patterns for FAILED tests (assuming similar formats)
        failed_patterns = [
            re.compile(r'^(tests/.*?) FAILED \[\s*\d+%\]'),  # Format 1: test ... FAILED [ X%]
            re.compile(r'^FAILED (tests/.*)$')  # Format 2: FAILED test ...
        ]
        for line in lines:
            line = line.strip()
            # Check for PASSED tests
            for pattern in passed_patterns:
                match = pattern.match(line)
                if match:
                    test_name = match.group(1).strip()
                    passed_tests.add(test_name)
                    break  # Move to next line after match
            else:
                # Check for SKIPPED tests
                for pattern in skipped_patterns:
                    match = pattern.match(line)
                    if match:
                        test_name = match.group(1).strip()
                        skipped_tests.add(test_name)
                        break
                else:
                    # Check for FAILED tests
                    for pattern in failed_patterns:
                        match = pattern.match(line)
                        if match:
                            test_name = match.group(1).strip()
                            failed_tests.add(test_name)
                            break
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
