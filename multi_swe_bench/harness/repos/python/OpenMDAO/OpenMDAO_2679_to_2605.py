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
        repo_name = self.pr.repo
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
                """ls -la
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
pip install -e .[all] --break-system-packages
###ACTION_DELIMITER###
echo 'testflo openmdao -v -n 1' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install numpy==1.26.0 --break-system-packages
###ACTION_DELIMITER###
pip uninstall -y numpy --break-system-packages && pip install numpy==1.26.0 --break-system-packages
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y numpy --break-system-packages && pip install numpy==1.19.5 --break-system-packages
###ACTION_DELIMITER###
apt-get install -y python3.10 python3.10-pip && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 && pip3.10 install -e .[all] --break-system-packages && pip3.10 install numpy==1.23.5 --break-system-packages
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository -y ppa:deadsnakes/ppa && apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.8 python3.8-pip python3.8-dev && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1 && python3.8 -m pip install --upgrade pip && pip3.8 install -e .[all] --break-system-packages && pip3.8 install numpy==1.23.5 --break-system-packages
###ACTION_DELIMITER###
apt-get install -y python3.8 python3.8-dev && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.8 get-pip.py && python3.8 -m pip install --upgrade pip && pip3.8 install -e .[all] --break-system-packages && pip3.8 install numpy==1.23.5 --break-system-packages
###ACTION_DELIMITER###
apt-get install -y curl && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.8 get-pip.py && python3.8 -m pip install --upgrade pip && pip3.8 install -e .[all] --break-system-packages && pip3.8 install numpy==1.23.5 --break-system-packages
###ACTION_DELIMITER###
apt-get install -y curl && curl https://bootstrap.pypa.io/pip/3.8/get-pip.py -o get-pip.py && python3.8 get-pip.py && python3.8 -m pip install --upgrade pip && pip3.8 install -e .[all] --break-system-packages && pip3.8 install numpy==1.23.5 --break-system-packages
###ACTION_DELIMITER###
apt-get install -y python3.8-distutils && curl https://bootstrap.pypa.io/pip/3.8/get-pip.py -o get-pip.py && python3.8 get-pip.py && python3.8 -m pip install --upgrade pip && pip3.8 install -e .[all] --break-system-packages && pip3.8 install numpy==1.23.5 --break-system-packages
###ACTION_DELIMITER###
curl https://bootstrap.pypa.io/pip/3.8/get-pip.py -o get-pip.py && python3.8 get-pip.py --ignore-installed && python3.8 -m pip install --upgrade pip && pip3.8 install -e .[all] --break-system-packages && pip3.8 install numpy==1.23.5 --break-system-packages
###ACTION_DELIMITER###
pip3.8 install --upgrade setuptools && pip3.8 install pyDOE2 docopt --no-build-isolation --break-system-packages && pip3.8 install -e .[all] --break-system-packages && pip3.8 install numpy==1.23.5 --break-system-packages
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'testflo openmdao -v -n 1' > test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
testflo openmdao -v -n 1

""".replace("[[REPO_NAME]]", repo_name),
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
testflo openmdao -v -n 1

""".replace("[[REPO_NAME]]", repo_name),
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
testflo openmdao -v -n 1

""".replace("[[REPO_NAME]]", repo_name),
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
RUN git clone https://github.com/OpenMDAO/OpenMDAO.git /home/OpenMDAO

WORKDIR /home/OpenMDAO
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("OpenMDAO", "OpenMDAO_2679_to_2605")
class OPENMDAO_2679_TO_2605(Instance):
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

        return "bash /home/run.sh"

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

        # Split log into lines and process each line
        for line in log.split("\n"):
            if "..." in line and ".py" in line:
                # Split line into test name and status parts
                parts = line.split("...", 1)
                if len(parts) < 2:
                    continue
                # Extract and clean test name
                test_part = parts[0].split("]")[-1].strip()
                cleaned_test_name = re.sub(r"[^\w/:.-]+$", "", test_part)
                # Ensure the test name contains a .py file
                if ".py" not in cleaned_test_name:
                    continue
                # Extract status
                status = parts[1].strip().split()[0]
                # Categorize test
                if status == "OK":
                    passed_tests.add(cleaned_test_name)
                elif status == "FAIL":
                    failed_tests.add(cleaned_test_name)
                elif status == "SKIP":
                    skipped_tests.add(cleaned_test_name)
        parsed_results = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
        }

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
