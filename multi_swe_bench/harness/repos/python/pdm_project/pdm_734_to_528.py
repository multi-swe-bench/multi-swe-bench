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
apt-get update && apt-get install -y git-lfs
###ACTION_DELIMITER###
git lfs install && git lfs pull
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
sed -i '/version = {use_scm = true}/d' pyproject.toml
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pdm install -d
###ACTION_DELIMITER###
pip install six
###ACTION_DELIMITER###
pdm install -d
###ACTION_DELIMITER###
pip install --force-reinstall pythonfinder
###ACTION_DELIMITER###
pip install pythonfinder==2.0.5
###ACTION_DELIMITER###
pdm install -d
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
pip install pip==22.0
###ACTION_DELIMITER###
pdm install -d
###ACTION_DELIMITER###
pdm install -d -v
###ACTION_DELIMITER###
pip install pythonfinder==1.2.3
###ACTION_DELIMITER###
pip install pythonfinder==2.0.0
###ACTION_DELIMITER###
pip install pythonfinder==1.2.3
###ACTION_DELIMITER###
pdm config python.path /usr/local/bin/python3.9 && pdm install -d
###ACTION_DELIMITER###
pip install packaging==20.9
###ACTION_DELIMITER###
pdm install -d
###ACTION_DELIMITER###
pip install --upgrade pip==23.0
###ACTION_DELIMITER###
pdm lock
###ACTION_DELIMITER###
pip install pip==22.0
###ACTION_DELIMITER###
pip install html5lib
###ACTION_DELIMITER###
pip install pip==20.3.4
###ACTION_DELIMITER###
pdm install -d
###ACTION_DELIMITER###
echo 'pdm run pytest -v tests/' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pdm run pytest -v tests/

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
pdm run pytest -v tests/

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
pdm run pytest -v tests/

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
RUN git clone https://github.com/pdm-project/pdm.git /home/pdm

WORKDIR /home/pdm
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pdm-project", "pdm_734_to_528")
class PDM_734_TO_528(Instance):
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
        # Regex patterns to match test results
        passed_pattern = re.compile(r'^(tests/.*?)\s+PASSED\s+\[\s*\d+%\]', re.MULTILINE)
        failed_pattern = re.compile(r'^FAILED\s+(tests/.*?)\s+-', re.MULTILINE)
        skipped_pattern1 = re.compile(r'^(tests/.*?)\s+SKIPPED\s+\[\s*\d+%\]', re.MULTILINE)
        skipped_pattern2 = re.compile(r'^SKIPPED\s+(tests/.*?)\s+-', re.MULTILINE)
        # Extract passed tests
        passed_matches = passed_pattern.findall(log)
        for test in passed_matches:
            passed_tests.add(test.strip())
        # Extract failed tests
        failed_matches = failed_pattern.findall(log)
        for test in failed_matches:
            failed_tests.add(test.strip())
        # Extract skipped tests
        skipped_matches1 = skipped_pattern1.findall(log)
        skipped_matches2 = skipped_pattern2.findall(log)
        for test in skipped_matches1 + skipped_matches2:
            skipped_tests.add(test.strip())
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
