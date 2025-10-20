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
python run-tests.py --help
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
python run-tests.py --help
###ACTION_DELIMITER###
echo 'python run-tests.py --all --examples' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libsundials-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y libsuitesparse-dev libopenblas-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgfortran5 jupyter nbconvert && pip install jupyter nbconvert && export MPLBACKEND=Agg
###ACTION_DELIMITER###
pip install nbconvert ipykernel && export MPLBACKEND=Agg
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y graphviz && pip install pygraphviz && export MPLBACKEND=Agg
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgraphviz-dev && pip install pygraphviz && export MPLBACKEND=Agg
###ACTION_DELIMITER###
echo 'pytest --verbose --color=yes --tb=short tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
echo 'python run-tests.py --all --examples' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest --verbose --color=yes --tb=short tests/' > test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest --verbose --color=yes --tb=short tests/

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
pytest --verbose --color=yes --tb=short tests/

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
pytest --verbose --color=yes --tb=short tests/

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
RUN git clone https://github.com/pybamm-team/PyBaMM.git /home/PyBaMM

WORKDIR /home/PyBaMM
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pybamm-team", "PyBaMM_2959_to_2764")
class PYBAMM_2959_TO_2764(Instance):
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
        # Regex patterns to match test lines (Type 1: test name first, Type 2: status first)
        pattern1 = re.compile(r'^(.+?)\s+\x1b\[\d+m(FAILED|PASSED|SKIPPED)\x1b\[0m', re.MULTILINE)
        pattern2 = re.compile(r'^\[\d+\]\s+\x1b\[\d+m(FAILED|PASSED|SKIPPED)\x1b\[0m\s+(.+?)\s+-', re.MULTILINE)
        # Process Type 1 matches (test name followed by status)
        for match in pattern1.findall(log):
            test_name, status = match
            clean_name = re.sub(r'\x1b\[.*?m', '', test_name).strip()
            if status == 'PASSED':
                passed_tests.add(clean_name)
            elif status == 'FAILED':
                failed_tests.add(clean_name)
            elif status == 'SKIPPED':
                skipped_tests.add(clean_name)
        # Process Type 2 matches (status followed by test name)
        for match in pattern2.findall(log):
            status, test_name = match
            clean_name = re.sub(r'\x1b\[.*?m', '', test_name).strip()
            if status == 'PASSED':
                passed_tests.add(clean_name)
            elif status == 'FAILED':
                failed_tests.add(clean_name)
            elif status == 'SKIPPED':
                skipped_tests.add(clean_name)
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
