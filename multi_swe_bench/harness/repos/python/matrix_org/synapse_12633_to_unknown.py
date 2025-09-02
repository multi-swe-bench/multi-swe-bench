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

###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential python3-dev libffi-dev python3-pip python3-setuptools sqlite3 libssl-dev virtualenv libjpeg-dev libxslt1-dev
###ACTION_DELIMITER###
poetry install --extras "all test"
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH"
###ACTION_DELIMITER###
poetry install --extras "all test"
###ACTION_DELIMITER###
apt-get install -y libpq-dev
###ACTION_DELIMITER###
poetry install --extras "all test"
###ACTION_DELIMITER###
poetry run trial -v tests
###ACTION_DELIMITER###
poetry run trial --help
###ACTION_DELIMITER###
poetry run trial tests
###ACTION_DELIMITER###
poetry add setuptools
###ACTION_DELIMITER###
poetry add 'setuptools<60.0.0'
###ACTION_DELIMITER###
poetry run trial tests
###ACTION_DELIMITER###
poetry install --extras "url_preview"
###ACTION_DELIMITER###
echo 'poetry run trial tests' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
poetry run trial tests

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
poetry run trial tests

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
poetry run trial tests

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
RUN git clone https://github.com/matrix-org/synapse.git /home/synapse

WORKDIR /home/synapse
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("matrix-org", "synapse_12633_to_unknown")
class SYNAPSE_12633_TO_UNKNOWN(Instance):
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
        import json
        # Regex pattern to match test lines with status
        current_module = ''
        current_test_case = ''
        in_summary = False
        for line in log.split('\n'):
            # Remove line number prefix (e.g., [   2] )
            content = re.sub(r'^\[\s*\d+\]\s*', '', line)
            # Detect start of summary section
            if re.match(r'^-{50,}$', content) or re.match(r'^Ran \d+ tests', content):
                in_summary = True
            # Match module (e.g., tests.api.test_auth) - no leading spaces
            if re.match(r'^tests\.[\w.]+\.test_\w+$', content):
                current_module = content
                current_test_case = ''
            # Match test case (e.g., AuthTestCase, URLPreviewTests) - 2 leading spaces
            elif re.match(r'^  [^\s]+(TestCase|Tests)$', content):
                current_test_case = content.strip()
            # Match full test names (likely failed tests)
            elif re.match(r'^tests\.[\w.]+\.\w+\.\w+\s*$', content):
                failed_tests.add(content.strip())
            # Match test method (e.g., test_blocking_mau ... [OK], test_failure ... ERROR)
            method_match = re.match(r'^\s{4,}(.+?)\s+\.\.\.\s*\[?(\w+)\]?$', content)
            if method_match and current_module and current_test_case:
                    method_name = method_match.group(1).strip()
                    status = method_match.group(2).upper()
                    full_test_name = f'{current_module}.{current_test_case}.{method_name}'
                    if status == 'OK':
                        passed_tests.add(full_test_name)
                    elif status == 'SKIPPED':
                        skipped_tests.add(full_test_name)
                    elif status in ('FAILED', 'ERROR', 'FAIL', 'FAILURE'):
                        failed_tests.add(full_test_name)
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
