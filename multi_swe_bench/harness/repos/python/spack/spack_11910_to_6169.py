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
ls -d */
###ACTION_DELIMITER###
ls lib
###ACTION_DELIMITER###
ls lib/spack
###ACTION_DELIMITER###
spack help
###ACTION_DELIMITER###
ls bin
###ACTION_DELIMITER###
./bin/spack help
###ACTION_DELIMITER###
./bin/spack help --all
###ACTION_DELIMITER###
find . -name tests
###ACTION_DELIMITER###
ls -d .github
###ACTION_DELIMITER###
ls .github
###ACTION_DELIMITER###
find . -name "test_*.py"
###ACTION_DELIMITER###
pip list | grep pytest
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
pytest -v ./lib/spack/spack/test/
###ACTION_DELIMITER###
pip install ordereddict-backport
###ACTION_DELIMITER###
pip install ordereddict
###ACTION_DELIMITER###
pytest -v ./lib/spack/spack/test/
###ACTION_DELIMITER###
find . -name 'ordereddict_backport.py'
###ACTION_DELIMITER###
export PYTHONPATH=$PYTHONPATH:/home/spack/lib/spack && pytest -v ./lib/spack/spack/test/
###ACTION_DELIMITER###
export PYTHONPATH=$PYTHONPATH:/home/spack/lib/spack/external && pytest -v ./lib/spack/spack/test/
###ACTION_DELIMITER###
python -m venv venv && source venv/bin/activate && pip install pytest && export PYTHONPATH=/home/spack/lib/spack/external:$PYTHONPATH && pytest -v ./lib/spack/spack/test/
###ACTION_DELIMITER###
./bin/spack help test
###ACTION_DELIMITER###
./bin/spack test -- -v
###ACTION_DELIMITER###
./bin/spack test -l
###ACTION_DELIMITER###
./bin/spack-python -m pytest -v lib/spack/spack/test/
###ACTION_DELIMITER###
export PATH=$PATH:./bin && ./bin/spack-python -m pytest -v lib/spack/spack/test/
###ACTION_DELIMITER###
export PYTEST_ADDOPTS="-v" && ./bin/spack test
###ACTION_DELIMITER###
echo 'export PYTEST_ADDOPTS="-v" && ./bin/spack test' > /home/spack/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
export PYTEST_ADDOPTS="-v" && ./bin/spack test

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
export PYTEST_ADDOPTS="-v" && ./bin/spack test

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
export PYTEST_ADDOPTS="-v" && ./bin/spack test

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
RUN git clone https://github.com/spack/spack.git /home/spack

WORKDIR /home/spack
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("spack", "spack_11910_to_6169")
class SPACK_11910_TO_6169(Instance):
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
        pattern = re.compile(r'^\s*(\[\d+\]\s+)?(\S+::\S+)\s+(PASSED|FAILED|SKIPPED)', re.IGNORECASE | re.MULTILINE)
        matches = pattern.findall(log)
        for line_num_part, test_name, status in matches:
            if status.upper() == 'PASSED':
                passed_tests.add(test_name)
            elif status.upper() == 'FAILED':
                failed_tests.add(test_name)
            elif status.upper() == 'SKIPPED':
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
