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
ls testing
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install mock pytest pytest-cov
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=short tests/unit/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install six
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from google.cloud import _helpers/from google.cloud.core import _helpers/' google/cloud/storage/batch.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from google.cloud.core import _helpers/from google.api_core import _helpers/' google/cloud/storage/batch.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install google-api-core
###ACTION_DELIMITER###
ls google/cloud/storage/_helpers.py
###ACTION_DELIMITER###
sed -i 's/from google.api_core import _helpers/from google.cloud.storage import _helpers/' google/cloud/storage/batch.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from google import resumable_media/import google.resumable_media/' google/cloud/storage/_helpers.py
###ACTION_DELIMITER###
sed -i 's/from google import resumable_media/import google.resumable_media as resumable_media/' google/cloud/storage/_helpers.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip show -f google-resumable-media
###ACTION_DELIMITER###
pip uninstall -y google-cloud-storage && pip install .
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytz
###ACTION_DELIMITER###
sed -i '1i import google.resumable_media as resumable_media' tests/unit/test_blob.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i '1c from google import resumable_media' tests/unit/test_blob.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
python -c "from google import resumable_media; print('Import successful')"
###ACTION_DELIMITER###
sed -i '/^import /i from google import resumable_media' tests/unit/test_blob.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
head -n 10 tests/unit/test_blob.py"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v --no-header -rA --tb=short tests/unit/

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
pytest -v --no-header -rA --tb=short tests/unit/

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
pytest -v --no-header -rA --tb=short tests/unit/

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

# Choose an appropriate base image based on the project's requirements - replace python:3.10-slim with actual base image
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
RUN git clone https://github.com/googleapis/python-storage.git /home/python-storage

WORKDIR /home/python-storage
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("googleapis", "python_storage_526_to_325")
class PYTHON_STORAGE_526_TO_325(Instance):
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
        import json
        # Implement the log parsing logic here
        # Split log into lines and process each line
        lines = log.split('\n')
        # Regex patterns for test name followed by status or vice versa
        pattern = re.compile(r'.*(tests/[^\s]+)\s+(PASSED|FAILED|SKIPPED)|.*(PASSED|FAILED|SKIPPED)\s+(tests/[^\s]+)')
        for line in lines:
            match = pattern.search(line)
            if not match:
                continue
            # Extract test name and status from either group
            test_name = match.group(1) or match.group(4)
            status = match.group(2) or match.group(3)
            if not test_name or not status:
                continue
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
