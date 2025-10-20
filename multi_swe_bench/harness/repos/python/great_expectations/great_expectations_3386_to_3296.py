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
        return "python:3.7-slim"
    
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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y build-essential libssl-dev libffi-dev
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
pip install -r requirements-dev-base.txt
###ACTION_DELIMITER###
pip install freezegun>=0.3.15
###ACTION_DELIMITER###
pip list | grep freezegun
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider ./tests' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest==5.3.5
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install jinja2==3.0.3
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y locales && locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8
###ACTION_DELIMITER###
sed -i 's/^# *en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/ --no-header//' test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/ --tb=no//' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install boto3>=1.9
###ACTION_DELIMITER###
pip list | grep boto3
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|./tests|./tests --no-spark|' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install sqlalchemy
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|--no-spark|--no-spark --no-sqlalchemy|' test_commands.sh
###ACTION_DELIMITER###
sed -i 's|--no-sqlalchemy|--no-sqlalchemy --no-postgresql|' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install requirements-parser nbformat
###ACTION_DELIMITER###
pip install -r requirements-dev-base.txt
###ACTION_DELIMITER###
pip install moto s3fs gcsfs
###ACTION_DELIMITER###
pip install pyarrow openpyxl xlrd
###ACTION_DELIMITER###
pip install azure-identity azure-keyvault-secrets azure-storage-blob google-cloud-secret-manager pypd snapshottest
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install nbconvert
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest-benchmark
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest-benchmark==3.4.1
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v -rA -p no:cacheprovider ./tests --no-spark --no-sqlalchemy --no-postgresql

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
pytest -v -rA -p no:cacheprovider ./tests --no-spark --no-sqlalchemy --no-postgresql

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
pytest -v -rA -p no:cacheprovider ./tests --no-spark --no-sqlalchemy --no-postgresql

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
FROM python:3.7-slim

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
RUN git clone https://github.com/great-expectations/great_expectations.git /home/great_expectations

WORKDIR /home/great_expectations
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("great-expectations", "great_expectations_3386_to_3296")
class GREAT_EXPECTATIONS_3386_TO_3296(Instance):
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
        passed_tests = set[str]() # Tests that passed successfully
        failed_tests = set[str]() # Tests that failed
        skipped_tests = set[str]() # Tests that were skipped
        import re
        import json
        # Implement the log parsing logic here
        pattern = re.compile(r'(PASSED|FAILED|SKIPPED|XFAILED)\s+(tests/.*?\.py::[^\s]+)|(tests/.*?\.py::[^\s]+)\s+(PASSED|FAILED|SKIPPED|XFAILED)')
        for match in pattern.finditer(log):
            status1, test1, test2, status2 = match.groups()
            if status1 and test1:
                status = status1.strip()
                test_name = test1.strip()
            elif test2 and status2:
                status = status2.strip()
                test_name = test2.strip()
            else:
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
