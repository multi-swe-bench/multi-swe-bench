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
        return "python:3.7"
    
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
                """ls
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
pytest --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
apt-get install -y golang
###ACTION_DELIMITER###
apt-get install -y ruby
###ACTION_DELIMITER###
apt-get install -y rustc
###ACTION_DELIMITER###
pytest --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
git config --global user.email "you@example.com" && git config --global user.name "Your Name"
###ACTION_DELIMITER###
pytest --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
gem install bundler
###ACTION_DELIMITER###

###ACTION_DELIMITER###
echo "pytest --no-header -rA --tb=no -p no:cacheprovider" > /home/pre-commit/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest --no-header -rA --tb=no -p no:cacheprovider

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
pytest --no-header -rA --tb=no -p no:cacheprovider

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
pytest --no-header -rA --tb=no -p no:cacheprovider

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
FROM python:3.7

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
RUN git clone https://github.com/pre-commit/pre-commit.git /home/pre-commit

WORKDIR /home/pre-commit
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pre-commit", "pre-commit_v1_13_0")
class PRE_COMMIT_V1_13_0(Instance):
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
    # Implement the log parsing logic here
        # This will parse verbose logs like fix-patch-run.log and test-patch-run.log
        verbose_re = re.compile(r"^(tests/.*?::\S+)\s+(PASSED|FAILED|SKIPPED)", re.MULTILINE)
        for match in verbose_re.finditer(log):
            test_name, status = match.groups()
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
        # This will parse the summary for failed and errored tests from any log file
        summary_re = re.compile(r"^=+\s+short test summary info\s+=+((?:.|\n)*?)^=+.+=$", re.MULTILINE)
        summary_match = summary_re.search(log)
        if summary_match:
            summary_content = summary_match.group(1)
            failed_re = re.compile(r"^(?:FAILED|ERROR) (.*?)(?: - .*)?$", re.MULTILINE)
            for match in failed_re.finditer(summary_content):
                failed_tests.add(match.group(1).strip())
        # This will find non-verbose passed tests.
        test_re = re.compile(r'^(tests/.*\.py) (?:\.+|s+|F+|E+)+\s+\[\s+\d+%\]', re.MULTILINE)
        for test_file_match in test_re.finditer(log):
            # extract the dots and the test file name
            test_file = test_file_match.group(1)
            # we need to get the test names from the test file.
            # we can't do that from the log file, so we will just add the file name
            # to the passed tests.
            passed_tests.add(test_file)
        # Final cleanup. If a test is in failed_tests, it should not be in passed_tests or skipped_tests.
        passed_tests.difference_update(failed_tests)
        skipped_tests.difference_update(failed_tests)
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
