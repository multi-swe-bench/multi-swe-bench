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
        return "python:3.6-slim"
    
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
                """ls -F
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install -q -e examples/tutorial[test]
###ACTION_DELIMITER###
pip install -q -e examples/javascript[test]
###ACTION_DELIMITER###
pip install -q "pytest>=3" coverage greenlet blinker python-dotenv
###ACTION_DELIMITER###
coverage run -p -m pytest tests examples
###ACTION_DELIMITER###
pip install -q "Werkzeug==0.14" "Jinja2==2.10" "itsdangerous==0.24" "Click==5.1"
###ACTION_DELIMITER###
coverage run -p -m pytest tests examples
###ACTION_DELIMITER###
pip install "pytest<4"
###ACTION_DELIMITER###
coverage run -p -m pytest tests examples
###ACTION_DELIMITER###
echo "coverage run -p -m pytest tests examples" > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
coverage run -p -m pytest tests examples

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
coverage run -p -m pytest tests examples

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
coverage run -p -m pytest tests examples

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
FROM python:3.6-slim

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
RUN git clone https://github.com/pallets/flask.git /home/flask

WORKDIR /home/flask
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pallets", "flask_2765_to_1593")
class FLASK_2765_TO_1593(Instance):
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
        # Regex to find lines with test results
        test_line_regex = re.compile(r"^(tests/.*|examples/.*) ([\.sF]+)")
        for line in log.splitlines():
            match = test_line_regex.match(line)
            if match:
                test_file = match.group(1).split(" ")[0]
                results = match.group(2)
                # Assuming each character in the results string represents a single test
                # and the test name is the file name. 
                # A more sophisticated approach would be needed if individual test names are required.
                if 'F' in results:
                    failed_tests.add(test_file)
                elif 's' in results:
                    skipped_tests.add(test_file)
                else:
                    passed_tests.add(test_file)
        # Fallback to summary line if no test lines were found
        if not any([passed_tests, failed_tests, skipped_tests]):
            summary_line_regex = re.compile(r"=============== ((\d+) failed, )?((\d+) passed, )?((\d+) skipped) in .* ===============")
            summary_match = summary_line_regex.search(log)
            if summary_match:
                # This part is tricky as we don't have test names from the summary line.
                # We can't populate the sets with meaningful data here.
                # This implementation will return empty sets if only the summary line is present.
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
