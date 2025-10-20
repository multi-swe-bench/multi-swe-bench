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
        return "python:3.10-slim"
    
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
                """ls requirements
###ACTION_DELIMITER###
cat requirements/py310.yml
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgeos-dev proj-bin proj-data libproj-dev libnetcdf-dev libhdf5-dev build-essential graphviz
###ACTION_DELIMITER###
pip install 'cartopy>=0.21' 'cf-units>=3.1' 'cftime>=1.5' 'dask-core>=2022.9.0' 'matplotlib-base>=3.5' 'netcdf4' 'numpy>=1.23,!=1.24.3' 'python-xxhash' 'pyproj' 'scipy' 'shapely!=1.8.3'
###ACTION_DELIMITER###
pip install 'cartopy>=0.21' 'cf-units>=3.1' 'cftime>=1.5' 'dask>=2022.9.0' 'matplotlib-base>=3.5' 'netcdf4' 'numpy>=1.23,!=1.24.3' 'xxhash' 'pyproj' 'scipy' 'shapely!=1.8.3'
###ACTION_DELIMITER###
pip install 'cartopy>=0.21' 'cf-units>=3.1' 'cftime>=1.5' 'dask>=2022.9.0' 'matplotlib>=3.5' 'netcdf4' 'numpy>=1.23,!=1.24.3' 'xxhash' 'pyproj' 'scipy' 'shapely!=1.8.3'
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
python tools/generate_std_names.py etc/cf-standard-name-table.xml lib/iris/std_names.py
###ACTION_DELIMITER###
pip install --upgrade setuptools
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
sed -i '36s/description = help or cmd.description/description = help or getattr(cmd, "description", "Custom command")/' setup.py
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install asv-runner distributed filelock 'imagehash>=4.0' pre-commit psutil pytest pytest-cov pytest-xdist requests
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider -n auto lib/iris/tests' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y netcdf-bin
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
which ncgen && ncgen --version
###ACTION_DELIMITER###
ln -s /usr/bin/ncgen /usr/local/bin/ncgen
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v --no-header -rA --tb=no -p no:cacheprovider -n auto lib/iris/tests

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider -n auto lib/iris/tests

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider -n auto lib/iris/tests

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
FROM python:3.10-slim

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
RUN git clone https://github.com/SciTools/iris.git /home/iris

WORKDIR /home/iris
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("SciTools", "iris_5775_to_unknown")
class IRIS_5775_TO_UNKNOWN(Instance):
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
        # Implement the log parsing logic here
        # Pattern to match test status and name
        pattern = r'.*?(PASSED|FAILED|SKIPPED)\s+(lib/iris/tests/[^\r\n]+)'
        matches = re.findall(pattern, log, re.MULTILINE)
        for status, test_name in matches:
            # Clean up the test name by stripping whitespace
            cleaned_test_name = test_name.strip()
            # Add to the corresponding set
            if status == 'PASSED':
                passed_tests.add(cleaned_test_name)
            elif status == 'FAILED':
                failed_tests.add(cleaned_test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(cleaned_test_name)
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
