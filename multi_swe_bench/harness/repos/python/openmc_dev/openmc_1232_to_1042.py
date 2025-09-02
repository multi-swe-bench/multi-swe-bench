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
        return "ubuntu:22.04"
    
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
                """apt-get update && apt-get install -y libopenblas-dev cython3
###ACTION_DELIMITER###
pip install -e .[test]
###ACTION_DELIMITER###
apt-get install -y python3-pip
###ACTION_DELIMITER###
pip install -e .[test]
###ACTION_DELIMITER###
pip install --upgrade cython
###ACTION_DELIMITER###
pip install -e .[test]
###ACTION_DELIMITER###
pip install --upgrade numpy
###ACTION_DELIMITER###
apt-get install -y g++ cmake mpich libhdf5-dev libopenblas-dev
###ACTION_DELIMITER###
mkdir -p build && cd build && cmake .. && make
###ACTION_DELIMITER###
pip install -e .[test]
###ACTION_DELIMITER###
cd ..
###ACTION_DELIMITER###
pip install -e .[test]
###ACTION_DELIMITER###
apt remove -y cython3
###ACTION_DELIMITER###
pip install cython==0.29.36
###ACTION_DELIMITER###
pip install -e .[test]
###ACTION_DELIMITER###
./tools/ci/download-xs.sh
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
./tools/ci/download-xs.sh
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install scipy==1.9.3
###ACTION_DELIMITER###
echo 'export OPENMC_CROSS_SECTIONS=/root/nndc_hdf5/cross_sections.xml
pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'export OPENMC_CROSS_SECTIONS=/root/nndc_hdf5/cross_sections.xml
export OPENMC_ENDF_DATA=/root/endf-b-vii.1/
pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
export OPENMC_CROSS_SECTIONS=/root/nndc_hdf5/cross_sections.xml
export OPENMC_ENDF_DATA=/root/endf-b-vii.1/
pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/

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
export OPENMC_CROSS_SECTIONS=/root/nndc_hdf5/cross_sections.xml
export OPENMC_ENDF_DATA=/root/endf-b-vii.1/
pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/

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
export OPENMC_CROSS_SECTIONS=/root/nndc_hdf5/cross_sections.xml
export OPENMC_ENDF_DATA=/root/endf-b-vii.1/
pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:22.04 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:22.04

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
RUN git clone https://github.com/openmc-dev/openmc.git /home/openmc

WORKDIR /home/openmc
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("openmc-dev", "openmc_1232_to_1042")
class OPENMC_1232_TO_1042(Instance):
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
        # Split log into lines
        lines = log.splitlines()
        # Regex patterns to match test cases
        pattern1 = re.compile(r'(tests/[^ ]+) (PASSED|FAILED|SKIPPED)\b')
        pattern2 = re.compile(r'(PASSED|FAILED|SKIPPED)\b (tests/[^ ]+)')
        for line in lines:
            # Check pattern 1: test name followed by status
            match = pattern1.search(line)
            if match:
                test_name = match.group(1).strip()
                status = match.group(2)
            else:
                # Check pattern 2: status followed by test name
                match = pattern2.search(line)
                if match:
                    status = match.group(1)
                    test_name = match.group(2).strip()
                else:
                    continue  # No match, skip line
            # Add test to the appropriate set
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
