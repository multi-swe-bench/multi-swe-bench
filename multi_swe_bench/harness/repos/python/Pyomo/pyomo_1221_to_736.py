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
                """ls
###ACTION_DELIMITER###
pip install .
###ACTION_DELIMITER###
find . -name "test_*.py"
###ACTION_DELIMITER###
echo 'nosetests -v' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
pip install PyUtilib==5.7.3.dev0
###ACTION_DELIMITER###
pip install PyUtilib==5.7.3
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3-dev libssl-dev libffi-dev ampl-mp && pip install pyyaml
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3-dev libssl-dev libffi-dev python3-venv && pip install pyyaml
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest && echo 'pytest --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest pyomo --verbose' > test_commands.sh && pip install cyipopt && pip install 'pyyaml<6.0'
###ACTION_DELIMITER###
apt-get update && apt-get install -y pkg-config glpk-utils coinor-ipopt && echo 'pytest pyomo --verbose' > test_commands.sh && pip install cyipopt
###ACTION_DELIMITER###
apt-get update && apt-get install -y pkg-config glpk-utils ipopt ampl-mp && echo 'pytest pyomo --verbose' > test_commands.sh && pip install cyipopt
###ACTION_DELIMITER###
sed -i 's/main/main contrib non-free/' /etc/apt/sources.list && apt-get update && apt-get install -y pkg-config glpk-utils coinor-ipopt && pip install cyipopt
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bookworm main contrib non-free' > /etc/apt/sources.list.d/debian.list && apt-get update && apt-get install -y pkg-config glpk-utils coinor-ipopt && echo 'pytest pyomo --verbose' > test_commands.sh && pip install cyipopt
###ACTION_DELIMITER###
apt-get update && apt-get install -y glpk-utils && echo 'pytest pyomo --verbose --ignore=ATTIC' > test_commands.sh && pip install cyipopt
###ACTION_DELIMITER###
apt-get update && apt-get install -y pkg-config glpk-utils && echo 'pytest pyomo --verbose --ignore=ATTIC' > test_commands.sh && pip install cyipopt
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bookworm main contrib non-free' > /etc/apt/sources.list.d/debian-contrib.list && apt-get update && apt-get install -y coinor-ipopt coinor-ipopt-dev pkg-config glpk-utils && echo 'pytest pyomo --verbose --ignore=ATTIC' > test_commands.sh && pip install cyipopt
###ACTION_DELIMITER###
apt-get update && apt-get install -y ipopt ipopt-dev pkg-config glpk-utils && echo 'pytest pyomo --verbose --ignore=ATTIC' > test_commands.sh && pip install cyipopt
###ACTION_DELIMITER###
rm -f /etc/apt/sources.list.d/debian.list /etc/apt/sources.list.d/debian-contrib.list && echo 'deb http://deb.debian.org/debian bookworm main contrib' > /etc/apt/sources.list.d/debian.list && apt-get update && apt-get install -y coinor-ipopt coinor-ipopt-dev glpk-utils pkg-config && echo 'pytest pyomo --verbose --ignore=ATTIC' > test_commands.sh && pip install cyipopt
###ACTION_DELIMITER###
apt-get update && apt-get install -y glpk-utils && echo 'pytest pyomo --verbose --ignore=ATTIC' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip install 'pyyaml<6.0' && echo 'pytest pyomo --verbose --ignore=ATTIC --ignore=pyomo/contrib/pynumero/algorithms/solvers/tests/test_cyipopt_solver.py' > test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest pyomo --verbose --ignore=ATTIC --ignore=pyomo/contrib/pynumero/algorithms/solvers/tests/test_cyipopt_solver.py

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
pytest pyomo --verbose --ignore=ATTIC --ignore=pyomo/contrib/pynumero/algorithms/solvers/tests/test_cyipopt_solver.py

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
pytest pyomo --verbose --ignore=ATTIC --ignore=pyomo/contrib/pynumero/algorithms/solvers/tests/test_cyipopt_solver.py

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
RUN git clone https://github.com/Pyomo/pyomo.git /home/pyomo

WORKDIR /home/pyomo
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Pyomo", "pyomo_1221_to_736")
class PYOMO_1221_TO_736(Instance):
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
        # Implement the log parsing logic here
        # Regex pattern to match test lines with status at end or beginning
        pattern = re.compile(
            r'(?P<test_name>[\w/]+\.py::[\w:]+)\s+(?P<status>PASSED|FAILED|SKIPPED)|(?P<status2>PASSED|FAILED|SKIPPED)\s+(?P<test_name2>[\w/]+\.py::[\w:]+)'
        )
        for line in log.split('\n'):
            match = pattern.search(line)
            if match:
                # Check which group matched
                if match.group('test_name') and match.group('status'):
                    test_name = match.group('test_name')
                    status = match.group('status')
                else:
                    test_name = match.group('test_name2')
                    status = match.group('status2')
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
