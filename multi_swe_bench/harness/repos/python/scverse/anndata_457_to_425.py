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
                """ls -l
###ACTION_DELIMITER###
pip install .[test]
###ACTION_DELIMITER###
pip install scikit-learn
###ACTION_DELIMITER###
pip install .[test]
###ACTION_DELIMITER###
SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True pip install .[test]
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.26
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install scikit-learn==0.23.2
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip install scikit-learn==0.23.2
###ACTION_DELIMITER###
pip install numpy==1.19.5 setuptools<60.0.0
###ACTION_DELIMITER###
pip install 'numpy==1.19.5' 'setuptools<60.0.0'
###ACTION_DELIMITER###
pip install scikit-learn==0.23.2
###ACTION_DELIMITER###
pip install --no-build-isolation scikit-learn==0.23.2
###ACTION_DELIMITER###
pip install 'Cython>=0.28.5'
###ACTION_DELIMITER###
pip install --no-build-isolation scikit-learn==0.23.2
###ACTION_DELIMITER###
pip install 'Cython==0.29.21'
###ACTION_DELIMITER###
pip install --no-build-isolation scikit-learn==0.23.2
###ACTION_DELIMITER###
pip install 'scipy==1.5.4'
###ACTION_DELIMITER###
apt-get install -y libopenblas-dev
###ACTION_DELIMITER###
pip install --no-build-isolation scikit-learn==0.23.2
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install 'scanpy==1.8.2'
###ACTION_DELIMITER###
pip install 'umap-learn==0.5.2'
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install 'numpy==1.26.4'
###ACTION_DELIMITER###
sed -i 's/--tb=no//' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install --no-build-isolation 'scikit-learn==0.23.2'
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install 'pandas==1.3.5' && bash test_commands.sh
###ACTION_DELIMITER###
pip install openpyxl
###ACTION_DELIMITER###
pip install 'statsmodels==0.13.5'
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v --no-header -rA  -p no:cacheprovider

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
pytest -v --no-header -rA  -p no:cacheprovider

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
pytest -v --no-header -rA  -p no:cacheprovider

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
RUN git clone https://github.com/scverse/anndata.git /home/anndata

WORKDIR /home/anndata
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("scverse", "anndata_457_to_425")
class ANNDATA_457_TO_425(Instance):
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
        import json  # Included as per skeleton, not used in this implementation
        # Regex patterns to match test result lines
        # Pattern 1: Test name followed by status and percentage (e.g., 'test PASSED [ 0%]')
        pattern1 = re.compile(r'^(.+?)\s+(PASSED|FAILED|SKIPPED)\s+\[\s*\d+%\]$')
        # Pattern 2: Status followed by test name (e.g., 'FAILED test')
        pattern2 = re.compile(r'^(PASSED|FAILED|SKIPPED)\s+(.+)$')
        for line in log.split('\n'):
            line = line.strip()
            match1 = pattern1.match(line)
            if match1:
                test_name = match1.group(1).strip()
                status = match1.group(2)
            else:
                match2 = pattern2.match(line)
                if match2:
                    status = match2.group(1)
                    test_name = match2.group(2).strip()
                else:
                    continue  # Skip non-test lines
            # Categorize test based on status
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
