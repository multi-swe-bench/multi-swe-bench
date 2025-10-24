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
        repo_name = self.pr.repo
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
pip install -e '.[all,testing]'
###ACTION_DELIMITER###
pytest --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y fontconfig
###ACTION_DELIMITER###
pytest --version
###ACTION_DELIMITER###
pip install pydantic==1.10.12
###ACTION_DELIMITER###
pytest --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgles2-mesa
###ACTION_DELIMITER###
apt-get update && apt-get install -y libegl1-mesa libgl1-mesa-dri
###ACTION_DELIMITER###
pytest --version
###ACTION_DELIMITER###
pip install numpy==1.26.4
###ACTION_DELIMITER###
pytest -p no:napari --version
###ACTION_DELIMITER###
echo 'pytest -v -p no:napari --no-header -rA --tb=no -p no:cacheprovider --ignore tools' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libglib2.0-0
###ACTION_DELIMITER###
apt-get update && apt-get install -y libqt5core5a libqt5gui5 libqt5widgets5 libqt5svg5
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
apt-get update && apt-get install -y xvfb
###ACTION_DELIMITER###
echo 'xvfb-run pytest -v -p no:napari --no-header -rA --tb=no -p no:cacheprovider --ignore tools' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run pytest -v --maxfail=0 -p no:napari --no-header -rA --tb=no -p no:cacheprovider --ignore tools' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
xvfb-run pytest -v --maxfail=0 -p no:napari --no-header -rA --tb=no -p no:cacheprovider --ignore tools

""".replace("[[REPO_NAME]]", repo_name),
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
xvfb-run pytest -v --maxfail=0 -p no:napari --no-header -rA --tb=no -p no:cacheprovider --ignore tools

""".replace("[[REPO_NAME]]", repo_name),
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
xvfb-run pytest -v --maxfail=0 -p no:napari --no-header -rA --tb=no -p no:cacheprovider --ignore tools

""".replace("[[REPO_NAME]]", repo_name),
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
RUN git clone https://github.com/napari/napari.git /home/napari

WORKDIR /home/napari
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("napari", "napari_2913_to_2054")
class NAPARI_2913_TO_2054(Instance):
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

        return "bash /home/run.sh"

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

        # Compile regex patterns for test cases, including ERROR
        pattern1 = re.compile(r"^(.+?)\s+(PASSED|FAILED|SKIPPED|ERROR)\s+\[.*\]$")
        pattern2 = re.compile(r"^(PASSED|FAILED|SKIPPED|ERROR)\s+(.+)$")
        # Split log into lines and process each line
        for line in log.split("\n"):
            line = line.strip()
            match1 = pattern1.match(line)
            match2 = pattern2.match(line)
            if match1:
                test_name = match1.group(1)
                status = match1.group(2)
            elif match2:
                status = match2.group(1)
                test_name = match2.group(2)
            else:
                continue  # Skip lines that don't match
            # Add test to the appropriate set
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status == "FAILED":
                failed_tests.add(test_name)
            elif status == "SKIPPED":
                skipped_tests.add(test_name)
            elif status == "ERROR":
                failed_tests.add(test_name)
        parsed_results = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
        }

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
