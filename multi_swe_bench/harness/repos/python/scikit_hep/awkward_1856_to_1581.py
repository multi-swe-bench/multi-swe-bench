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
        return "python:3.9-slim-bullseye"
    
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
apt-get update && apt-get install -y build-essential cmake make
###ACTION_DELIMITER###
pip install .[test,dev]
###ACTION_DELIMITER###
git submodule update --init --recursive
###ACTION_DELIMITER###
pip install .[test,dev]
###ACTION_DELIMITER###
apt-get install -y python3-dev
###ACTION_DELIMITER###
/tmp/pip-build-env-pig424ql/overlay/lib/python3.9/site-packages/cmake/data/bin/cmake -S /home/awkward -B build/temp.linux-x86_64-cpython-39 -DCMAKE_LIBRARY_OUTPUT_DIRECTORY=/home/awkward/build/lib.linux-x86_64-cpython-39/ -DPYTHON_EXECUTABLE=/usr/local/bin/python3.9 -DEXAMPLE_VERSION_INFO=2.0.0rc2 -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/home/awkward/build/lib.linux-x86_64-cpython-39/ -DPYTHON_EXECUTABLE=/usr/local/bin/python3.9 -DPYBUILD=ON -DBUILD_TESTING=OFF -DCMAKE_CXX_COMPILER=g++
###ACTION_DELIMITER###
cmake --version
###ACTION_DELIMITER###
python localbuild.py --pytest tests
###ACTION_DELIMITER###
pip list | grep numpy
###ACTION_DELIMITER###
pip install numpy==1.26.4
###ACTION_DELIMITER###
python localbuild.py --pytest tests
###ACTION_DELIMITER###
echo 'python localbuild.py --pytest tests' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python localbuild.py --pytest tests

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
python localbuild.py --pytest tests

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
python localbuild.py --pytest tests

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim-bullseye with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.9-slim-bullseye

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
RUN git clone https://github.com/scikit-hep/awkward.git /home/awkward

WORKDIR /home/awkward
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("scikit-hep", "awkward_1856_to_1581")
class AWKWARD_1856_TO_1581(Instance):
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
        # Implement the log parsing logic here
        # Pattern for passed tests (captures test name before ' PASSED')
        passed_pattern = re.compile(r"(tests/.*?)\s+PASSED")
        passed_tests.update(passed_pattern.findall(log))
        # Pattern for failed tests: captures 'test_name FAILED' and underlined test names
        failed_pattern1 = re.compile(r"(tests/.*?)\s+FAILED")
        failed_pattern2 = re.compile(r"_{20,}\s+(tests/.*?)\s+_{20,}")  # Underlined failed tests
        failed_tests.update(failed_pattern1.findall(log))
        failed_tests.update(failed_pattern2.findall(log))
        # Pattern for skipped tests: captures 'SKIPPED [1] tests/...' (clean file name)
        skipped_pattern1 = re.compile(r"\[\s*\d+\s*\]\s*SKIPPED\s+\[\d+\]\s+(tests/[^:]+)")  # Stop at first colon to exclude line number/reason
        skipped_tests.update(skipped_pattern1.findall(log))
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
