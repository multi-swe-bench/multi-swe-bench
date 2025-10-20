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
        return "python:3.11-slim"
    
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
                """ls -la
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install -r dev-requirements.txt
###ACTION_DELIMITER###
echo 'pytest -v -rA --tb=short' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip --version
###ACTION_DELIMITER###
cat setup.py
###ACTION_DELIMITER###
pip install --upgrade pip==20.3.4
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install --upgrade pip==19.3.1
###ACTION_DELIMITER###
cat dev-requirements.txt
###ACTION_DELIMITER###
cat piptools/_compat/pip_compat.py
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.9
###ACTION_DELIMITER###
apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl
###ACTION_DELIMITER###
curl https://pyenv.run | bash
###ACTION_DELIMITER###
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc && echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc && echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc && source ~/.bashrc
###ACTION_DELIMITER###
pyenv install 3.9.0
###ACTION_DELIMITER###
pyenv local 3.9.0
###ACTION_DELIMITER###
python --version
###ACTION_DELIMITER###
pip --version
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install --upgrade pip==20.0.2
###ACTION_DELIMITER###
pip install --upgrade pip==20.1
###ACTION_DELIMITER###
pip install --upgrade pip==20.0.2
###ACTION_DELIMITER###
pip install --upgrade pip==20.2.4
###ACTION_DELIMITER###
pip install --upgrade pip==19.3.1 && pip install -e . && pip install -r dev-requirements.txt && bash test_commands.sh
###ACTION_DELIMITER###
pip install --upgrade pip==19.0 && pip install -e . && pip install -r dev-requirements.txt && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -rA --tb=short' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v -rA --tb=short

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
pytest -v -rA --tb=short

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
pytest -v -rA --tb=short

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

# Choose an appropriate base image based on the project's requirements - replace python:3.11-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.11-slim

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
RUN git clone https://github.com/jazzband/pip-tools.git /home/pip-tools

WORKDIR /home/pip-tools
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("jazzband", "pip_tools_909_to_644")
class PIP_TOOLS_909_TO_644(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re
        # Regex pattern to match test names and statuses. Handles two formats:
        # 1. Test name followed by status (e.g., "tests/... PASSED")
        # 2. Status followed by test name (e.g., "FAILED tests/...")
        # Test names can be in format "tests/...py::test..." or "tests/...py:line_number"
        pattern = r'^(PASSED|FAILED|SKIPPED)\s+(.*)$|^(.*?)\s+(PASSED|FAILED|SKIPPED)$'
        matches = re.findall(pattern, log, re.MULTILINE)
        for match in matches:
            test_name = None
            status = None
            # Check if first part of the pattern matched (test name followed by status)
            if match[0] and match[1]:
                status = match[0]
                test_name = match[1]
            # Check if second part of the pattern matched (status followed by test name)
            elif match[2] and match[3]:
                test_name = match[2]
                status = match[3]
            else:
                continue  # No match
            # Add to the appropriate set
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
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
