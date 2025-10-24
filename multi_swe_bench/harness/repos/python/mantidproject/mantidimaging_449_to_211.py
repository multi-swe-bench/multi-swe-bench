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
                """ls -la
###ACTION_DELIMITER###
which conda
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
###ACTION_DELIMITER###
bash Miniconda3-latest-Linux-x86_64.sh -b -p /miniconda
###ACTION_DELIMITER###
source /miniconda/etc/profile.d/conda.sh
###ACTION_DELIMITER###
conda --version
###ACTION_DELIMITER###
make install-conda-env
###ACTION_DELIMITER###
apt-get install -y make
###ACTION_DELIMITER###
make install-conda-env
###ACTION_DELIMITER###
conda config --prepend channels conda-forge
###ACTION_DELIMITER###
conda config --prepend channels defaults
###ACTION_DELIMITER###
conda create -n mantidimaging -c dtasev mantidimaging python=3.7 -y
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
###ACTION_DELIMITER###
conda create -n mantidimaging -c dtasev mantidimaging python=3.7 -y
###ACTION_DELIMITER###
conda activate mantidimaging
###ACTION_DELIMITER###
pip install -U -r deps/pip-requirements.txt
###ACTION_DELIMITER###
apt-get install -y build-essential
###ACTION_DELIMITER###
pip install -U -r deps/pip-requirements.txt
###ACTION_DELIMITER###
pip install PyQt5==5.15
###ACTION_DELIMITER###
pip install pyqtgraph==0.11
###ACTION_DELIMITER###
nosetests -v
###ACTION_DELIMITER###
pip install nose
###ACTION_DELIMITER###
nosetests -v
###ACTION_DELIMITER###
pip install nose-randomly
###ACTION_DELIMITER###
nosetests -v
###ACTION_DELIMITER###
apt-get install -y libgl1-mesa-glx
###ACTION_DELIMITER###
nosetests -v
###ACTION_DELIMITER###
apt-get install -y libglib2.0-0
###ACTION_DELIMITER###
nosetests -v
###ACTION_DELIMITER###
pip install mock
###ACTION_DELIMITER###
nosetests -v
###ACTION_DELIMITER###
apt-get install -y libxcb-xinerama0
###ACTION_DELIMITER###
apt-get install -y libqt5gui5 libqt5widgets5 libxcb-render-util0 libxcb-image0 libxkbcommon-x11-0
###ACTION_DELIMITER###
export QT_QPA_PLATFORM=offscreen && nosetests -v
###ACTION_DELIMITER###
pip install testfixtures
###ACTION_DELIMITER###
pip install hazelnut
###ACTION_DELIMITER###
export QT_QPA_PLATFORM=offscreen && nosetests -v
###ACTION_DELIMITER###
echo 'export QT_QPA_PLATFORM=offscreen && nosetests -v' > test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
export QT_QPA_PLATFORM=offscreen && nosetests -v

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
export QT_QPA_PLATFORM=offscreen && nosetests -v

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
export QT_QPA_PLATFORM=offscreen && nosetests -v

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
RUN git clone https://github.com/mantidproject/mantidimaging.git /home/mantidimaging

WORKDIR /home/mantidimaging
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("mantidproject", "mantidimaging_449_to_211")
class MANTIDIMAGING_449_TO_211(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re

        # Split log into lines for processing
        lines = log.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # Match test lines starting with #<number> followed by test name
            test_match = re.match(r"^#\d+\s+(.*?)\s+\.\.\.", line)
            if test_match:
                test_name = test_match.group(1).strip()
                status = None
                # Check if status is on the same line
                status_match = re.search(r"\.\.\.\s+(ok|ERROR|SKIP:.*)$", line)
                if status_match:
                    status = status_match.group(1)
                else:
                    # Check subsequent lines for status
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        status_match = re.match(r"^(ok|ERROR|SKIP:.*)$", next_line)
                        if status_match:
                            status = status_match.group(1)
                            i = j  # Skip processed lines
                            break
                        j += 1
                # Categorize test based on status
                if status:
                    if status == "ok":
                        passed_tests.add(test_name)
                    elif status == "ERROR":
                        failed_tests.add(test_name)
                    elif status.startswith("SKIP:"):
                        skipped_tests.add(test_name)
            i += 1
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
