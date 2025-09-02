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
                """ls
###ACTION_DELIMITER###
echo 'pytest-cov<=2.12.1' > constraints-test.txt && cat constraints-dev.txt >> constraints-test.txt
###ACTION_DELIMITER###
pip install -e . -r requirements-dev-test.txt -c constraints-test.txt
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'jinja2<=2.11.3' >> constraints-test.txt && pip install -e . -r requirements-dev-test.txt -c constraints-test.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'markupsafe<2.0.0' >> constraints-test.txt && pip install -e . -r requirements-dev-test.txt -c constraints-test.txt
###ACTION_DELIMITER###
sed -i 's/markupsafe<2.0.0/markupsafe==1.1.1/' constraints-test.txt && pip install -e . -r requirements-dev-test.txt -c constraints-test.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y locales && locale-gen en_US.UTF-8 && export LANG=en_US.UTF-8
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
locale -a && locale-gen en_US.UTF-8 && echo 'export LANG=en_US.UTF-8' > test_commands.sh && echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider' >> test_commands.sh
###ACTION_DELIMITER###
sed -i 's/^# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8 && echo 'export LANG=en_US.UTF-8' > test_commands.sh && echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider' >> test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -r requirements.txt -c constraints-test.txt
###ACTION_DELIMITER###
echo 'sqlalchemy<1.4.0' >> constraints-test.txt && pip install -e . -r requirements-dev-test.txt -c constraints-test.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -rA -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install nbformat && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pandas<2.0.0' >> constraints-test.txt && pip install -e . -r requirements-dev-test.txt -c constraints-test.txt
###ACTION_DELIMITER###
sed -i 's/pandas<2.0.0/pandas==1.4.0/' constraints-test.txt && pip install -e . -r requirements-dev-test.txt -c constraints-test.txt
###ACTION_DELIMITER###
sed -i 's/pandas==1.4.0/pandas==1.3.5/' constraints-test.txt && pip install -e . -r requirements-dev-test.txt -c constraints-test.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'numpy<=1.21.6' >> constraints-test.txt && pip install -e . -r requirements-dev-test.txt -c constraints-test.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install nbconvert && bash test_commands.sh
###ACTION_DELIMITER###
echo 'jinja2<=2.11.3' >> constraints-test.txt && echo 'mistune<2.0.0' >> constraints-test.txt && pip install -e . -r requirements-dev-test.txt -c constraints-test.txt && pip install nbconvert==6.5.4 && bash test_commands.sh
###ACTION_DELIMITER###
echo 'jinja2<=2.11.3' >> constraints-test.txt && echo 'mistune<2.0.0' >> constraints-test.txt && pip install -e . -r requirements-dev-test.txt -c constraints-test.txt && pip install nbconvert==6.5.4 && bash test_commands.sh
###ACTION_DELIMITER###
pip install jinja2==2.11.3 && pip install -e . -r requirements-dev-test.txt -c constraints-test.txt && pip install nbconvert==5.6.1 && bash test_commands.sh
###ACTION_DELIMITER###
pip install ipython_genutils && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v -rA -p no:cacheprovider

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
pytest -v -rA -p no:cacheprovider

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
pytest -v -rA -p no:cacheprovider

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
RUN git clone https://github.com/great-expectations/great_expectations.git /home/great_expectations

WORKDIR /home/great_expectations
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("great-expectations", "great_expectations_4426_to_unknown")
class GREAT_EXPECTATIONS_4426_TO_UNKNOWN(Instance):
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
        # Extract all test names (lines with line numbers and test cases)
        # Capture all test names (optional line number brackets)
        all_tests_pattern = re.compile(r'^(?:\[\s*\d+\]\s+)?(tests/.*?\.py::(?:\w+::)*test_\w+\[.*?\]|tests/.*?\.py::(?:\w+::)*test_\w+)', re.MULTILINE)
        all_tests = set(match for match in all_tests_pattern.findall(log))
        # Extract skipped tests (optional line number brackets)
        skipped_pattern = re.compile(r'^(?:\[\s*\d+\]\s+)?(tests/.*?\.py::(?:\w+::)*test_\w+\[.*?\]|tests/.*?\.py::(?:\w+::)*test_\w+)\s+SKIPPED', re.MULTILINE)
        skipped_tests = set(match for match in skipped_pattern.findall(log))
        # Extract failed tests (optional line number brackets)
        failed_pattern = re.compile(r'^(?:\[\s*\d+\]\s+)?FAILED\s+(tests/.*?\.py::(?:\w+::)*test_\w+\[.*?\]|tests/.*?\.py::(?:\w+::)*test_\w+)', re.MULTILINE)
        failed_tests = set(match for match in failed_pattern.findall(log))
        # Calculate passed tests (all tests not skipped or failed)
        passed_tests = all_tests - skipped_tests - failed_tests
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
