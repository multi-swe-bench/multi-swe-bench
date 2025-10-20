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
        return "python:3.12-slim"
    
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
                """ls -la
###ACTION_DELIMITER###
apt-get update && apt-get install -y git-lfs python3-dev
###ACTION_DELIMITER###
git submodule update --init --recursive
###ACTION_DELIMITER###
pip install --editable .
###ACTION_DELIMITER###
pip install ".[dev]"
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip install ".[dev]"
###ACTION_DELIMITER###
echo 'pytest --no-header -v -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install PyQt5
###ACTION_DELIMITER###
pip install --upgrade qtpy
###ACTION_DELIMITER###
apt-get update && apt-get install -y xvfb
###ACTION_DELIMITER###
echo 'xvfb-run -a pytest --no-header -v -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export QT_QPA_PLATFORM=offscreen
xvfb-run -a pytest --no-header -v -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libqt5core5a libqt5widgets5 libqt5gui5
###ACTION_DELIMITER###
echo -e 'export QT_API=pyqt5
export QT_QPA_PLATFORM=offscreen
xvfb-run -a pytest --no-header -v -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'export QT_API=pyqt5
export QT_QPA_PLATFORM=offscreen
xvfb-run -a pytest --no-header -v -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export QT_API=pyqt5
export QT_QPA_PLATFORM=offscreen
pytest --no-header -v -rA --tb=no -p no:cacheprovider -n auto tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export QT_API=pyqt5
export QT_QPA_PLATFORM=offscreen
xvfb-run -a pytest --no-header -v -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export QT_API=pyqt5
export QT_QPA_PLATFORM=offscreen
xvfb-run -a pytest --no-header -v -rA --tb=no -p no:cacheprovider -n 2 tests/' > test_commands.sh
###ACTION_DELIMITER###
ls -la ci
###ACTION_DELIMITER###
echo -e 'export QT_API=pyqt5
export QT_QPA_PLATFORM=offscreen
mkdir -p build && cd build && cmake ../src/clib -DCMAKE_BUILD_TYPE=Debug && make -j$(nproc) && ctest -j$(nproc) -E Lint --output-on-failure' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y cmake
###ACTION_DELIMITER###
pip install -U pip wheel setuptools cmake pybind11 'conan<2' resdata
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
export QT_API=pyqt5
export QT_QPA_PLATFORM=offscreen
mkdir -p build && cd build && cmake ../src/clib -DCMAKE_BUILD_TYPE=Debug && make -j$(nproc) && ctest -j$(nproc) -E Lint --output-on-failure

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
export QT_API=pyqt5
export QT_QPA_PLATFORM=offscreen
mkdir -p build && cd build && cmake ../src/clib -DCMAKE_BUILD_TYPE=Debug && make -j$(nproc) && ctest -j$(nproc) -E Lint --output-on-failure

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
export QT_API=pyqt5
export QT_QPA_PLATFORM=offscreen
mkdir -p build && cd build && cmake ../src/clib -DCMAKE_BUILD_TYPE=Debug && make -j$(nproc) && ctest -j$(nproc) -E Lint --output-on-failure

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

# Choose an appropriate base image based on the project's requirements - replace python:3.12-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.12-slim

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
RUN git clone https://github.com/equinor/ert.git /home/ert

WORKDIR /home/ert
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("equinor", "ert_7562_to_7302")
class ERT_7562_TO_7302(Instance):
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
        # import json  # Not used for this parsing
        # Pattern to match test lines with status (Passed, Failed, Skipped)
        test_line_pattern = re.compile(
            r"Test\s+#\d+: (.*?)\s+\.{2,}\s+(Passed|Failed|Skipped)\b",
            re.IGNORECASE
        )
        # Find all test lines and extract name and status
        test_matches = test_line_pattern.findall(log)
        for test_name, status in test_matches:
            test_name = test_name.strip()
            status = status.strip().upper()
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status == "FAILED":
                failed_tests.add(test_name)
            elif status == "SKIPPED":
                skipped_tests.add(test_name)
        # Pattern to match the failed tests summary section
        failed_summary_pattern = re.compile(
            r"The following tests FAILED:\s*(.*?)\s*(Errors|Total Test time)",
            re.DOTALL | re.IGNORECASE
        )
        failed_summary_match = failed_summary_pattern.search(log)
        if failed_summary_match:
            failed_section = failed_summary_match.group(1)
            # Extract test names from the failed section
            failed_test_pattern = re.compile(r"\d+ - (.*?)\s*\(", re.IGNORECASE)
            failed_tests_in_summary = failed_test_pattern.findall(failed_section)
            for test_name in failed_tests_in_summary:
                test_name = test_name.strip()
                failed_tests.add(test_name)
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
