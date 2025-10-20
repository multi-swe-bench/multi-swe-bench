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
                """ls .github/workflows
###ACTION_DELIMITER###
apt-get update && apt-get install -y libopenblas-dev gfortran liblapack-dev glpk-utils
###ACTION_DELIMITER###
python -m pip install --upgrade pip setuptools && python setup.py dependencies --extras 'tests,docs,optional' | tail -1 | xargs python -m pip install
###ACTION_DELIMITER###
echo 'pytest --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --full-trace -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.26.4
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
pip install .[docs]
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
pip install -e .[tests,docs]
###ACTION_DELIMITER###
pip install pytest-baseline
###ACTION_DELIMITER###
pip install pytest-regressions
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --full-trace -p no:cacheprovider --ignore=doc/OnlineDocs/tests/test_examples.py' > test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
apt-get install -y lsb-release
###ACTION_DELIMITER###
pip install pytest-json-report
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --full-trace -p no:cacheprovider --ignore=doc/OnlineDocs/tests/test_examples.py --json-report --json-report-file=-' > test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v --no-header -rA --full-trace -p no:cacheprovider --ignore=doc/OnlineDocs/tests/test_examples.py --json-report --json-report-file=-

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
pytest -v --no-header -rA --full-trace -p no:cacheprovider --ignore=doc/OnlineDocs/tests/test_examples.py --json-report --json-report-file=-

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
pytest -v --no-header -rA --full-trace -p no:cacheprovider --ignore=doc/OnlineDocs/tests/test_examples.py --json-report --json-report-file=-

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
RUN git clone https://github.com/Pyomo/pyomo.git /home/pyomo

WORKDIR /home/pyomo
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Pyomo", "pyomo_3054_to_2557")
class PYOMO_3054_TO_2557(Instance):
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
        import re
        import json
        # Define regex patterns to match test result lines
        # Pattern 1: Capture test name as non-whitespace characters
        pattern1 = re.compile(r'^\[\s*\d+\s*\]\s+([^\s]+)\s+(PASSED|FAILED|SKIPPED)\s+.*$')
        # Pattern 2: Capture test name as non-whitespace characters
        pattern2 = re.compile(r'^\[\s*\d+\s*\]\s+(PASSED|FAILED|SKIPPED)\s+([^\s]+)\s+.*$')
        # Pattern 3: Capture test name as non-whitespace characters
        pattern3 = re.compile(r'^([^\s]+)\s+(PASSED|FAILED|SKIPPED)\s+.*$')
        for line in log.split('\n'):
            line = line.strip()
            # Check pattern 1: [line num] test_name status [percentage]
            match = pattern1.match(line)
            if match:
                test_name = match.group(1).strip()
                status = match.group(2)
            else:
                # Check pattern 2: [line num] status test_name [error]
                match = pattern2.match(line)
                if match:
                    status = match.group(1)
                    test_name = match.group(2).strip()
                else:
                    # Check pattern 3: test_name status [percentage] (no line num)
                    match = pattern3.match(line)
                    if match:
                        test_name = match.group(1).strip()
                        status = match.group(2)
                    else:
                        continue  # No match, skip
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
