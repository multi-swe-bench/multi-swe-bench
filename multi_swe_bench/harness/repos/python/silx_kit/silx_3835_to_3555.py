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
                """apt-get update && apt-get install -y build-essential xvfb libqt5gui5 libqt5widgets5 libqt5opengl5 libxkbcommon-x11-0 mesa-utils
###ACTION_DELIMITER###
pip install cython
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
sed -i 's/(int, long)/(int, int)/g' src/silx/io/specfile.pyx
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo 'QT_QPA_PLATFORM=offscreen LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -s "-screen 0 1024x768x24 -ac -noreset" pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run -s "-screen 0 1024x768x24 -ac -noreset" sh -c "QT_QPA_PLATFORM=offscreen LIBGL_ALWAYS_SOFTWARE=1 QT_XCB_GL_INTEGRATION=none pytest -v --no-header -rA --tb=short -p no:cacheprovider"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run -s "-screen 0 1024x768x24 -ac -noreset" sh -c "QT_QPA_PLATFORM=offscreen LIBGL_ALWAYS_SOFTWARE=1 QT_XCB_GL_INTEGRATION=none pytest -v --no-header -rA --tb=short -p no:cacheprovider"' > test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run -s "-screen 0 1024x768x24 -ac -noreset" sh -c "export QT_QPA_PLATFORM=offscreen; export LIBGL_ALWAYS_SOFTWARE=1; export QT_XCB_GL_INTEGRATION=none; pytest -v --no-header -rA --tb=short -p no:cacheprovider -p no:xvfb"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libqt5x11extras5 libqt5svg5
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.26.4 && echo 'xvfb-run -s "-screen 0 1024x768x24 -ac -noreset" sh -c "QT_QPA_PLATFORM=offscreen LIBGL_ALWAYS_SOFTWARE=1 QT_XCB_GL_INTEGRATION=none python run_tests.py -v"' > test_commands.sh
###ACTION_DELIMITER###
pip install numpy>=2.0.2 && echo 'xvfb-run -s "-screen 0 1024x768x24 -ac -noreset" sh -c "QT_QPA_PLATFORM=offscreen LIBGL_ALWAYS_SOFTWARE=1 QT_XCB_GL_INTEGRATION=none pytest -v --no-header -rA --tb=short -p no:cacheprovider"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
xvfb-run -s "-screen 0 1024x768x24 -ac -noreset" sh -c "QT_QPA_PLATFORM=offscreen LIBGL_ALWAYS_SOFTWARE=1 QT_XCB_GL_INTEGRATION=none pytest -v --no-header -rA --tb=short -p no:cacheprovider"

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
xvfb-run -s "-screen 0 1024x768x24 -ac -noreset" sh -c "QT_QPA_PLATFORM=offscreen LIBGL_ALWAYS_SOFTWARE=1 QT_XCB_GL_INTEGRATION=none pytest -v --no-header -rA --tb=short -p no:cacheprovider"

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
xvfb-run -s "-screen 0 1024x768x24 -ac -noreset" sh -c "QT_QPA_PLATFORM=offscreen LIBGL_ALWAYS_SOFTWARE=1 QT_XCB_GL_INTEGRATION=none pytest -v --no-header -rA --tb=short -p no:cacheprovider"

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
RUN git clone https://github.com/silx-kit/silx.git /home/silx

WORKDIR /home/silx
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("silx-kit", "silx_3835_to_3555")
class SILX_3835_TO_3555(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re

        # Regex patterns to match test statuses and names
        # Capture test names using groups
        passed_pattern = re.compile(r"(src/.*?\.py::.*?)\s+PASSED", re.IGNORECASE)
        failed_pattern = re.compile(r"FAILED\s+(src/.*?\.py::.*)", re.IGNORECASE)
        skipped_pattern = re.compile(r"SKIPPED.*?(\S+\.py::?\S*)", re.IGNORECASE)
        # Track test statuses
        test_status = {}
        # Process PASSED tests
        for test_name in passed_pattern.findall(log):
            test_status[test_name] = "PASSED"
        # Process FAILED tests
        for test_name in failed_pattern.findall(log):
            test_status[test_name] = "FAILED"
        # Process SKIPPED tests
        for test_name in skipped_pattern.findall(log):
            test_status[test_name] = "SKIPPED"
        # Populate the sets based on the final status
        for test_name, status in test_status.items():
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status == "FAILED":
                failed_tests.add(test_name)
            elif status == "SKIPPED":
                skipped_tests.add(test_name)
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
