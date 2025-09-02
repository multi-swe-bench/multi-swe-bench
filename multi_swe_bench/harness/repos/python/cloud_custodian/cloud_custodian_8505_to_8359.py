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
                """cat README.md
###ACTION_DELIMITER###
cat pyproject.toml
###ACTION_DELIMITER###
poetry add --group dev vcr-unittest
###ACTION_DELIMITER###
pip install poetry
###ACTION_DELIMITER###
poetry install
###ACTION_DELIMITER###
poetry add --group dev vcr-unittest
###ACTION_DELIMITER###
cat CONTRIBUTING.md
###ACTION_DELIMITER###
ls tools
###ACTION_DELIMITER###
poetry add --group dev vcrpy-unittest
###ACTION_DELIMITER###
poetry add --editable ./tools/c7n_openstack
###ACTION_DELIMITER###
poetry add --editable ./tools/c7n_awscc
###ACTION_DELIMITER###
poetry add --editable ./tools/c7n_azure
###ACTION_DELIMITER###
poetry add --editable ./tools/c7n_gcp
###ACTION_DELIMITER###
echo 'poetry run pytest -v --no-header -rA --tb=native -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
poetry add --editable ./tools/c7n_tencentcloud
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
poetry add --group dev python-hcl2
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
poetry add --group dev azure-functions parameterized
###ACTION_DELIMITER###
poetry add --editable ./tools/c7n_kube
###ACTION_DELIMITER###
poetry add --editable ./tools/c7n_mailer
###ACTION_DELIMITER###
poetry run pip install -e ./tools/c7n_mailer
###ACTION_DELIMITER###
ls tools/c7n_mailer
###ACTION_DELIMITER###
poetry run pip install ./tools/c7n_mailer
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
poetry add --group dev fakeredis
###ACTION_DELIMITER###
poetry add --editable ./tools/c7n_org
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
poetry add --group dev google-cloud-secretmanager
###ACTION_DELIMITER###
poetry add --group dev google-cloud-secret-manager
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/^poetry run pytest.*/poetry run pytest -v --no-header -rA --tb=native -p no:cacheprovider -m "not skiplive" -n auto/' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
poetry add --editable ./tools/c7n_left
###ACTION_DELIMITER###
poetry lock --no-cache --regenerate
###ACTION_DELIMITER###
poetry install
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
poetry run pytest --collect-only -v"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
poetry run pytest -v --no-header -rA --tb=native -p no:cacheprovider -m "not skiplive" -n auto

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
poetry run pytest -v --no-header -rA --tb=native -p no:cacheprovider -m "not skiplive" -n auto

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
poetry run pytest -v --no-header -rA --tb=native -p no:cacheprovider -m "not skiplive" -n auto

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
RUN git clone https://github.com/cloud-custodian/cloud-custodian.git /home/cloud-custodian

WORKDIR /home/cloud-custodian
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("cloud-custodian", "cloud_custodian_8505_to_8359")
class CLOUD_CUSTODIAN_8505_TO_8359(Instance):
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
        # Parse log lines to extract test statuses
        lines = log.split('\n')
        for line in lines:
            line = line.strip()
            if 'FAILED' in line:
                parts = line.split('FAILED ')
                if len(parts) > 1:
                    test_part = parts[1]
                    test_name = test_part.split(' -')[0].strip()
                    failed_tests.add(test_name)
            elif 'PASSED' in line:
                parts = line.split('PASSED ')
                if len(parts) > 1:
                    test_part = parts[1]
                    test_name = test_part.split()[0].strip()
                    passed_tests.add(test_name)
            elif 'SKIPPED' in line:
                parts = line.split('SKIPPED ')
                if len(parts) > 1:
                    test_part = parts[1]
                    test_name = test_part.split()[0].strip()
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
