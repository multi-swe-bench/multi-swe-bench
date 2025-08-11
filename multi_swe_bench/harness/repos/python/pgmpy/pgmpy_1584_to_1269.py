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
apt-get update && apt-get install -y libopenblas-dev gfortran
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
pip install .
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install numpy==1.26.4
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip uninstall -y networkx && pip install networkx==2.8.8
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install daft && pip uninstall -y pandas && pip install pandas==1.5.3
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install --force-reinstall daft
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
python -c 'import daft; print(daft.__version__)'
###ACTION_DELIMITER###
pip uninstall -y daft && pip install daft==0.4.1
###ACTION_DELIMITER###
pip install daft==0.4.7
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install matplotlib
###ACTION_DELIMITER###
python -c 'from daft import PGM; print("Success")'
###ACTION_DELIMITER###
pip uninstall -y daft && pip install daft-pgm
###ACTION_DELIMITER###
pip uninstall -y daft-pgm && pip install daft==0.0.4
###ACTION_DELIMITER###
pip uninstall -y daft && pip install daft-pgm && python -c 'from daft import PGM; print("PGM imported successfully")'
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
echo 'pytest -v' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v

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
pytest -v

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
pytest -v

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
RUN git clone https://github.com/pgmpy/pgmpy.git /home/pgmpy

WORKDIR /home/pgmpy
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pgmpy", "pgmpy_1584_to_1269")
class PGMPY_1584_TO_1269(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re
        # Regex patterns based on log analysis
        # Updated patterns to match real log format (no sample line numbers)
        passed_pattern = re.compile(r'^(pgmpy/tests/.*?)\s+PASSED\s+\[\s*\d+%\]$', re.MULTILINE)
        failed_pattern = re.compile(r'^FAILED\s+(pgmpy/tests/[^\s]+)$', re.MULTILINE)
        skipped_pattern_exec = re.compile(r'^(pgmpy/tests/.*?)\s+SKIPPED\s+\[\s*\d+%\]$', re.MULTILINE)
        skipped_pattern_summary = re.compile(r'^SKIPPED\s+(pgmpy/tests/[^\s]+)$', re.MULTILINE)
        for line in log.split('\n'):
            # Match passed tests from execution lines
            passed_match = passed_pattern.search(line)
            if passed_match:
                passed_tests.add(passed_match.group(1))
            # Match skipped tests from execution lines
            skipped_exec_match = skipped_pattern_exec.search(line)
            if skipped_exec_match:
                skipped_tests.add(skipped_exec_match.group(1))
            # Match failed tests from summary lines
            failed_match = failed_pattern.search(line)
            if failed_match:
                failed_tests.add(failed_match.group(1))
            # Match skipped tests from summary lines
            skipped_sum_match = skipped_pattern_summary.search(line)
            if skipped_sum_match:
                skipped_tests.add(skipped_sum_match.group(1))
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
