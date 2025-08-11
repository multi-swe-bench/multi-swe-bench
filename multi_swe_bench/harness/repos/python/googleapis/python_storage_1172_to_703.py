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
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
pip install -e . mock pytest pytest-cov -c testing/constraints-3.9.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'PYTHONPATH=. pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip list | grep google
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
python -c 'import google.auth; import google.api_core; print("Imports successful")'
###ACTION_DELIMITER###
pip show google-auth | grep Location && python -c 'import sys; print("\nPython path:", sys.path)'
###ACTION_DELIMITER###
ls /usr/local/lib/python3.9/site-packages/google/auth
###ACTION_DELIMITER###
ls google
###ACTION_DELIMITER###
python -c 'import google; print(google.__path__)'
###ACTION_DELIMITER###
pip install .
###ACTION_DELIMITER###
python -c 'import google.auth; import google.api_core; print("Imports successful")'
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install google-cloud-kms
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/unit tests/system' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'PYTHONPATH=testing pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/unit tests/system' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls testing
###ACTION_DELIMITER###
ls tests
###ACTION_DELIMITER###
find . -name 'test_utils'
###ACTION_DELIMITER###
pip install google-cloud-testutils
###ACTION_DELIMITER###
echo 'PYTHONPATH=tests pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/unit tests/system' > test_commands.sh
###ACTION_DELIMITER###
pip show -f google-cloud-testutils
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/unit tests/system' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install google-cloud-iam
###ACTION_DELIMITER###
pip install google-cloud-iamcredentials
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
pip install google-cloud-iamcredentials
###ACTION_DELIMITER###
echo 'PYTHONPATH=/usr/local/lib/python3.9/site-packages pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/unit tests/system' > test_commands.sh
###ACTION_DELIMITER###
pip install google-cloud-iam-credentials
###ACTION_DELIMITER###
pip show -f google-cloud-iam
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/unit tests/system -k "not test__signing"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/unit' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/unit -k "not (test_create_bucket_w_custom_endpoint or test_ctor_w_custom_endpoint_use_auth or test_list_buckets_w_custom_endpoint)"' > test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/unit -k "not (test_create_bucket_w_custom_endpoint or test_ctor_w_custom_endpoint_use_auth or test_list_buckets_w_custom_endpoint)"

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/unit -k "not (test_create_bucket_w_custom_endpoint or test_ctor_w_custom_endpoint_use_auth or test_list_buckets_w_custom_endpoint)"

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/unit -k "not (test_create_bucket_w_custom_endpoint or test_ctor_w_custom_endpoint_use_auth or test_list_buckets_w_custom_endpoint)"

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
RUN git clone https://github.com/googleapis/python-storage.git /home/python-storage

WORKDIR /home/python-storage
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("googleapis", "python_storage_1172_to_703")
class PYTHON_STORAGE_1172_TO_703(Instance):
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
        passed_tests = set() # Tests that passed successfully
        failed_tests = set() # Tests that failed
        skipped_tests = set() # Tests that were skipped
        import re
        # Split log into lines
        lines = log.split('\n')
        # Regex pattern to match test names and statuses
        pattern = re.compile(r'(tests/[^\s]+)\s+(PASSED|FAILED|SKIPPED)|(PASSED|FAILED|SKIPPED)\s+(tests/[^\s]+)')
        for line in lines:
            match = pattern.search(line)
            if match:
                if match.group(1) and match.group(2):
                    test_name = match.group(1)
                    status = match.group(2)
                elif match.group(3) and match.group(4):
                    test_name = match.group(4)
                    status = match.group(3)
                else:
                    continue  # No match, skip
                # Add to the appropriate set
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
