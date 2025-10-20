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
                """ls
###ACTION_DELIMITER###
make installdeps-test
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make installdeps-test
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
make installdeps-test
###ACTION_DELIMITER###
python3 -m venv venv && source venv/bin/activate && make installdeps-test
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv && source venv/bin/activate && make installdeps-test
###ACTION_DELIMITER###
python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip setuptools && make installdeps-test
###ACTION_DELIMITER###
python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip setuptools && pip install pandas>=1.0.0 && pip install -e . && pip install -r test-requirements.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.8 python3.8-venv && python3.8 -m venv venv && source venv/bin/activate && pip install --upgrade pip setuptools && make installdeps-test
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.8 python3.8-venv
###ACTION_DELIMITER###
python3.8 -m venv venv && source venv/bin/activate && pip install --upgrade pip setuptools && make installdeps-test
###ACTION_DELIMITER###
sed -i '6s/2.1.0/2.1.13/' test-requirements.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip install --upgrade pip setuptools && make installdeps-test
###ACTION_DELIMITER###
source venv/bin/activate && make test
###ACTION_DELIMITER###
sed -i '1s/4.4.1/6.2.5/' test-requirements.txt && source venv/bin/activate && make installdeps-test && make test
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.19.5 && make installdeps-test && make test
###ACTION_DELIMITER###
source venv/bin/activate && pip install scikit-learn==0.23.2 && make test
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.19.5 && pip install -e . && pip install -r test-requirements.txt && make test
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.19.5 matplotlib==3.3.4 && pip install -e . && pip install -r test-requirements.txt && make test
###ACTION_DELIMITER###
source venv/bin/activate && pip uninstall -y numpy && pip install numpy==1.19.5 && pip install -e . && pip install -r test-requirements.txt && make test
###ACTION_DELIMITER###
source venv/bin/activate && sed -i 's/dtype=np.int/dtype=int/' venv/lib/python3.8/site-packages/sklearn/feature_extraction/image.py && make test
###ACTION_DELIMITER###
source venv/bin/activate && sed -i 's/np.float/float/' venv/lib/python3.8/site-packages/sklearn/linear_model/_least_angle.py && make test
###ACTION_DELIMITER###
source venv/bin/activate && sed -i 's/np.float/float/' venv/lib/python3.8/site-packages/sklearn/decomposition/_lda.py && make test
###ACTION_DELIMITER###
source venv/bin/activate && sed -i 's/from numpy import bool/from numpy import bool_ as bool/' evalml/tests/conftest.py && make test
###ACTION_DELIMITER###
deactivate && rm -rf venv && python3.8 -m venv venv && source venv/bin/activate && pip install --upgrade pip setuptools && pip install numpy==1.19.5 matplotlib==3.3.4 && pip install -e . && pip install -r test-requirements.txt && make test
###ACTION_DELIMITER###
source venv/bin/activate && sed -i 's/np.int/int/g' evalml/tests/conftest.py && pip freeze | grep numpy && make test
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.19.5 && sed -i 's/dtype=np.int/dtype=int/' venv/lib/python3.8/site-packages/sklearn/feature_extraction/image.py && make test
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.22.0 && sed -i 's/dtype=np.int/dtype=int/' venv/lib/python3.8/site-packages/sklearn/feature_extraction/image.py && make test
###ACTION_DELIMITER###
apt-get update && apt-get install -y graphviz && source venv/bin/activate && echo 'pytest evalml/ --doctest-modules --doctest-continue-on-failure -v' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
pytest evalml/ --doctest-modules --doctest-continue-on-failure -v' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
source venv/bin/activate
pytest evalml/ --doctest-modules --doctest-continue-on-failure -v

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
source venv/bin/activate
pytest evalml/ --doctest-modules --doctest-continue-on-failure -v

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
source venv/bin/activate
pytest evalml/ --doctest-modules --doctest-continue-on-failure -v

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
RUN git clone https://github.com/alteryx/evalml.git /home/evalml

WORKDIR /home/evalml
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("alteryx", "evalml_1651_to_1566")
class EVALML_1651_TO_1566(Instance):
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
        # Regex patterns to match test lines
        pattern1 = re.compile(r'^(.*?)\s+(PASSED|FAILED|SKIPPED)\s+\[\s*\d+\%\]', re.MULTILINE)
        pattern2 = re.compile(r'^(PASSED|FAILED|SKIPPED)\s+(.*?)\s+-\s+.*', re.MULTILINE)
        # Extract tests from pattern 1 matches
        for test_name, status in pattern1.findall(log):
            test_name = test_name.strip()
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
        # Extract tests from pattern 2 matches
        for status, test_name in pattern2.findall(log):
            test_name = test_name.strip()
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
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
