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
        return "python:3.10-slim"
    
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
pip install -e .[tests,docs]
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
pip install -e .[tests,docs]
###ACTION_DELIMITER###
pip download ruamel.yaml==0.15.51 --no-deps && tar xzf ruamel.yaml-0.15.51.tar.gz && cd ruamel.yaml-0.15.51 && sed -i 's/Str/Constant/g' setup.py && sed -i 's/node.s/node.value/g' setup.py && pip install . && cd ..
###ACTION_DELIMITER###
wget https://files.pythonhosted.org/packages/source/r/ruamel.yaml/ruamel.yaml-0.15.51.tar.gz && tar xzf ruamel.yaml-0.15.51.tar.gz && cd ruamel.yaml-0.15.51 && sed -i 's/Str/Constant/g' setup.py && sed -i 's/node.s/node.value/g' setup.py && pip install . && cd ..
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
wget https://files.pythonhosted.org/packages/source/r/ruamel.yaml/ruamel.yaml-0.15.51.tar.gz && tar xzf ruamel.yaml-0.15.51.tar.gz && cd ruamel.yaml-0.15.51 && sed -i 's/Str/Constant/g' setup.py && sed -i 's/node.s/node.value/g' setup.py && pip install . && cd ..
###ACTION_DELIMITER###
cd ruamel.yaml-0.15.51 && sed -i 's/Str/Constant/g' setup.py && sed -i 's/Bytes/Constant/g' setup.py && sed -i 's/node.s/node.value/g' setup.py && pip install . && cd ..
###ACTION_DELIMITER###
sed -i 's/Str/Constant/g' setup.py && sed -i 's/Bytes/Constant/g' setup.py && sed -i 's/node.s/node.value/g' setup.py && pip install .
###ACTION_DELIMITER###
sed -i 's/Str/Constant/g' setup.py && sed -i 's/Bytes/Constant/g' setup.py && sed -i 's/Num/Constant/g' setup.py && sed -i 's/node.s/node.value/g' setup.py && sed -i 's/node.n/node.value/g' setup.py && pip install .
###ACTION_DELIMITER###
sed -i 's/NameConstant/Constant/g' setup.py && pip install .
###ACTION_DELIMITER###
cd .. && pip install -e .[tests,docs]
###ACTION_DELIMITER###
pip install rdflib-jsonld==0.6.2
###ACTION_DELIMITER###
pip install -e .[tests,docs]
###ACTION_DELIMITER###
pip install setuptools<58.0.0 && pip install rdflib-jsonld==0.4.0 && pip install -e .[tests,docs]
###ACTION_DELIMITER###
pip install 'setuptools<58.0.0' && pip install rdflib-jsonld==0.4.0 && pip install -e .[tests,docs]
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install --upgrade pytest-yapf
###ACTION_DELIMITER###
sed -i 's/--yapf//' pytest.ini
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
sed -i 's/--flake8 --pep8 //' pytest.ini
###ACTION_DELIMITER###
pip uninstall -y pytest-pep8 pytest-flake8 pytest-yapf
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install attrs==19.3.0
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
echo 'pytest -v' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v

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
pytest -v

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
pytest -v

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
FROM python:3.10-slim

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
RUN git clone https://github.com/SwissDataScienceCenter/renku-python.git /home/renku-python

WORKDIR /home/renku-python
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("SwissDataScienceCenter", "renku-python_369_to_unknown")
class RENKU_PYTHON_369_TO_307(Instance):
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
        # Extract test cases using regex
        # Extract test cases where test name comes first
        pattern1 = re.compile(r'(tests/[^:]+::[^ ]+)\s+(PASSED|FAILED|ERROR|SKIPPED|XFAILED)')
        matches1 = pattern1.findall(log)
        # Extract test cases where status comes first
        pattern2 = re.compile(r'(PASSED|FAILED|ERROR|SKIPPED|XFAILED)\s+(tests/[^:]+::[^ ]+)')
        matches2 = pattern2.findall(log)
        for test_name, status in matches1:
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ['FAILED', 'ERROR', 'XFAILED']:
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
        for status, test_name in matches2:
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ['FAILED', 'ERROR', 'XFAILED']:
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
