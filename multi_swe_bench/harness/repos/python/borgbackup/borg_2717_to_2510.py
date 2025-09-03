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
                """ls
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.6 python3.6-venv python3.6-dev
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.6 python3.6-venv python3.6-dev
###ACTION_DELIMITER###
apt-get install -y python3.7 python3.7-venv python3.7-dev
###ACTION_DELIMITER###
python3.7 -m venv venv37
###ACTION_DELIMITER###
source venv37/bin/activate
###ACTION_DELIMITER###
export CFLAGS="-I/usr/include/openssl -DOPENSSL_API_COMPAT=0x10002000L" && export CPPFLAGS="$CFLAGS" && export LDFLAGS="-lcrypto" && pip install -r requirements.d/development.txt -r requirements.d/attic.txt -r requirements.d/fuse.txt
###ACTION_DELIMITER###
apt-get install -y libssl-dev && export CFLAGS="-I/usr/include/openssl -DOPENSSL_API_COMPAT=0x10002000L" && export CPPFLAGS="$CFLAGS" && export LDFLAGS="-lcrypto" && pip install -r requirements.d/development.txt -r requirements.d/attic.txt -r requirements.d/fuse.txt
###ACTION_DELIMITER###
apt-get install -y pkg-config && export CFLAGS="-I/usr/include/openssl -DOPENSSL_API_COMPAT=0x10002000L" && export CPPFLAGS="$CFLAGS" && export LDFLAGS="-lcrypto" && pip install -r requirements.d/development.txt -r requirements.d/attic.txt -r requirements.d/fuse.txt
###ACTION_DELIMITER###
apt-get install -y libfuse-dev && export CFLAGS="-I/usr/include/openssl -DOPENSSL_API_COMPAT=0x10002000L" && export CPPFLAGS="$CFLAGS" && export LDFLAGS="-lcrypto" && pip install -r requirements.d/development.txt -r requirements.d/attic.txt -r requirements.d/fuse.txt
###ACTION_DELIMITER###
apt-get install -y build-essential && export CFLAGS="-I/usr/include/openssl -DOPENSSL_API_COMPAT=0x10002000L" && export CPPFLAGS="$CFLAGS" && export LDFLAGS="-lcrypto" && pip install -r requirements.d/development.txt -r requirements.d/attic.txt -r requirements.d/fuse.txt
###ACTION_DELIMITER###
export CFLAGS="-I/usr/include/openssl -DOPENSSL_API_COMPAT=0x10000000L" && export CPPFLAGS="$CFLAGS" && export LDFLAGS="-lcrypto" && pip install -r requirements.d/development.txt -r requirements.d/attic.txt -r requirements.d/fuse.txt
###ACTION_DELIMITER###
export CFLAGS="-I/usr/include/openssl -DOPENSSL_API_COMPAT=0x10002000L" && export CPPFLAGS="$CFLAGS" && export LDFLAGS="-lcrypto" && pip install -r requirements.d/development.txt -r requirements.d/attic.txt -r requirements.d/fuse.txt
###ACTION_DELIMITER###
export CFLAGS="-I/usr/include/openssl -DOPENSSL_API_COMPAT=0x10002000L" && export CPPFLAGS="$CFLAGS" && export LDFLAGS="-lcrypto" && pip install -r requirements.d/development.txt -r requirements.d/fuse.txt
###ACTION_DELIMITER###
echo 'pytest -v -rs --benchmark-skip --pyargs borg.testsuite' > test_commands.sh
###ACTION_DELIMITER###
pip install 'pytest<5.0' && bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest==5.4.3 && bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest==5.3.5 pytest-xdist==1.34.0 && bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest==4.6.11 pytest-xdist==1.34.0 && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -rs --benchmark-skip --pyargs borg.testsuite --noconfig' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/\[pytest\]/\[tool:pytest\]/g' setup.cfg && pip install pytest>=6.0 && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y pytest-benchmark && pip install pytest==6.2.5 && bash test_commands.sh
###ACTION_DELIMITER###
pip install -e . && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y liblz4-dev && pip install -e . && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libacl1-dev && pip install -e . && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -rs --pyargs borg.testsuite' > test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v -rs --pyargs borg.testsuite

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
pytest -v -rs --pyargs borg.testsuite

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
pytest -v -rs --pyargs borg.testsuite

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
RUN git clone https://github.com/borgbackup/borg.git /home/borg

WORKDIR /home/borg
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("borgbackup", "borg_2717_to_2510")
class BORG_2717_TO_2510(Instance):
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
        # Pattern to match test lines with status (PASSED, FAILED, SKIPPED)
        # Pattern for PASSED/FAILED tests in execution lines (with line numbers)
        test_exec_pattern = re.compile(r'(borg/[\w/:.\[\]]+)\s+(PASSED|FAILED|SKIPPED)\b', re.IGNORECASE)
        # Split log into lines and process each line
        for line in log.split('\n'):
            exec_match = test_exec_pattern.search(line)
            if exec_match:
                test_name = exec_match.group(1)
                status = exec_match.group(2)
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
