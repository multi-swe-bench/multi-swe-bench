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
                """git checkout dev-requirements.txt
###ACTION_DELIMITER###
sed -i 's/collections\.Iterable/collections.abc.Iterable/g' src/prefect/utilities/collections.py
###ACTION_DELIMITER###
apt-get update && apt-get install -y graphviz build-essential
###ACTION_DELIMITER###
pip install -r dev-requirements.txt
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
echo 'pytest -v tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pytest >=5.0, <5.3.2/pytest>=6.2.5/' dev-requirements.txt
###ACTION_DELIMITER###
pip install -r dev-requirements.txt
###ACTION_DELIMITER###
sed -i 's/^black$/black<22.3.0/' dev-requirements.txt
###ACTION_DELIMITER###
pip install -r dev-requirements.txt
###ACTION_DELIMITER###
sed -i 's/black<22.3.0/black<22.0.0/' dev-requirements.txt
###ACTION_DELIMITER###
pip install -r dev-requirements.txt
###ACTION_DELIMITER###
pip install --pre -r dev-requirements.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pytest >=5.0, <5.3.2/pytest>=6.2.5/' dev-requirements.txt
###ACTION_DELIMITER###
pip install -r dev-requirements.txt
###ACTION_DELIMITER###
cat dev-requirements.txt
###ACTION_DELIMITER###
sed -i 's/pytest >= 5.0, < 5.3.2/pytest>=6.2.5/' dev-requirements.txt
###ACTION_DELIMITER###
cat dev-requirements.txt
###ACTION_DELIMITER###
pip install -r dev-requirements.txt
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v tests/

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
pytest -v tests/

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
pytest -v tests/

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
RUN git clone https://github.com/PrefectHQ/prefect.git /home/prefect

WORKDIR /home/prefect
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("PrefectHQ", "prefect_1786_to_1673")
class PREFECT_1786_TO_1673(Instance):
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
        passed_tests = set[str]() # Tests that passed successfully
        failed_tests = set[str]() # Tests that failed
        skipped_tests = set[str]() # Tests that were skipped
        import re
        import json  # Not used, but kept as per skeleton
        # Pattern for PASSED/FAILED tests
        test_pattern = re.compile(r'^(tests/.*?)\s+(PASSED|FAILED)\s+\[\s*\d+%\]\s*$')
        # Pattern for SKIPPED tests
        skipped_pattern = re.compile(r'^SKIPPED\s+\[\d+\]\s+(tests/.*?):.*')
        # Pattern for XFAIL tests (added to failed_tests)
        xpass_pattern = re.compile(r'^XPASS\s+(tests/.*?)\s+-\s+.*')
        xfail_pattern = re.compile(r'^XFAIL\s+(tests/.*?)\s+-\s+.*')
        for line in log.split('\n'):
            # Check for PASSED/FAILED tests
            match = test_pattern.match(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
                continue
            # Check for XPASS tests
            match = xpass_pattern.match(line)
            if match:
                test_name = match.group(1)
                passed_tests.add(test_name)
                continue
            # Check for SKIPPED tests
            match = skipped_pattern.match(line)
            if match:
                test_name = match.group(1)
                skipped_tests.add(test_name)
                continue
            # Check for XFAIL tests
            match = xfail_pattern.match(line)
            if match:
                test_name = match.group(1)
                failed_tests.add(test_name)
                continue
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
