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
                """apt-get update && apt-get install -y python3 python3-pip python3-venv build-essential libssl-dev rustc cargo
###ACTION_DELIMITER###
python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip
###ACTION_DELIMITER###
source venv/bin/activate && pip install -r requirements_test.txt
###ACTION_DELIMITER###
sed -i 's/codecov==2.0.15/codecov==2.1.13/' requirements_test.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip install -r requirements_test.txt
###ACTION_DELIMITER###
sed -i 's/typed-ast==1.4.1/typed-ast==1.5.5/' requirements_test.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip install -r requirements_test.txt
###ACTION_DELIMITER###
sed -i 's/mypy==0.761/mypy==0.910/' requirements_test.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip install -r requirements_test.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip install cryptography
###ACTION_DELIMITER###
source venv/bin/activate && pip install -e .
###ACTION_DELIMITER###
source venv/bin/activate && wget https://files.pythonhosted.org/packages/source/e/ed25519/ed25519-1.5.tar.gz && tar -xzf ed25519-1.5.tar.gz && sed -i 's/configparser.SafeConfigParser()/configparser.ConfigParser()/g' ed25519-1.5/versioneer.py && pip install ./ed25519-1.5
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
source venv/bin/activate && wget https://files.pythonhosted.org/packages/source/e/ed25519/ed25519-1.5.tar.gz && tar -xzf ed25519-1.5.tar.gz && sed -i 's/configparser.SafeConfigParser()/configparser.ConfigParser()/g' ed25519-1.5/versioneer.py && pip install ./ed25519-1.5
###ACTION_DELIMITER###
source venv/bin/activate && wget https://files.pythonhosted.org/packages/source/e/ed25519/ed25519-1.5.tar.gz && tar -xzf ed25519-1.5.tar.gz && sed -i 's/configparser.SafeConfigParser()/configparser.ConfigParser()/g' ed25519-1.5/versioneer.py && sed -i 's/parser.readfp(f)/parser.read_file(f)/g' ed25519-1.5/versioneer.py && pip install ./ed25519-1.5
###ACTION_DELIMITER###
source venv/bin/activate && pip install -e .
###ACTION_DELIMITER###
echo './venv/bin/pytest -v -rA --tb=short -p no:cacheprovider ./tests' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pytest==5.3.5/pytest==7.4.0/' requirements_test.txt && source venv/bin/activate && pip install -r requirements_test.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3-distutils
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.12-distutils
###ACTION_DELIMITER###
sed -i 's/pytest-timeout==1.3.4/pytest-timeout==2.2.0/' requirements_test.txt && source venv/bin/activate && pip install -r requirements_test.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.9 python3.9-venv python3.9-dev
###ACTION_DELIMITER###
rm -rf venv && python3.9 -m venv venv && source venv/bin/activate && pip install --upgrade pip
###ACTION_DELIMITER###
source venv/bin/activate && pip install -r requirements_test.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip install -e .
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install protobuf==3.20.1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y avahi-daemon avahi-utils libavahi-client-dev && service avahi-daemon start
###ACTION_DELIMITER###
source venv/bin/activate && pip install pytest-mock && bash test_commands.sh
###ACTION_DELIMITER###
avahi-daemon --daemonize && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
./venv/bin/pytest -v -rA --tb=short -p no:cacheprovider ./tests

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
./venv/bin/pytest -v -rA --tb=short -p no:cacheprovider ./tests

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
./venv/bin/pytest -v -rA --tb=short -p no:cacheprovider ./tests

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
RUN git clone https://github.com/postlund/pyatv.git /home/pyatv

WORKDIR /home/pyatv
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("postlund", "pyatv_418_to_unknown")
class PYATV_418_TO_UNKNOWN(Instance):
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
        # Compile regex patterns to match test cases and their statuses
        pattern1 = re.compile(r'^(tests/[\w/\.::]+)\s+(PASSED|FAILED|SKIPPED)\b')
        pattern2 = re.compile(r'^(PASSED|FAILED|SKIPPED)\s+(tests/[\w/\.::]+)\b')
        # Iterate through each line in the log content
        for line in log.split('\n'):
            line = line.strip()
            # Check for pattern where test name is followed by status
            match = pattern1.match(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
            else:
                # Check for pattern where status is followed by test name
                match = pattern2.match(line)
                if match:
                    status = match.group(1)
                    test_name = match.group(2)
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
