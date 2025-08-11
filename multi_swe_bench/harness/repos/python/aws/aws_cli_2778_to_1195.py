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
        return "ubuntu:latest"
    
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
                """python3 --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.8 python3.8-venv python3.8-dev
###ACTION_DELIMITER###
python3.8 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate && python scripts/ci/install
###ACTION_DELIMITER###
sed -i 's/git:\/\/github.com\/boto\/botocore.git/https:\/\/github.com\/boto\/botocore.git/' requirements.txt
###ACTION_DELIMITER###
source venv/bin/activate && python scripts/ci/install
###ACTION_DELIMITER###
sed -i 's/https:\/\/github.com\/boto\/botocore.git/git+https:\/\/github.com\/boto\/botocore.git/' requirements.txt
###ACTION_DELIMITER###
sed -i 's/https:\/\/github.com\/boto\/botocore.git/git+https:\/\/github.com\/boto\/botocore.git/' requirements.txt
###ACTION_DELIMITER###
source venv/bin/activate && python scripts/ci/install
###ACTION_DELIMITER###
sed -i 's/git+git+https:\/\/github.com\/boto\/botocore.git/git+https:\/\/github.com\/boto\/botocore.git/' requirements.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip install --upgrade pip && python scripts/ci/install
###ACTION_DELIMITER###
sed -i 's/git+git:\/\/github.com\/boto\/s3transfer.git/git+https:\/\/github.com\/boto\/s3transfer.git/' requirements.txt
###ACTION_DELIMITER###
sed -i 's/git:\/\/github.com\/boto\/s3transfer.git/git+https:\/\/github.com\/boto\/s3transfer.git/' requirements.txt
###ACTION_DELIMITER###
sed -i 's/git+git:\/\/github.com\/boto\/s3transfer.git/git+https:\/\/github.com\/boto\/s3transfer.git/' requirements.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip install --upgrade pip && python scripts/ci/install
###ACTION_DELIMITER###
sed -i 's/git+git:\/\/github.com\/boto\/jmespath.git/git+https:\/\/github.com\/boto\/jmespath.git/' requirements.txt
###ACTION_DELIMITER###
sed -i 's/git:\/\/github.com\/boto\/jmespath.git/git+https:\/\/github.com\/boto\/jmespath.git/' requirements.txt
###ACTION_DELIMITER###
sed -i 's/git+git:\/\/github.com\/boto\/jmespath.git/git+https:\/\/github.com\/boto\/jmespath.git/' requirements.txt
###ACTION_DELIMITER###
grep 'github.com/boto' requirements.txt
###ACTION_DELIMITER###
source venv/bin/activate && python scripts/ci/install
###ACTION_DELIMITER###
apt-get install -y python3.8-distutils
###ACTION_DELIMITER###
source venv/bin/activate && pip install docutils
###ACTION_DELIMITER###
source venv/bin/activate && python scripts/ci/install
###ACTION_DELIMITER###
apt-get install -y python3.9 python3.9-venv python3.9-dev
###ACTION_DELIMITER###
python3.9 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate && python scripts/ci/install
###ACTION_DELIMITER###
source venv/bin/activate && pip install --upgrade setuptools wheel
###ACTION_DELIMITER###
source venv/bin/activate && python scripts/ci/install
###ACTION_DELIMITER###
sed -i 's/wheel==0.24.0/wheel>=0.37.0/' requirements.txt
###ACTION_DELIMITER###
source venv/bin/activate && python scripts/ci/install
###ACTION_DELIMITER###
source venv/bin/activate && python --version
###ACTION_DELIMITER###
deactivate && rm -rf venv && python3.9 -m venv venv && source venv/bin/activate && python --version
###ACTION_DELIMITER###
source venv/bin/activate && pip install setuptools==44.0.0 && python scripts/ci/install
###ACTION_DELIMITER###
echo 'venv/bin/nosetests -v tests/unit tests/functional' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install pytest pytest-nose && echo 'venv/bin/pytest -v --nosecompat tests/unit tests/functional' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'venv/bin/nosetests -v tests/unit tests/functional' > test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
venv/bin/nosetests -v tests/unit tests/functional

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
venv/bin/nosetests -v tests/unit tests/functional

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
venv/bin/nosetests -v tests/unit tests/functional

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:latest with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:latest

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
RUN git clone https://github.com/aws/aws-cli.git /home/aws-cli

WORKDIR /home/aws-cli
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("aws", "aws_cli_2778_to_1195")
class AWS_CLI_2778_TO_1195(Instance):
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
        # Split log into lines and process each line
        lines = log.split('\n')
        for line in lines:
            line = line.strip()
            if re.search(r'\.\.\.|\u2026', line):
                # Split into test part (before '...') and status part (after '...')
                test_part, status_part = re.split(r'\.\.\.|\u2026', line, 1)
                # Extract test name (remove [number] prefix)
                test_name = re.sub(r'^.*?\[\s*\d+\s*\]\s*', '', test_part).strip()
                # Extract status (take first word after '...')
                status = status_part.strip().split()[0].lower() if status_part.strip() else ''
                # Map status to category
                if status in ('ok', 'passed', '√'):
                    passed_tests.add(test_name)
                elif status in ('fail', 'failed', 'error', 'x', 'exception'):
                    failed_tests.add(test_name)
                elif status in ('skip', 'skipped', 'xfail'):
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
