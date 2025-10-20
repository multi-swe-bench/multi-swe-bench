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
                """ls dev
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
add-apt-repository -y ppa:deadsnakes/ppa
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository -y ppa:deadsnakes/ppa
###ACTION_DELIMITER###
apt-get install -y python3.7 python3.7-venv
###ACTION_DELIMITER###
python3.7 -m venv koalas-venv
###ACTION_DELIMITER###
source koalas-venv/bin/activate
###ACTION_DELIMITER###
pip install -e .[spark]
###ACTION_DELIMITER###
pip show pyspark
###ACTION_DELIMITER###
export SPARK_HOME=/home/koalas/koalas-venv/lib/python3.7/site-packages/pyspark
###ACTION_DELIMITER###
echo "./dev/pytest -v" > test_commands.sh
###ACTION_DELIMITER###
echo -e 'source koalas-venv/bin/activate\nexport SPARK_HOME=/home/koalas/koalas-venv/lib/python3.7/site-packages/pyspark\n./dev/pytest -v' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source koalas-venv/bin/activate\nexport SPARK_HOME=/home/koalas/koalas-venv/lib/python3.7/site-packages/pyspark\nsource dev/env_setup.sh\n./dev/pytest -v' > test_commands.sh
###ACTION_DELIMITER###
pip install pyspark==2.4.8
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y openjdk-8-jdk
###ACTION_DELIMITER###
echo -e 'source koalas-venv/bin/activate\nexport JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64\nexport SPARK_HOME=/home/koalas/koalas-venv/lib/python3.7/site-packages/pyspark\nsource dev/env_setup.sh\n./dev/pytest -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
source koalas-venv/bin/activate
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export SPARK_HOME=/home/koalas/koalas-venv/lib/python3.7/site-packages/pyspark
source dev/env_setup.sh
./dev/pytest -v

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
source koalas-venv/bin/activate
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export SPARK_HOME=/home/koalas/koalas-venv/lib/python3.7/site-packages/pyspark
source dev/env_setup.sh
./dev/pytest -v

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
source koalas-venv/bin/activate
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export SPARK_HOME=/home/koalas/koalas-venv/lib/python3.7/site-packages/pyspark
source dev/env_setup.sh
./dev/pytest -v

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
RUN git clone https://github.com/databricks/koalas.git /home/koalas

WORKDIR /home/koalas
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("databricks", "koalas_447_to_264")
class KOALAS_447_TO_264(Instance):
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
        # Pattern for passed tests: e.g., "test_name PASSED [  0%]"
        passed_pattern = re.compile(r'^(.*?)\s+PASSED\s+\[\s*\d+%\]', re.MULTILINE)
        for match in passed_pattern.findall(log):
            test_name = match.strip()
            passed_tests.add(test_name)
        # Patterns for failed tests: either "test_name FAILED [  0%]" or "FAILED test_name"
        failed_pattern1 = re.compile(r'^(.*?)\s+FAILED\s+\[\s*\d+%\]', re.MULTILINE)
        failed_pattern2 = re.compile(r'^FAILED\s+(.*)$', re.MULTILINE)
        for match in failed_pattern1.findall(log) + failed_pattern2.findall(log):
            test_name = match.strip()
            failed_tests.add(test_name)
        # Patterns for skipped tests: either "test_name SKIPPED [  0%]" or "SKIPPED test_name"
        skipped_pattern1 = re.compile(r'^(.*?)\s+SKIPPED\s+\[\s*\d+%\]', re.MULTILINE)
        skipped_pattern2 = re.compile(r'^SKIPPED\s+(.*)$', re.MULTILINE)
        for match in skipped_pattern1.findall(log) + skipped_pattern2.findall(log):
            test_name = match.strip()
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
