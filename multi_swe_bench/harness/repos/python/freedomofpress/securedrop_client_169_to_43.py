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
        return "ubuntu:latest"
    
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
                """ls
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip python3-pyqt5 python3-pyqt5.qtsvg xvfb
###ACTION_DELIMITER###
pip3 install pipenv
###ACTION_DELIMITER###
apt-get install -y pipx
###ACTION_DELIMITER###
pipx install pipenv
###ACTION_DELIMITER###
pipx ensurepath
###ACTION_DELIMITER###
export PATH="$HOME/.local/bin:$PATH"
###ACTION_DELIMITER###
pipenv install --dev
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository -y ppa:deadsnakes/ppa
###ACTION_DELIMITER###
apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl
###ACTION_DELIMITER###
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
###ACTION_DELIMITER###
export PATH="$HOME/.pyenv/bin:$PATH" && eval "$(pyenv init -)"
###ACTION_DELIMITER###
pyenv install 3.5.10
###ACTION_DELIMITER###
pyenv local 3.5.10
###ACTION_DELIMITER###
pipenv install --dev
###ACTION_DELIMITER###
pip3 install virtualenv==20.0.35
###ACTION_DELIMITER###
pip3 install --upgrade pip==20.3.4
###ACTION_DELIMITER###
python -m pip install virtualenv==20.0.35
###ACTION_DELIMITER###
export LANG=en_US.UTF-8 && pipenv install --dev
###ACTION_DELIMITER###
pipx runpip pipenv install virtualenv==20.0.35
###ACTION_DELIMITER###
pipx install pipenv==2020.11.15
###ACTION_DELIMITER###
pipx install --force pipenv==2020.11.15
###ACTION_DELIMITER###
pipenv install --dev
###ACTION_DELIMITER###
pipx install --force pipenv==2021.5.29
###ACTION_DELIMITER###
export LANG=en_US.UTF-8 && pipenv install --dev
###ACTION_DELIMITER###
pipx install --python ~/.pyenv/versions/3.5.10/bin/python pipenv==2021.5.29
###ACTION_DELIMITER###
pipx install --force --python ~/.pyenv/versions/3.5.10/bin/python pipenv==2021.5.29
###ACTION_DELIMITER###
pipx reinstall pipenv==2021.5.29 --python ~/.pyenv/versions/3.5.10/bin/python
###ACTION_DELIMITER###
pyenv local 3.5.10 && python -m pip install pipenv==2021.5.29
###ACTION_DELIMITER###
export LANG=en_US.UTF-8 && pipenv install --dev
###ACTION_DELIMITER###
export PATH="$HOME/.pyenv/versions/3.5.10/bin:$PATH" && python -m pip install --force-reinstall pipenv==2021.5.29 && pipenv install --dev
###ACTION_DELIMITER###
pip install setuptools==39.2.0 && pipenv install --dev
###ACTION_DELIMITER###
pipenv run pip install setuptools==39.2.0 && pipenv install --dev
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
pipenv run make test
###ACTION_DELIMITER###
echo 'pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pipenv run make test

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
pipenv run make test

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
pipenv run make test

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:latest with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:latest

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
RUN git clone https://github.com/freedomofpress/securedrop-client.git /home/securedrop-client

WORKDIR /home/securedrop-client
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("freedomofpress", "securedrop_client_169_to_43")
class SECUREDROP_CLIENT_169_TO_43(Instance):
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
        import json
        # Regex pattern to match test lines with status
        pattern = re.compile(r'(tests/[^ ]+)\s+(PASSED|FAILED|SKIPPED)(?:\s+\[\s*\d+%\s*\])?', re.IGNORECASE)
        # Split log into lines and process each line
        for line in log.split('\n'):
            line = line.strip()
            match = pattern.search(line)
            if match:
                test_name = match.group(1)
                status = match.group(2).upper()
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
