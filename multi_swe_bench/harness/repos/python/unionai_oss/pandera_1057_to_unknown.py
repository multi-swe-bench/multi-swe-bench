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
                """apt-get update && apt-get install -y build-essential openjdk-11-jdk
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential default-jdk
###ACTION_DELIMITER###
sed -i 's/numpy >= 1.19.0/numpy >= 1.19.0, < 2.0.0/' requirements-dev.txt
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
sed -i 's/types-pkg_resources/types-setuptools/' requirements-dev.txt
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/default-java
pytest -v -rA tests' > /home/pandera/test_commands.sh && chmod +x /home/pandera/test_commands.sh
###ACTION_DELIMITER###
bash /home/pandera/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/multimethod/multimethod==1.9.1/' requirements-dev.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
bash /home/pandera/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pydantic/pydantic<2/' requirements-dev.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
bash /home/pandera/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/default-java
export PYSPARK_SUBMIT_ARGS="--conf spark.sql.ansi.enabled=false"
pytest -v -rA tests' > /home/pandera/test_commands.sh && chmod +x /home/pandera/test_commands.sh
###ACTION_DELIMITER###
bash /home/pandera/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/default-java
mkdir -p conf
echo "spark.sql.ansi.enabled false" > conf/spark-defaults.conf
export SPARK_CONF_DIR=$(pwd)/conf
pytest -v -rA tests' > /home/pandera/test_commands.sh && chmod +x /home/pandera/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/default-java
export PYSPARK_SUBMIT_ARGS="--conf spark.sql.ansi.enabled=false pyspark-shell"
pytest -v -rA tests' > /home/pandera/test_commands.sh && chmod +x /home/pandera/test_commands.sh
###ACTION_DELIMITER###
bash /home/pandera/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/default-java
export PYSPARK_SUBMIT_ARGS="--conf spark.sql.ansi.enabled=false pyspark-shell"
pytest -v -rA tests/core' > /home/pandera/test_commands.sh && chmod +x /home/pandera/test_commands.sh
###ACTION_DELIMITER###
bash /home/pandera/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pandas>=1.2.0/pandas==1.5.0/' requirements-dev.txt && pip install -r requirements-dev.txt --force-reinstall
###ACTION_DELIMITER###
sed -i 's/pandas>=2.0.0/pandas==1.5.0/' requirements-dev.txt && pip install -r requirements-dev.txt --force-reinstall
###ACTION_DELIMITER###
sed -i 's/pandas>=1.2.0/pandas==1.5.0/' requirements-dev.txt && pip install -r requirements-dev.txt --force-reinstall
###ACTION_DELIMITER###
sed -i 's/pandas >= 1.2.0/pandas == 1.5.0/' requirements-dev.txt && pip install -r requirements-dev.txt --force-reinstall
###ACTION_DELIMITER###
bash /home/pandera/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/default-java
export PYSPARK_SUBMIT_ARGS="--conf spark.sql.ansi.enabled=false pyspark-shell"
pytest -v -rA tests/core

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
#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/default-java
export PYSPARK_SUBMIT_ARGS="--conf spark.sql.ansi.enabled=false pyspark-shell"
pytest -v -rA tests/core

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
#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/default-java
export PYSPARK_SUBMIT_ARGS="--conf spark.sql.ansi.enabled=false pyspark-shell"
pytest -v -rA tests/core

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
RUN git clone https://github.com/unionai-oss/pandera.git /home/pandera

WORKDIR /home/pandera
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("unionai-oss", "pandera_1057_to_unknown")
class PANDERA_1057_TO_UNKNOWN(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        # Define regex patterns for each status
        passed_re = re.compile(r'(?:PASSED\s+(\S+)|(\S+)\s+PASSED)')
        failed_re = re.compile(r'FAILED\s+(\S+)')
        error_re = re.compile(r'ERROR\s+(\S+)')
        skipped_re = re.compile(r'SKIPPED\s+\[\d+\]\s+.*?:\s*([^\s]+)')
        # Split log into lines
        lines = log.split('\n')
        for line in lines:
            # Check for passed tests
            passed_match = passed_re.search(line)
            if passed_match:
                test_name = passed_match.group(1) or passed_match.group(2)
                passed_tests.add(test_name)
            # Check for failed tests
            failed_match = failed_re.search(line)
            if failed_match:
                test_name = failed_match.group(1)
                failed_tests.add(test_name)
            # Check for error tests (treat as failed)
            error_match = error_re.search(line)
            if error_match:
                test_name = error_match.group(1)
                failed_tests.add(test_name)
            # Check for skipped tests
            skipped_match = skipped_re.search(line)
            if skipped_match:
                test_name = skipped_match.group(1)
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
