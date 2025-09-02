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
pip install -r test_requirements.txt
###ACTION_DELIMITER###
pip install -e .[d,jupyter]
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider tests' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest==6.2.5
###ACTION_DELIMITER###
pip install pytest-xdist==2.5.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider --run-optional no_python2 tests' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'tox -e py39 -- -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest==7.0.0
###ACTION_DELIMITER###
pip install pytest-xdist==3.0.2
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pytest >= 6.1.1/pytest >= 7.0.0/' test_requirements.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
tox -e py39 -- pip freeze | grep pytest
###ACTION_DELIMITER###
rm -rf .tox && bash test_commands.sh
###ACTION_DELIMITER###
tox -e py39 -- pip freeze | grep pytest
###ACTION_DELIMITER###
tox -e py39 -- pip install pytest==7.0.0 && bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest==7.0.0 && pytest -v --run-optional no_python2 tests
###ACTION_DELIMITER###
sed -i 's/pytest >= 7.0.0/pytest >= 6.1.1/' test_requirements.txt && rm -rf .tox && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pytest >= 6.1.1/pytest >= 7.0.0/' test_requirements.txt && rm -rf .tox && bash test_commands.sh
###ACTION_DELIMITER###
echo 'tox -e py39 -- pip install pytest==7.0.0 && pytest -v --run-optional no_python2 tests' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --run-optional no_python2 tests' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'tox -e py39 -- pip install pytest==7.0.0 pytest-xdist==3.0.2 && pytest -v --run-optional no_python2 tests' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'tox -e py39 -- sh -c "pip install pytest==7.0.0 pytest-xdist==3.0.2 && pytest -v --run-optional no_python2 tests"' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'pip install -r test_requirements.txt\npip install pytest==7.0.0 pytest-xdist==3.0.2\npytest -v --run-optional no_python2 tests' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --run-optional no_python2 tests -k "not optional"' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --run-optional no_python2 --ignore=tests/optional.py tests' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --run-optional no_python2 -p no:tests.optional tests' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest==7.0.0 && pytest -v --run-optional no_python2 tests
###ACTION_DELIMITER###
echo 'pip install pytest==7.0.0 && pytest -v -p no:tests.optional --run-optional no_python2 tests' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -p no:tests.optional tests' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -p no:tests.optional --ignore=tests/test_no_ipynb.py tests' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -p no:tests.optional --ignore=tests/test_no_ipynb.py tests' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v -p no:tests.optional --ignore=tests/test_no_ipynb.py tests

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
pytest -v -p no:tests.optional --ignore=tests/test_no_ipynb.py tests

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
pytest -v -p no:tests.optional --ignore=tests/test_no_ipynb.py tests

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
RUN git clone https://github.com/psf/black.git /home/black

WORKDIR /home/black
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("psf", "black_2690_to_75")
class BLACK_2690_TO_75(Instance):
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
        # Regex patterns to identify test cases and their statuses
        # Pattern 1: Matches lines like "tests/...::... PASSED [  0%]"
        pattern1 = re.compile(
            r'^(tests/[\w\/\.\-::\[\]]+)\s+'  # Test name (includes tests/, colons, brackets)
            r'(passed|failed|skipped|xfailed|xfail) '  # Status (case-insensitive)
            r'\s*\[.+\]$',  # Percentage in brackets
            re.MULTILINE | re.IGNORECASE
        )
        # Pattern 2: Matches summary lines like "FAILED tests/...::..."
        pattern2 = re.compile(
            r'(passed|failed|skipped|xfailed|xfail) '  # Status (case-insensitive)
            r'(tests/[\w\/\.::\[\]]+)',  # Test name
            re.MULTILINE | re.IGNORECASE
        )
        # Process matches from pattern1
        for match in pattern1.finditer(log):
            test_name = match.group(1)
            status = match.group(2)
            if status.upper() == 'PASSED':
                passed_tests.add(test_name)
            elif status.upper() == 'FAILED':
                failed_tests.add(test_name)
            elif status.upper() in ('SKIPPED', 'XFAILED', 'XFAIL'):
                skipped_tests.add(test_name)
        # Process matches from pattern2
        for match in pattern2.finditer(log):
            status = match.group(1)
            test_name = match.group(2)
            if status.upper() == 'PASSED':
                passed_tests.add(test_name)
            elif status.upper() == 'FAILED':
                failed_tests.add(test_name)
            elif status.upper() in ('SKIPPED', 'XFAILED', 'XFAIL'):
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
