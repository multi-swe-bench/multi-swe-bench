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
        repo_name= self.pr.repo
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
                """python3.7 --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.7
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl
###ACTION_DELIMITER###
git clone https://github.com/pyenv/pyenv.git ~/.pyenv && export PYENV_ROOT="$HOME/.pyenv" && export PATH="$PYENV_ROOT/bin:$PATH" && eval "$(pyenv init -)" && pyenv install 3.7.17 && pyenv global 3.7.17
###ACTION_DELIMITER###
pipenv --python 3.7
###ACTION_DELIMITER###
pip install pipenv
###ACTION_DELIMITER###
pipenv --python 3.7
###ACTION_DELIMITER###
pipenv install --dev
###ACTION_DELIMITER###
pipenv run pip install setuptools==58.0.0
###ACTION_DELIMITER###
pipenv install --dev
###ACTION_DELIMITER###
pipenv run tox --version
###ACTION_DELIMITER###
echo 'pipenv run tox -e py37 -v' > /home/agents-aea/test_commands.sh
###ACTION_DELIMITER###
bash /home/agents-aea/test_commands.sh
###ACTION_DELIMITER###
pipenv lock --clear
###ACTION_DELIMITER###
pipenv install --dev
###ACTION_DELIMITER###
bash /home/agents-aea/test_commands.sh
###ACTION_DELIMITER###
rm -f Pipfile.lock
###ACTION_DELIMITER###
echo 'pipenv run pytest --doctest-modules aea tests/ --cov-report=html --cov-report=term --cov=aea -v' > /home/agents-aea/test_commands.sh
###ACTION_DELIMITER###
bash /home/agents-aea/test_commands.sh
###ACTION_DELIMITER###
pipenv run pip install protobuf==3.20.3
###ACTION_DELIMITER###
bash /home/agents-aea/test_commands.sh
###ACTION_DELIMITER###
echo 'pipenv run pytest --doctest-modules aea tests/ --cov-report=html --cov-report=term --cov=aea -v --ignore=tests/test_connections/test_oef/' > /home/agents-aea/test_commands.sh
###ACTION_DELIMITER###
bash /home/agents-aea/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pipenv run pytest --doctest-modules aea tests/ --cov-report=html --cov-report=term --cov=aea -v --ignore=tests/test_connections/test_oef/

""".replace("[[REPO_NAME]]", repo_name)
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
if ! git -C /home/[[REPO_NAME]] apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
pipenv run pytest --doctest-modules aea tests/ --cov-report=html --cov-report=term --cov=aea -v --ignore=tests/test_connections/test_oef/

""".replace("[[REPO_NAME]]", repo_name)
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
if ! git -C /home/[[REPO_NAME]] apply --whitespace=nowarn  /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
pipenv run pytest --doctest-modules aea tests/ --cov-report=html --cov-report=term --cov=aea -v --ignore=tests/test_connections/test_oef/

""".replace("[[REPO_NAME]]", repo_name)
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
RUN git clone https://github.com/fetchai/agents-aea.git /home/agents-aea

WORKDIR /home/agents-aea
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("fetchai", "agents_aea_158_to_147")
class AGENTS_AEA_158_TO_147(Instance):
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
        summary_failed: set[str] = set()  # Summary failed tests (authoritative)
        summary_skipped: set[str] = set()  # Summary skipped tests (authoritative)
        import re
        # Parse test cases from log content
        # Pattern for test cases with status on the same line (e.g., "test_name PASSED [  2%]")
        same_line_pattern = re.compile(r'^(?:\[\s*\d+\]\s+)?([\w/]+\.py::[\w.:]+(?:\[\S+\])?).*(PASSED|FAILED|SKIPPED)(?:\s+\[\s*\d+%?\])?', re.MULTILINE)
        for match in same_line_pattern.finditer(log):
            test_name = match.group(1).strip()
            status = match.group(2)
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
        # Pattern for summary section test cases (e.g., "FAILED test_name")
        summary_pattern = re.compile(r'^(FAILED|ERROR|SKIPPED)\s+(.*)$', re.MULTILINE)
        # Find the summary section to avoid false positives
        summary_start = log.find('=========================== short test summary info ============================')
        if summary_start != -1:
            summary_log = log[summary_start:]
            for match in summary_pattern.finditer(summary_log):
                status = match.group(1)
                test_name = match.group(2).strip()
                if status in ['FAILED', 'ERROR']:
                    summary_failed.add(test_name)
                elif status == 'SKIPPED':
                    summary_skipped.add(test_name)
        # Handle test cases where name and status are on separate lines (e.g., test name on one line, PASSED on next)
        separate_line_pattern = re.compile(r'^(?:\[\s*\d+\]\s+)?([\w/]+\.py::[\w.:]+(?:\[\S+\])?)\n.*?^(?:\[\s*\d+\]\s+)?PASSED(?:\s+\[\s*\d+%?\])?', re.MULTILINE | re.DOTALL)
        for match in separate_line_pattern.finditer(log):
            test_name = match.group(1).strip()
            passed_tests.add(test_name)
        # Prioritize summary statuses over individual line matches
        final_status = {}
        for test in passed_tests:
            final_status[test] = "passed"
        for test in failed_tests:
            final_status[test] = "failed"
        for test in skipped_tests:
            final_status[test] = "skipped"
        # Overwrite with summary results
        for test in summary_failed:
            final_status[test] = "failed"
        for test in summary_skipped:
            final_status[test] = "skipped"
        parsed_results = {
            "passed_tests": {t for t, s in final_status.items() if s == "passed"},
            "failed_tests": {t for t, s in final_status.items() if s == "failed"},
            "skipped_tests": {t for t, s in final_status.items() if s == "skipped"}
        }
        

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
