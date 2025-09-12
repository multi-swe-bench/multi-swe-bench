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
cat Makefile
###ACTION_DELIMITER###
cat test_requirements.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libopenblas-dev gfortran default-jdk libproj-dev proj-bin libgdal-dev libhdf5-dev libssl-dev libffi-dev python3-dev
###ACTION_DELIMITER###
make install-test-requirements
###ACTION_DELIMITER###
pip install --upgrade pip && pip install numpy==1.23.5 --only-binary numpy
###ACTION_DELIMITER###
make install-test-requirements
###ACTION_DELIMITER###
echo 'numpy==1.23.5' > constraints.txt && pip install -r test_requirements.txt -c constraints.txt
###ACTION_DELIMITER###
pip install -r test_requirements.txt -c constraints.txt --only-binary numpy
###ACTION_DELIMITER###
sed -i 's/pyarrow>=0.12.0, <1.0.0/pyarrow>=0.19.0, <1.0.0/' test_requirements.txt
###ACTION_DELIMITER###
pip install -r test_requirements.txt -c constraints.txt --only-binary numpy
###ACTION_DELIMITER###
sed -i 's/pyarrow>=0.19.0, <1.0.0/pyarrow>=0.12.0, <1.0.0/' test_requirements.txt
###ACTION_DELIMITER###
sed -i 's/pyarrow>=0.12.0, <1.0.0/pyarrow>=3.0.0/' test_requirements.txt
###ACTION_DELIMITER###
pip install -r test_requirements.txt -c constraints.txt --only-binary numpy
###ACTION_DELIMITER###
sed -i 's/pyproj>=2.2.0, <3.0/pyproj>=3.0.0/' test_requirements.txt
###ACTION_DELIMITER###
pip install -r test_requirements.txt -c constraints.txt --only-binary numpy,pyproj
###ACTION_DELIMITER###
echo 'pytest -v tests --cov-config pyproject.toml' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pyarrow>=3.0.0/pyarrow>=0.12.0, <2.0.0/' test_requirements.txt
###ACTION_DELIMITER###
pip install -r test_requirements.txt -c constraints.txt --only-binary numpy,pyarrow
###ACTION_DELIMITER###
sed -i 's/pyarrow>=0.12.0, <2.0.0/pyarrow==0.17.1/' test_requirements.txt && pip install -r test_requirements.txt -c constraints.txt
###ACTION_DELIMITER###
pip install -r test_requirements.txt -c constraints.txt --no-build-isolation
###ACTION_DELIMITER###
pip install Cython && pip install -r test_requirements.txt -c constraints.txt --no-build-isolation
###ACTION_DELIMITER###
sed -i 's/pyarrow==0.17.1/pyarrow==1.0.1/' test_requirements.txt && pip install -r test_requirements.txt -c constraints.txt --no-build-isolation
###ACTION_DELIMITER###
pip install Cython==0.29.21 && sed -i 's/pyarrow==1.0.1/pyarrow==0.17.1/' test_requirements.txt && pip install -r test_requirements.txt -c constraints.txt --no-build-isolation
###ACTION_DELIMITER###
sed -i 's/pyarrow==0.17.1/pyarrow==1.0.0/' test_requirements.txt && pip install -r test_requirements.txt -c constraints.txt --no-build-isolation
###ACTION_DELIMITER###
sed -i 's/pyarrow==1.0.0/pyarrow==1.0.1/' test_requirements.txt && pip install -r test_requirements.txt -c constraints.txt --only-binary pyarrow
###ACTION_DELIMITER###
sed -i 's/fsspec<0.7.0,>=0.5.1/fsspec>=0.7.0/' requirements.txt && sed -i 's/pyarrow==1.0.1/pyarrow>=2.0.0/' test_requirements.txt && pip install -r test_requirements.txt -c constraints.txt --only-binary pyarrow
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pandas==1.5.3
pyarrow==1.0.1' > constraints.txt && sed -i 's/pandas>=0.24.0/pandas>=0.24.0, <2.0.0/' test_requirements.txt && sed -i 's/pyarrow>=2.0.0/pyarrow==1.0.1/' test_requirements.txt && pip install -r test_requirements.txt -c constraints.txt --only-binary pyarrow,pandas
###ACTION_DELIMITER###
pip install -r test_requirements.txt -c constraints.txt --no-build-isolation
###ACTION_DELIMITER###
pip cache purge && pip install pyarrow==1.0.1 --no-build-isolation --no-deps && pip install -r test_requirements.txt -c constraints.txt --no-build-isolation
###ACTION_DELIMITER###
echo 'pandas==1.5.3
pyarrow==2.0.0' > constraints.txt && sed -i 's/pyarrow==1.0.1/pyarrow==2.0.0/' test_requirements.txt && pip install -r test_requirements.txt -c constraints.txt --only-binary pyarrow,pandas
###ACTION_DELIMITER###
pip install pyarrow==0.17.1 --no-deps --no-build-isolation && pip install pandas==1.5.3 && pip install -r test_requirements.txt -c constraints.txt --no-build-isolation
###ACTION_DELIMITER###
echo 'pandas==1.5.3
pyarrow==3.0.0' > constraints.txt && sed -i 's/pyarrow==0.17.1/pyarrow==3.0.0/' test_requirements.txt && pip install -r test_requirements.txt -c constraints.txt --only-binary pyarrow,pandas
###ACTION_DELIMITER###
sed -i 's/pyarrow==2.0.0/pyarrow==3.0.0/' test_requirements.txt && echo 'pandas==1.5.3
pyarrow==3.0.0' > constraints.txt && pip install -r test_requirements.txt -c constraints.txt --only-binary pyarrow,pandas
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pyspark~=2.2; python_version < "3.8"/pyspark~=3.3/' test_requirements.txt && pip install -r test_requirements.txt -c constraints.txt --only-binary pyspark
###ACTION_DELIMITER###
sed -i 's/pyspark~=2.2; python_version < "3.8"/pyspark~=3.3.0/' test_requirements.txt && pip install pyspark~=3.3.0 && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v tests --cov-config pyproject.toml

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
pytest -v tests --cov-config pyproject.toml

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
pytest -v tests --cov-config pyproject.toml

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
RUN git clone https://github.com/kedro-org/kedro.git /home/kedro

WORKDIR /home/kedro
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("kedro-org", "kedro_578_to_190")
class KEDRO_578_TO_190(Instance):
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
        # Pattern for passed tests: test name followed by PASSED and [ percentage ]
        passed_pattern = re.compile(r'^(.*?)\s+PASSED\s+\[\s*\d+%\]$', re.MULTILINE)
        passed_matches = passed_pattern.findall(log)
        for test in passed_matches:
            passed_tests.add(test.strip())
        # Pattern for failed tests: FAILED followed by test name
        failed_pattern = re.compile(r'^FAILED\s+(.*?)$', re.MULTILINE)
        failed_matches = failed_pattern.findall(log)
        for test in failed_matches:
            failed_tests.add(test.strip())
        # Check for skipped tests in both formats
        skipped_pattern1 = re.compile(r'^(.*?)\s+SKIPPED\s+\[\s*\d+%\]$', re.MULTILINE)
        skipped_matches1 = skipped_pattern1.findall(log)
        for test in skipped_matches1:
            skipped_tests.add(test.strip())
        skipped_pattern2 = re.compile(r'^SKIPPED\s+(.*?)$', re.MULTILINE)
        skipped_matches2 = skipped_pattern2.findall(log)
        for test in skipped_matches2:
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
