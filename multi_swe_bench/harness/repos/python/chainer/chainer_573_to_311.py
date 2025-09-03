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
                """ls -la
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
pip install numpy six
###ACTION_DELIMITER###
python3 -m venv venv && source venv/bin/activate && pip install numpy six
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv && source venv/bin/activate && pip install numpy six
###ACTION_DELIMITER###
source venv/bin/activate && python setup.py install && pip install mock nose
###ACTION_DELIMITER###
source venv/bin/activate && pip install setuptools
###ACTION_DELIMITER###
source venv/bin/activate && python setup.py install && pip install mock nose
###ACTION_DELIMITER###
source venv/bin/activate && pip install filelock protobuf
###ACTION_DELIMITER###
source venv/bin/activate && nosetests -v
###ACTION_DELIMITER###
source venv/bin/activate && pip install pytest pytest-nose && pytest -v
###ACTION_DELIMITER###
source venv/bin/activate && pip install pytest && pytest -v
###ACTION_DELIMITER###
source venv/bin/activate && CHAINER_TEST_CPU_ONLY=1 pytest -v
###ACTION_DELIMITER###
source venv/bin/activate && pytest --ignore=tests/cupy_tests -v
###ACTION_DELIMITER###
source venv/bin/activate && pip install cupy-cpu && CHAINER_TEST_CPU_ONLY=1 pytest --ignore=tests/cupy_tests -v
###ACTION_DELIMITER###
source venv/bin/activate && pip uninstall -y cupy && CHAINER_TEST_CPU_ONLY=1 pytest -v --ignore=tests/cupy_tests
###ACTION_DELIMITER###
source venv/bin/activate && export CUPY_CUDA_VERSION=none && CHAINER_TEST_CPU_ONLY=1 && pytest -v --ignore=tests/cupy_tests
###ACTION_DELIMITER###
source venv/bin/activate && CHAINER_TEST_CPU_ONLY=1 pytest -v --ignore=cupy --ignore=tests/cupy_tests
###ACTION_DELIMITER###
apt-get install -y python3.8 python3.8-venv && python3.8 -m venv venv38 && source venv38/bin/activate && pip install setuptools numpy six mock nose filelock protobuf && python setup.py install && nosetests -v
###ACTION_DELIMITER###
apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.6 python3.6-venv
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.7 python3.7-venv
###ACTION_DELIMITER###
python3.7 -m venv venv37 && source venv37/bin/activate && pip install setuptools numpy six mock nose filelock protobuf && python setup.py install && nosetests -v
###ACTION_DELIMITER###
echo 'source venv37/bin/activate && CHAINER_TEST_CPU_ONLY=1 nosetests -v' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
source venv37/bin/activate && CHAINER_TEST_CPU_ONLY=1 nosetests -v

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
source venv37/bin/activate && CHAINER_TEST_CPU_ONLY=1 nosetests -v

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
source venv37/bin/activate && CHAINER_TEST_CPU_ONLY=1 nosetests -v

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
RUN git clone https://github.com/chainer/chainer.git /home/chainer

WORKDIR /home/chainer
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("chainer", "chainer_573_to_311")
class CHAINER_573_TO_311(Instance):
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
        import json  # Note: json may not be needed, but kept as per skeleton
        # Regex patterns to match test lines
        line_pattern = re.compile(r'\[\s*\d+\]\s*(test_.+?)\s+\.\.\.\s+(ok|ERROR|FAIL|SKIPPED)\s*$')
        error_pattern = re.compile(r'(ERROR|FAIL|SKIPPED):\s*(.*)')
        # Process line number lines
        for line in log.splitlines():
            line_stripped = line.strip()
            if '...' in line_stripped:
                parts = re.split(r'\s+\.\.\.\s+', line_stripped)
                if len(parts) == 2:
                    test_part = parts[0].strip()
                    status = parts[1].strip()
                    # Extract test name by removing leading line number
                    test_name = re.sub(r'^\[\s*\d+\]\s*', '', test_part)
                    if test_name.startswith('test_'):
                        if status == 'ok':
                            passed_tests.add(test_name)
                        elif status in ('ERROR', 'FAIL'):
                            failed_tests.add(test_name)
                        elif status == 'SKIPPED':
                            skipped_tests.add(test_name)
        # Process error/fail/skipped lines
        for match in error_pattern.findall(log):
            status = match[0]
            test_name = match[1].strip()
            if status in ('ERROR', 'FAIL'):
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
