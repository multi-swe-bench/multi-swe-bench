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
                """apt-get update && apt-get install -y openjdk-8-jdk
###ACTION_DELIMITER###
cat /etc/os-release
###ACTION_DELIMITER###
apt-cache search openjdk
###ACTION_DELIMITER###
bash -c "echo 'deb http://deb.debian.org/debian bullseye main' > /etc/apt/sources.list.d/bullseye.list"
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y openjdk-8-jdk
###ACTION_DELIMITER###
apt-cache search -t bullseye openjdk-8
###ACTION_DELIMITER###
cat /etc/apt/sources.list.d/bullseye.list
###ACTION_DELIMITER###
apt-get install -y -t bullseye openjdk-8-jdk
###ACTION_DELIMITER###
apt-cache policy openjdk-8-jdk
###ACTION_DELIMITER###
bash -c "echo 'Package: openjdk-8-jdk
Pin: release n=bullseye
Pin-Priority: 900' > /etc/apt/preferences.d/bullseye-openjdk"
###ACTION_DELIMITER###
curl -L https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u382-b05/OpenJDK8U-jdk_x64_linux_hotspot_8u382b05.tar.gz -o openjdk8.tar.gz
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl -L https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u382-b05/OpenJDK8U-jdk_x64_linux_hotspot_8u382b05.tar.gz -o openjdk8.tar.gz
###ACTION_DELIMITER###
mkdir -p /usr/local/openjdk8 && tar -xzf openjdk8.tar.gz -C /usr/local/openjdk8 --strip-components=1
###ACTION_DELIMITER###
export JAVA_HOME=/usr/local/openjdk8 && export PATH=$JAVA_HOME/bin:$PATH && java -version
###ACTION_DELIMITER###
./dev/download_spark.sh
###ACTION_DELIMITER###
export SPARK_VERSION=2.4.5 && ./dev/download_spark.sh
###ACTION_DELIMITER###
mkdir -p /root/.cache/spark-versions/ && curl -L https://archive.apache.org/dist/spark/spark-2.4.5/spark-2.4.5-bin-hadoop2.7.tgz -o /root/.cache/spark-versions/spark-2.4.5-bin-hadoop2.7.tgz && tar -xzf /root/.cache/spark-versions/spark-2.4.5-bin-hadoop2.7.tgz -C /root/.cache/spark-versions/
###ACTION_DELIMITER###
echo -e 'export SPARK_HOME=/root/.cache/spark-versions/spark-2.4.5-bin-hadoop2.7
./dev/pytest -v' > test_commands.sh
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y build-essential cmake libboost-dev libboost-system-dev libboost-filesystem-dev python3-dev && pip uninstall -y pyarrow && pip install pyarrow<0.15 --no-binary :all:
###ACTION_DELIMITER###
pip install 'pyarrow<0.15' --no-binary :all:
###ACTION_DELIMITER###
pip install cython
###ACTION_DELIMITER###
pip install 'pyarrow<0.15' --no-binary :all:
###ACTION_DELIMITER###
apt-get install -y pkg-config libarrow-dev
###ACTION_DELIMITER###
apt-get install -y lsb-release && wget -O- https://apache.jfrog.io/artifactory/arrow/$(lsb_release --id --short | tr 'A-Z' 'a-z')/apache-arrow-keyring.gpg | gpg --dearmor > /etc/apt/trusted.gpg.d/apache-arrow.gpg && echo 'deb https://apache.jfrog.io/artifactory/arrow/debian $(lsb_release --codename --short) main' > /etc/apt/sources.list.d/arrow.list && apt-get update && apt-get install -y libarrow-dev
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget -O- https://apache.jfrog.io/artifactory/arrow/debian/apache-arrow-keyring.gpg | gpg --dearmor > /etc/apt/trusted.gpg.d/apache-arrow.gpg && echo 'deb https://apache.jfrog.io/artifactory/arrow/debian $(lsb_release --codename --short) main' > /etc/apt/sources.list.d/arrow.list && apt-get update && apt-get install -y libarrow-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y -t bullseye libarrow-dev
###ACTION_DELIMITER###
pip install --force-reinstall 'pyarrow<0.15'
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y pyarrow numpy && pip install pyarrow==0.14.0 numpy==1.18.5 && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y xclip tzdata
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y pandas matplotlib && pip install pandas==1.1.5 matplotlib==3.3.4 && export PYTHON_CLIPBOARD_BACKEND=xclip && bash test_commands.sh
###ACTION_DELIMITER###
pip install openpyxl && export PYTHON_CLIPBOARD_BACKEND=xclip && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y xlrd && echo 'export PYTHON_CLIPBOARD_BACKEND=xclip' >> test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip install xlrd==1.2.0 && echo 'export TZ=UTC' >> test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip install matplotlib==3.2.2 && echo 'export PYTHON_CLIPBOARD_BACKEND=dummy' >> test_commands.sh && echo 'export JAVA_OPTS="-Duser.timezone=UTC"' >> test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYTHON_CLIPBOARD_BACKEND=dummy
export TZ=UTC
export JAVA_OPTS="-Duser.timezone=UTC"
export SPARK_HOME=/root/.cache/spark-versions/spark-2.4.5-bin-hadoop2.7
./dev/pytest -v' > test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
export PYTHON_CLIPBOARD_BACKEND=dummy
export TZ=UTC
export JAVA_OPTS="-Duser.timezone=UTC"
export SPARK_HOME=/root/.cache/spark-versions/spark-2.4.5-bin-hadoop2.7
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
export PYTHON_CLIPBOARD_BACKEND=dummy
export TZ=UTC
export JAVA_OPTS="-Duser.timezone=UTC"
export SPARK_HOME=/root/.cache/spark-versions/spark-2.4.5-bin-hadoop2.7
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
export PYTHON_CLIPBOARD_BACKEND=dummy
export TZ=UTC
export JAVA_OPTS="-Duser.timezone=UTC"
export SPARK_HOME=/root/.cache/spark-versions/spark-2.4.5-bin-hadoop2.7
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

# Choose an appropriate base image based on the project's requirements - replace python:3.7-slim with actual base image
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
RUN git clone https://github.com/databricks/koalas.git /home/koalas

WORKDIR /home/koalas
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("databricks", "koalas_1381_to_532")
class KOALAS_1381_TO_532(Instance):
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
        # Extract passed tests from progress lines
        passed_pattern = re.compile(r'([\w\/]+\.py::[\w:]+) PASSED \[\s*\d+%?\]')
        passed_tests.update(passed_pattern.findall(log))
        # Extract failed tests from progress and summary lines
        failed_progress_pattern = re.compile(r'([\w\/]+\.py::[\w:]+) FAILED \[\s*\d+%?\]')
        failed_tests.update(failed_progress_pattern.findall(log))
        failed_summary_pattern = re.compile(r'FAILED ([\w\/]+\.py::[\w:]+)')
        failed_tests.update(failed_summary_pattern.findall(log))
        # Extract skipped tests from progress and summary lines
        skipped_progress_pattern = re.compile(r'([\w\/]+\.py::[\w:]+) SKIPPED \[\s*\d+%?\]')
        skipped_tests.update(skipped_progress_pattern.findall(log))
        skipped_summary_pattern = re.compile(r'SKIPPED ([\w\/]+\.py::[\w:]+)')
        skipped_tests.update(skipped_summary_pattern.findall(log))
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
