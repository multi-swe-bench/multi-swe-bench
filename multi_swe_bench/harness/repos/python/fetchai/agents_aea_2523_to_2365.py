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
        return "python:3.9"
    
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
                """pipenv install -e .
###ACTION_DELIMITER###
pip install pipenv
###ACTION_DELIMITER###
pipenv --python 3.9 && pipenv install --dev
###ACTION_DELIMITER###
pipenv run pip install openapi-core==0.13.2
###ACTION_DELIMITER###
pipenv run pip install 'pip<24.1'
###ACTION_DELIMITER###
pipenv run pip install openapi-core==0.13.2
###ACTION_DELIMITER###
pipenv install --dev
###ACTION_DELIMITER###
sed -i 's/tensorflow = "==2.4.0"/tensorflow = "==2.5.0"/' Pipfile
###ACTION_DELIMITER###
pipenv install --dev
###ACTION_DELIMITER###
echo '#!/bin/bash
pytest -v -rA --doctest-modules aea packages/fetchai/protocols packages/fetchai/connections packages/fetchai/skills tests/ --cov=aea --cov-report=term --cov-report=term-missing' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
pip install -e ".[dev]"
###ACTION_DELIMITER###
pip install click
###ACTION_DELIMITER###
pip install pycryptodome==3.10.1 docker==4.2.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest==5.4.3 pytest-asyncio==0.12.0 pytest-cov==2.9.0
###ACTION_DELIMITER###
pip install setuptools==41.0.0
###ACTION_DELIMITER###
pip install pytest==5.4.3 pytest-asyncio==0.12.0 pytest-cov==2.9.0
###ACTION_DELIMITER###
pip install setuptools==50.0.0
###ACTION_DELIMITER###
pip install setuptools==58.0.0
###ACTION_DELIMITER###
pip install setuptools==65.0.0
###ACTION_DELIMITER###
pip install pytest==5.4.3 pytest-asyncio==0.15.0 pytest-cov==2.9.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install gym==0.15.6
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -e plugins/aea-ledger-cosmos
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -e plugins/aea-ledger-ethereum
###ACTION_DELIMITER###
pip install -e plugins/aea-ledger-fetchai
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install click==7.1.2
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install oef==0.8.1
###ACTION_DELIMITER###
pip install --force-reinstall oef==0.8.1
###ACTION_DELIMITER###
pip install --force-reinstall --no-deps oef==0.8.1
###ACTION_DELIMITER###
pip install oef==0.8.1 protobuf==3.13.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install colorlog==4.1.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install aiohttp==3.7.4 aioprometheus==20.0.1 bandit==1.7.0 bech32==1.2.0 black==19.10b0 bs4==0.0.1 colorlog==4.1.0 defusedxml==0.6.0 docker==4.2.0 ecdsa>=0.15 eth-account==0.5.2 flake8==3.7.9 flake8-bugbear==20.1.4 flake8-docstrings==1.5.0 flake8-eradicate==0.4.0 flake8-isort==4.0.0 gitpython>=3.1.14 gym==0.15.6 ipfshttpclient==0.6.1 liccheck==0.4.3 markdown==3.2.1 matplotlib==3.2.1 memory-profiler==0.57.0 mistune==2.0.0a4 mkdocs==1.1 mkdocs-material==4.6.3 mypy==0.761 numpy>=1.18.1 oef==0.8.1 openapi-core==0.13.2 openapi-spec-validator==0.2.8 packaging==20.4 pexpect==4.8.0 psutil==5.7.0 pycryptodome>=3.10.1 pydoc-markdown==3.10.3 pydocstyle==3.0.0 pygments==2.7.4 pylint==2.6.0 pymdown-extensions==6.3 pytest==5.4.3 pytest-asyncio==0.12.0 pytest-cov==2.9.0 pytest-custom-exit-code==0.3.0 pytest-randomly==3.4.0 pytest-rerunfailures==9.0 requests>=2.22.0 safety==1.10.3 scikit-image>=0.17.2 sqlalchemy==1.3.17 temper-py==0.0.3 tensorflow==2.5.0 tox==3.15.1 vulture==2.3 isort==5.7.0 web3==5.12.0 yoti==2.14.0
###ACTION_DELIMITER###
bash test_commands.sh -v --showlocals --full-trace
###ACTION_DELIMITER###
echo '#!/bin/bash
pytest -v tests/test_packages/test_skills/test_simple_oracle/test_handlers.py' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
pytest -v tests/test_packages/test_skills/test_simple_oracle/ tests/test_packages/test_skills/test_aries_alice/' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
pytest -v tests/ packages/fetchai/protocols/ packages/fetchai/connections/ packages/fetchai/skills/' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
pytest -v tests/ packages/fetchai/protocols/ packages/fetchai/connections/ packages/fetchai/skills/

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
#!/bin/bash
pytest -v tests/ packages/fetchai/protocols/ packages/fetchai/connections/ packages/fetchai/skills/

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
#!/bin/bash
pytest -v tests/ packages/fetchai/protocols/ packages/fetchai/connections/ packages/fetchai/skills/

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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.9

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


@Instance.register("fetchai", "agents_aea_2523_to_2365")
class AGENTS_AEA_2523_TO_2365(Instance):
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
        # Compile regex patterns to match test cases and statuses
        # Adjust regex to ignore leading content (e.g., line numbers in brackets)
        # Refine regex to match test cases (format: tests/.../test_*.py::TestClass::test_method)
        pattern_test_status = re.compile(r'(tests/[\w/]+\.py::[\w:]+)\s+(PASSED|FAILED|SKIPPED)')  # Test case + status
        pattern_error_test = re.compile(r'ERROR\s+(tests/[\w/]+\.py::[\w:]+)')  # ERROR + test case
        pattern_status_line = re.compile(r'(PASSED|FAILED|SKIPPED)\s+\[.*?\]')  # Status with percentage
        pattern_test_name = re.compile(r'tests/[\w/]+\.py::[\w:]+')  # Extract test case name
        current_test = None
        for line in log.split('\n'):
            line = line.strip()
            # Match test name followed by status (e.g., '[123] tests/... PASSED')
            match = pattern_test_status.search(line)
            if match:
                test_name, status = match.groups()
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
                continue
            # Match ERROR followed by test name (e.g., '[456] ERROR tests/...')
            match = pattern_error_test.search(line)
            if match:
                test_name = match.group(1)
                failed_tests.add(test_name)
                continue
            # Extract test name from lines with leading content (e.g., '[789] tests/...')
            match = pattern_test_name.search(line)
            if match:
                current_test = match.group(0)
                continue
            # Match status line and associate with current test (e.g., '[012] PASSED [  0%]')
            match = pattern_status_line.search(line)
            if match:
                status = match.group(1)
                if current_test:
                    if status == 'PASSED':
                        passed_tests.add(current_test)
                    elif status == 'FAILED':
                        failed_tests.add(current_test)
                    elif status == 'SKIPPED':
                        skipped_tests.add(current_test)
                    current_test = None
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
