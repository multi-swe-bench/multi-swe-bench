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

    def dependency(self) -> Image | None:
        return "python:3.7"
    
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
                """ls -F
###ACTION_DELIMITER###
pip install -r requirements.txt -r requirements-dev.txt
###ACTION_DELIMITER###
BOTO_CONFIG=/dev/null AWS_SECRET_ACCESS_KEY=foobar_secret AWS_ACCESS_KEY_ID=foobar_key AWS_DEFAULT_REGION=us-east-1 pytest -v
###ACTION_DELIMITER###
ls -F tests/
###ACTION_DELIMITER###
ls -F moto/
###ACTION_DELIMITER###
pip install -r requirements.txt -r requirements-dev.txt -r requirements-tests.txt
###ACTION_DELIMITER###
python setup.py test
###ACTION_DELIMITER###
ls -F moto/core/
###ACTION_DELIMITER###
MOTO_S3_CUSTOM_ENDPOINTS=http://s3.acme.com,https://s3.acme.com:5000 AWS_DEFAULT_REGION=us-east-1 pytest -v
###ACTION_DELIMITER###
echo 'BOTO_CONFIG=/dev/null AWS_SECRET_ACCESS_KEY=foobar_secret AWS_ACCESS_KEY_ID=foobar_key AWS_DEFAULT_REGION=us-east-1 pytest --no-header -rA --tb=no -p no:cacheprovider' > /home/moto/test_commands.sh
###ACTION_DELIMITER###
pip install boto3==1.20.0 botocore==1.23.0
###ACTION_DELIMITER###
BOTO_CONFIG=/dev/null AWS_SECRET_ACCESS_KEY=foobar_secret AWS_ACCESS_KEY_ID=foobar_key AWS_DEFAULT_REGION=us-east-1 pytest -v
###ACTION_DELIMITER###

###ACTION_DELIMITER###
pip install responses==0.10.15
###ACTION_DELIMITER###

###ACTION_DELIMITER###
BOTO_CONFIG=/dev/null AWS_SECRET_ACCESS_KEY=foobar_secret AWS_ACCESS_KEY_ID=foobar_key AWS_DEFAULT_REGION=us-east-1 pytest -v
###ACTION_DELIMITER###

###ACTION_DELIMITER###
pip install --upgrade boto3 botocore && pip install -r requirements-dev.txt -r requirements-tests.txt
###ACTION_DELIMITER###
BOTO_CONFIG=/dev/null AWS_SECRET_ACCESS_KEY=foobar_secret AWS_ACCESS_KEY_ID=foobar_key AWS_DEFAULT_REGION=us-east-1 pytest -v --ignore=tests/test_emr/
###ACTION_DELIMITER###
ls -F
###ACTION_DELIMITER###
echo 'pip install boto3==1.20.0 botocore==1.23.0 && pip install responses==0.10.15 && BOTO_CONFIG=/dev/null AWS_SECRET_ACCESS_KEY=foobar_secret AWS_ACCESS_KEY_ID=foobar_key AWS_DEFAULT_REGION=us-east-1 pytest --no-header -rA --tb=no -p no:cacheprovider --ignore=tests/test_emr/' > /home/moto/test_commands.sh
###ACTION_DELIMITER###
pip install -r requirements.txt -r requirements-dev.txt -r requirements-tests.txt"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pip install boto3==1.20.0 botocore==1.23.0 && pip install responses==0.10.15 && BOTO_CONFIG=/dev/null AWS_SECRET_ACCESS_KEY=foobar_secret AWS_ACCESS_KEY_ID=foobar_key AWS_DEFAULT_REGION=us-east-1 pytest --no-header -rA --tb=no -p no:cacheprovider --ignore=tests/test_emr/

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
pip install boto3==1.20.0 botocore==1.23.0 && pip install responses==0.10.15 && BOTO_CONFIG=/dev/null AWS_SECRET_ACCESS_KEY=foobar_secret AWS_ACCESS_KEY_ID=foobar_key AWS_DEFAULT_REGION=us-east-1 pytest --no-header -rA --tb=no -p no:cacheprovider --ignore=tests/test_emr/

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
pip install boto3==1.20.0 botocore==1.23.0 && pip install responses==0.10.15 && BOTO_CONFIG=/dev/null AWS_SECRET_ACCESS_KEY=foobar_secret AWS_ACCESS_KEY_ID=foobar_key AWS_DEFAULT_REGION=us-east-1 pytest --no-header -rA --tb=no -p no:cacheprovider --ignore=tests/test_emr/

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
FROM python:3.7

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
RUN git clone https://github.com/getmoto/moto.git /home/moto

WORKDIR /home/moto
RUN git reset --hard
RUN git checkout 230e34748fab26b58b5ce4311fa5b2f93f6f1da1

RUN git checkout {pr.base.sha}"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("getmoto", "moto_2_2_9")
class MOTO_2_2_9(Instance):
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
        import json
        # TODO: Implement the parse_log function
        for line in log.splitlines():
            if "PASSED" in line:
                match = re.search(r".*(tests/.*)", line)
                if match:
                    passed_tests.add(match.group(1))
            elif "FAILED" in line:
                match = re.search(r".*(tests/.*)", line)
                if match:
                    failed_tests.add(match.group(1))
            elif "SKIPPED" in line:
                match = re.search(r".*(tests/.*)", line)
                if match:
                    skipped_tests.add(match.group(1))
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
