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
                """cat Makefile
###ACTION_DELIMITER###
cat setup.py
###ACTION_DELIMITER###
cat pyproject.toml
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-11-jre-headless && export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
###ACTION_DELIMITER###
apt-cache search openjdk
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-17-jre-headless && export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
###ACTION_DELIMITER###
make installdeps
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make installdeps
###ACTION_DELIMITER###
echo -e 'export PYARROW_IGNORE_TIMEZONE=1\nexport JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64\npytest -v -n auto woodwork/' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.26.4
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip show pyspark && ls -ld /usr/lib/jvm/java-17-openjdk-amd64
###ACTION_DELIMITER###
echo -e 'from pyspark.sql import SparkSession\nspark = SparkSession.builder.master("local[*]").getOrCreate()\ndf = spark.createDataFrame([(1, "test")])\ndf.show()\nspark.stop()' > test_spark.py && python test_spark.py
###ACTION_DELIMITER###
echo -e 'from pyspark.sql import SparkSession\nspark = SparkSession.builder.master("local[*]")\n    .config("spark.driver.extraJavaOptions", "--add-exports=java.base/sun.nio.ch=ALL-UNNAMED")\n    .config("spark.executor.extraJavaOptions", "--add-exports=java.base/sun.nio.ch=ALL-UNNAMED")\n    .getOrCreate()\ndf = spark.createDataFrame([(1, "test")])\ndf.show()\nspark.stop()' > test_spark.py && python test_spark.py
###ACTION_DELIMITER###
echo -e 'from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[*]")\
    .config("spark.driver.extraJavaOptions", "--add-exports=java.base/sun.nio.ch=ALL-UNNAMED")\
    .config("spark.executor.extraJavaOptions", "--add-exports=java.base/sun.nio.ch=ALL-UNNAMED")\
    .getOrCreate()
df = spark.createDataFrame([(1, "test")])
df.show()
spark.stop()' > test_spark.py && python test_spark.py
###ACTION_DELIMITER###
echo -e 'export PYARROW_IGNORE_TIMEZONE=1\nexport JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64\nexport SPARK_DRIVER_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED"\nexport SPARK_EXECUTOR_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED"\npytest -v -n auto woodwork/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYARROW_IGNORE_TIMEZONE=1\nexport JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64\nexport PYSPARK_SUBMIT_ARGS="--conf spark.driver.extraJavaOptions=--add-exports=java.base/sun.nio.ch=ALL-UNNAMED --conf spark.executor.extraJavaOptions=--add-exports=java.base/sun.nio.ch=ALL-UNNAMED pyspark-shell"\npytest -v -n auto woodwork/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
mkdir -p /usr/local/lib/python3.9/site-packages/pyspark/conf && echo -e 'spark.driver.extraJavaOptions --add-exports=java.base/sun.nio.ch=ALL-UNNAMED
spark.executor.extraJavaOptions --add-exports=java.base/sun.nio.ch=ALL-UNNAMED' > /usr/local/lib/python3.9/site-packages/pyspark/conf/spark-defaults.conf
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y procps && echo -e 'export PYARROW_IGNORE_TIMEZONE=1\nexport JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64\nexport SPARK_OPTS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED"\npytest -v -n auto woodwork/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYARROW_IGNORE_TIMEZONE=1\nexport JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64\nexport SPARK_DRIVER_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED"\nexport SPARK_EXECUTOR_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED"\npytest -v -n auto woodwork/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
mkdir -p /usr/local/lib/python3.9/site-packages/pyspark/conf && echo -e 'spark.driver.extraJavaOptions --add-exports=java.base/sun.nio.ch=ALL-UNNAMED
spark.executor.extraJavaOptions --add-exports=java.base/sun.nio.ch=ALL-UNNAMED' > /usr/local/lib/python3.9/site-packages/pyspark/conf/spark-defaults.conf && cat /usr/local/lib/python3.9/site-packages/pyspark/conf/spark-defaults.conf && bash test_commands.sh
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian oldstable main' >> /etc/apt/sources.list && apt-get update && apt-get install -y openjdk-11-jre-headless && export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64 && echo -e 'export PYARROW_IGNORE_TIMEZONE=1\nexport JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64\npytest -v -n auto woodwork/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-8-jre-headless && export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64 && echo -e 'export PYARROW_IGNORE_TIMEZONE=1\nexport JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64\npytest -v -n auto woodwork/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye main' >> /etc/apt/sources.list && apt-get update && apt-get install -y openjdk-11-jre-headless && export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64 && echo -e 'export PYARROW_IGNORE_TIMEZONE=1\nexport JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64\npytest -v -n auto woodwork/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
export SPARK_CONF_DIR=/usr/local/lib/python3.9/site-packages/pyspark/conf && bash test_commands.sh
###ACTION_DELIMITER###
export SPARK_DRIVER_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED" && export SPARK_EXECUTOR_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED" && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYARROW_IGNORE_TIMEZONE=1\nexport JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64\nexport SPARK_DRIVER_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED"\nexport SPARK_EXECUTOR_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED"\npytest -v -n auto woodwork/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYARROW_IGNORE_TIMEZONE=1\nexport JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64\nexport SPARK_MASTER=local[*]\nexport SPARK_DRIVER_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED"\nexport SPARK_EXECUTOR_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED"\npytest -v woodwork/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y pandas && pip install pandas==1.5.3 && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYARROW_IGNORE_TIMEZONE=1\nexport JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64\nexport SPARK_DRIVER_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED"\nexport SPARK_EXECUTOR_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED"\npytest -v -s woodwork/ --log-level=DEBUG' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip install moto && echo -e 'export PYARROW_IGNORE_TIMEZONE=1\nexport JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64\nexport SPARK_DRIVER_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED"\nexport SPARK_EXECUTOR_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED"\npytest -v -s woodwork/ --log-level=DEBUG' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYARROW_IGNORE_TIMEZONE=1\nexport JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64\nexport SPARK_DRIVER_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED"\nexport SPARK_EXECUTOR_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED"\nexport SPARK_MASTER=local[1]\npytest -v -s woodwork/ --log-level=DEBUG' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYARROW_IGNORE_TIMEZONE=1\nexport JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64\nexport SPARK_DRIVER_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED"\nexport SPARK_EXECUTOR_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED"\nexport SPARK_MASTER=local[1]\npytest -v -s woodwork/ --log-level=DEBUG --setup-show' > test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
export PYARROW_IGNORE_TIMEZONE=1
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export SPARK_DRIVER_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED"
export SPARK_EXECUTOR_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED"
export SPARK_MASTER=local[1]
pytest -v -s woodwork/ --log-level=DEBUG --setup-show

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
export PYARROW_IGNORE_TIMEZONE=1
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export SPARK_DRIVER_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED"
export SPARK_EXECUTOR_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED"
export SPARK_MASTER=local[1]
pytest -v -s woodwork/ --log-level=DEBUG --setup-show

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
export PYARROW_IGNORE_TIMEZONE=1
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export SPARK_DRIVER_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED"
export SPARK_EXECUTOR_EXTRA_JAVA_OPTIONS="--add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED"
export SPARK_MASTER=local[1]
pytest -v -s woodwork/ --log-level=DEBUG --setup-show

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
RUN git clone https://github.com/alteryx/woodwork.git /home/woodwork

WORKDIR /home/woodwork
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("alteryx", "woodwork_1557_to_1439")
class WOODWORK_1557_TO_1439(Instance):
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
        import json
        # Pattern for passed tests: test name followed by fixtures and PASSED
        passed_pattern = re.compile(r'(woodwork/tests/[\w/]+\.py::\w+(?:\[.+\])?)\s+\(fixtures.*?\)PASSED')
        # Pattern for failed tests: FAILED followed by test name
        failed_pattern = re.compile(r'FAILED\s+(woodwork/tests/[\w/]+\.py::\w+(?:\[.+\])?)')
        # Pattern for error tests: ERROR followed by test name (considered failed)
        error_pattern = re.compile(r'ERROR\s+(woodwork/tests/[\w/]+\.py::\w+(?:\[.+\])?)')
        # Pattern for skipped tests: SKIPPED followed by test name or test name followed by SKIPPED
        skipped_pattern1 = re.compile(r'SKIPPED\s+(woodwork/tests/[\w/]+\.py::\w+(?:\[.+\])?)')
        skipped_pattern2 = re.compile(r'(woodwork/tests/[\w/]+\.py::\w+(?:\[.+\])?)\s+\(fixtures.*?\)SKIPPED')
        test_status = {}
        # Process passed tests
        for match in passed_pattern.finditer(log):
            test_name = match.group(1)
            test_status[test_name] = 'passed'
        # Process failed tests
        for match in failed_pattern.finditer(log):
            test_name = match.group(1)
            test_status[test_name] = 'failed'
        # Process error tests (considered failed)
        for match in error_pattern.finditer(log):
            test_name = match.group(1)
            test_status[test_name] = 'failed'
        # Process skipped tests
        for match in skipped_pattern1.finditer(log):
            test_name = match.group(1)
            test_status[test_name] = 'skipped'
        for match in skipped_pattern2.finditer(log):
            test_name = match.group(1)
            test_status[test_name] = 'skipped'
        # Populate sets based on the final status
        for test, status in test_status.items():
            if status == 'passed':
                passed_tests.add(test)
            elif status == 'failed':
                failed_tests.add(test)
            elif status == 'skipped':
                skipped_tests.add(test)
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
