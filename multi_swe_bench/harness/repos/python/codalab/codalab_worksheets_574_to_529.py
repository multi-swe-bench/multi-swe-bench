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
                """ls -la
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2.7 python-virtualenv python-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python2.7 python2.7-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git
###ACTION_DELIMITER###
wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz
###ACTION_DELIMITER###
tar xzf Python-2.7.18.tgz
###ACTION_DELIMITER###
cd Python-2.7.18 && ./configure --enable-optimizations
###ACTION_DELIMITER###
make
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
cd /home/codalab-worksheets
###ACTION_DELIMITER###
./setup.sh server
###ACTION_DELIMITER###
wget https://bootstrap.pypa.io/pip/2.7/get-pip.py
###ACTION_DELIMITER###
python2.7 get-pip.py
###ACTION_DELIMITER###
pip2.7 install virtualenv
###ACTION_DELIMITER###
./setup.sh server
###ACTION_DELIMITER###
ln -s /usr/local/bin/python2.7 /usr/bin/python2.7
###ACTION_DELIMITER###
./setup.sh server
###ACTION_DELIMITER###
apt-get update && apt-get install -y libmysqlclient-dev
###ACTION_DELIMITER###
./setup.sh server
###ACTION_DELIMITER###
ln -s /usr/include/mysql/mysql_config.h /usr/include/mysql/my_config.h
###ACTION_DELIMITER###
./setup.sh server
###ACTION_DELIMITER###
ln -sf /usr/include/mysql/mysql_config.h /usr/include/mysql/my_config.h
###ACTION_DELIMITER###
./setup.sh server
###ACTION_DELIMITER###
ls /usr/include/mysql
###ACTION_DELIMITER###
./venv/bin/pip install MySQL-python==1.2.5 --global-option=build_ext --global-option="-I/usr/include/mysql"
###ACTION_DELIMITER###
export CFLAGS="-I/usr/include/mysql" && ./venv/bin/pip install MySQL-python==1.2.5
###ACTION_DELIMITER###
apt-get reinstall -y libmysqlclient-dev && export CFLAGS="-I/usr/include/mysql" && ./venv/bin/pip install MySQL-python==1.2.5
###ACTION_DELIMITER###
cp /usr/include/mysql/mysql_config.h /usr/include/mysql/my_config.h && ./venv/bin/pip install MySQL-python==1.2.5
###ACTION_DELIMITER###
ls /usr/include/mysql
###ACTION_DELIMITER###
export CFLAGS="-I/usr/include/mysql" && ./venv/bin/pip install MySQL-python==1.2.5 -v
###ACTION_DELIMITER###
apt-get install -y mysql-client && ./venv/bin/pip install MySQL-python==1.2.5
###ACTION_DELIMITER###
find / -name my_config.h 2>/dev/null && export CFLAGS="-I$(dirname $(find / -name my_config.h 2>/dev/null))" && ./venv/bin/pip install MySQL-python==1.2.5
###ACTION_DELIMITER###
mysql_config --include
###ACTION_DELIMITER###
./venv/bin/pip install MySQL-python==1.2.5 --global-option=build_ext --global-option="-I/usr/include/mysql"
###ACTION_DELIMITER###
ls -l /usr/include/mysql/my_config.h && cat /usr/include/mysql/my_config.h | head -n 10 && echo 'Test compilation...' && echo '#include "my_config.h"' > test.c && gcc -I/usr/include/mysql test.c -o test && echo 'Compilation successful' || echo 'Compilation failed'
###ACTION_DELIMITER###
find / -name mysql_config.h 2>/dev/null && ln -sf $(find / -name mysql_config.h 2>/dev/null | head -n 1) /usr/include/mysql/my_config.h
###ACTION_DELIMITER###
dpkg -L libmysqlclient-dev | grep mysql_config.h
###ACTION_DELIMITER###
echo '#define MYSQL_CONFIG_H' > /usr/include/mysql/my_config.h && ./venv/bin/pip install MySQL-python==1.2.5
###ACTION_DELIMITER###
./setup.sh server
###ACTION_DELIMITER###
./venv/bin/pip install -r requirements-tests.txt
###ACTION_DELIMITER###
echo './venv/bin/nosetests -v tests/' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
./venv/bin/nosetests -v tests/

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
./venv/bin/nosetests -v tests/

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
./venv/bin/nosetests -v tests/

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
RUN git clone https://github.com/codalab/codalab-worksheets.git /home/codalab-worksheets

WORKDIR /home/codalab-worksheets
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("codalab", "codalab-worksheets_574_to_unknown")
class CODALAB_WORKSHEETS_574_TO_529(Instance):
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
        # Implement the log parsing logic here
        pattern = re.compile(r'^\s*(?:\[\s*\d+\]\s*)?(.*?)\s*\.\.\.\s*(\w+)\s*$', re.MULTILINE)  # Handle optional [number] prefix
        matches = pattern.findall(log)
        for test_name, status in matches:
            test_name = test_name.strip()
            status_lower = status.lower()  # Case-insensitive check
            if status_lower == 'ok':
                passed_tests.add(test_name)
            elif status_lower in ['error', 'failed']:  # Handle ERROR/FAILED
                failed_tests.add(test_name)
            elif status_lower in ['skipped', 'skip']:  # Handle skipped tests
                skipped_tests.add(test_name)
            # Add handling for other statuses if needed
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
