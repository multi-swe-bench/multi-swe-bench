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
        return "python:3.6-buster"
    
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
echo 'pytest --cov=pydantic' > /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest --cov=pydantic

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
pytest --cov=pydantic

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
pytest --cov=pydantic

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
FROM python:3.6-buster

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
RUN git checkout 89b37d84732e95c484c72277b51ed8b2cd734013

RUN git checkout {pr.base.sha}"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pydantic", "pydantic_v0_9")
class PYDANTIC_V0_9(Instance):
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
        # TODO: Implement the parse_log function
        # Extract failed test names from the FAILURES section
        # Look for lines like: ____________________________ test_name _____________________________
        failure_section = False
        for line in log.splitlines():
            if line.startswith('=') and 'FAILURES' in line:
                failure_section = True
                continue
            if failure_section:
                m = re.match(r'^_{5,}\s+(test_[^\s]+)\s+_{5,}$', line)
                if m:
                    failed_tests.add(m.group(1))
                # End of failures section if we hit a line of '=' without 'FAILURES'
                elif line.startswith('=') and 'FAILURES' not in line:
                    break
        # Extract counts of passed and skipped tests from the summary line
        summary_match = re.search(r"(\d+) failed, (\d+) passed, (\d+) skipped", log)
        if summary_match:
            failed_count = int(summary_match.group(1))
            passed_count = int(summary_match.group(2))
            skipped_count = int(summary_match.group(3))
            # Add placeholder names for passed and skipped tests
            for i in range(1, passed_count + 1):
                passed_tests.add(f"passed_test_{i}")
            for i in range(1, skipped_count + 1):
                skipped_tests.add(f"skipped_test_{i}")
        # Try to match all possible summary formats if the previous regex did not match
        if not summary_match:
            summary_match = re.search(r"(\d+) passed, (\d+) skipped", log)
            if summary_match:
                passed_count = int(summary_match.group(1))
                skipped_count = int(summary_match.group(2))
                failed_count = 0
            else:
                summary_match = re.search(r"(\d+) passed", log)
                if summary_match:
                    passed_count = int(summary_match.group(1))
                    skipped_count = 0
                    failed_count = 0
                else:
                    summary_match = re.search(r"(\d+) skipped", log)
                    if summary_match:
                        passed_count = 0
                        skipped_count = int(summary_match.group(1))
                        failed_count = 0
                    else:
                        passed_count = skipped_count = failed_count = 0
            for i in range(1, passed_count + 1):
                passed_tests.add(f"passed_test_{i}")
            for i in range(1, skipped_count + 1):
                skipped_tests.add(f"skipped_test_{i}")
        # For passed and skipped tests, names are not available in this log format
        # Implement the log parsing logic here
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
