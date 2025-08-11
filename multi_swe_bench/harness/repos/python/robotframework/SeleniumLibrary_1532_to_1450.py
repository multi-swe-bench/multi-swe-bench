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
        return "python:3.9-slim"
    
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
ls atest
###ACTION_DELIMITER###
cat requirements.txt
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
python atest/run.py
###ACTION_DELIMITER###
pip install robotstatuschecker
###ACTION_DELIMITER###
python atest/run.py
###ACTION_DELIMITER###
pip install requests
###ACTION_DELIMITER###
python atest/run.py
###ACTION_DELIMITER###
apt-get install -y firefox
###ACTION_DELIMITER###
apt-get install -y firefox-esr
###ACTION_DELIMITER###
python atest/run.py firefox
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
python atest/run.py firefox
###ACTION_DELIMITER###
pip install approvaltests mockito
###ACTION_DELIMITER###
python atest/run.py firefox
###ACTION_DELIMITER###
pip install selenium==3.141.0
###ACTION_DELIMITER###
python atest/run.py firefox
###ACTION_DELIMITER###
echo 'python atest/run.py firefox' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python atest/run.py firefox

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
python atest/run.py firefox

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
python atest/run.py firefox

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.9-slim

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
RUN git clone https://github.com/robotframework/SeleniumLibrary.git /home/SeleniumLibrary

WORKDIR /home/SeleniumLibrary
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("robotframework", "SeleniumLibrary_1532_to_1450")
class SELENIUMLIBRARY_1532_TO_1450(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        # TODO: Implement the parse_log function
        # Implement the log parsing logic here
        # Parse result strings to extract test files and generate test names
        file_results_pattern = r'^(utest/.*?\.py) (.*?)\s+\['
        file_results = re.findall(file_results_pattern, log, re.MULTILINE)
        all_tests = []
        test_status = {}
        # Generate test names and map statuses from result strings
        for file_path, result_str in file_results:
            num_tests = len(result_str)
            # Generate test names (e.g., file_path::test_1, file_path::test_2)
            for i in range(num_tests):
                test_name = f'{file_path}::test_{i+1}'
                all_tests.append(test_name)
                # Map result character to status
                result = result_str[i]
                if result == 'F':
                    test_status[test_name] = 'failed'
                elif result == 's':
                    test_status[test_name] = 'skipped'
                else:  # '.' or other passing indicators
                    test_status[test_name] = 'passed'
        all_tests_set = set(all_tests)
        # Extract explicit failed tests (to overwrite generated names with actual names)
        explicit_failed = re.findall(r'FAILED (utest/.*?)(?:\s|$)', log)
        for test in explicit_failed:
            if test not in all_tests_set:
                all_tests.append(test)
                all_tests_set.add(test)
            test_status[test] = 'failed'
        # Extract explicit skipped tests
        explicit_skipped = re.findall(r'SKIPPED (utest/.*?)(?:\s|$)', log)
        for test in explicit_skipped:
            if test not in all_tests_set:
                all_tests.append(test)
                all_tests_set.add(test)
            test_status[test] = 'skipped'
        # Populate test sets from test_status
        for test, status in test_status.items():
            if status == 'failed':
                failed_tests.add(test)
            elif status == 'skipped':
                skipped_tests.add(test)
            else:
                passed_tests.add(test)
        # Validate with summary (adjust counts if needed)
        summary_match = re.search(r'=+ (\d+) failed, (\d+) passed, (\d+) skipped,?.*', log)
        if summary_match:
            exp_failed, exp_passed, exp_skipped = map(int, summary_match.groups())
            # Adjust failed tests
            if len(failed_tests) < exp_failed:
                missing = exp_failed - len(failed_tests)
                failed_tests.update(set(all_tests) - failed_tests - skipped_tests - passed_tests)
            elif len(failed_tests) > exp_failed:
                failed_tests = set(list(failed_tests)[:exp_failed])
            # Adjust skipped tests
            if len(skipped_tests) < exp_skipped:
                missing = exp_skipped - len(skipped_tests)
                skipped_tests.update(set(all_tests) - failed_tests - skipped_tests - passed_tests)
            elif len(skipped_tests) > exp_skipped:
                skipped_tests = set(list(skipped_tests)[:exp_skipped])
            # Recalculate passed tests to match summary
            passed_tests = all_tests_set - failed_tests - skipped_tests
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
