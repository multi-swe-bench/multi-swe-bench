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
        return "python:3.10.7-slim-bullseye"

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
cat setup.sh
###ACTION_DELIMITER###
cat requirements-dev.txt
###ACTION_DELIMITER###
echo -e 'y\ny\ny\ny' | ./setup.sh --install
###ACTION_DELIMITER###
apt-get update && apt-get install -y sudo curl
###ACTION_DELIMITER###
echo -e 'y\ny\ny\ny' | ./setup.sh --install
###ACTION_DELIMITER###
apt-get update && apt-get install -y libpython3.10-dev python3.10-venv libta-lib-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential python3-dev python3-venv wget
###ACTION_DELIMITER###
wget https://downloads.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz && tar -xzf ta-lib-0.4.0-src.tar.gz && cd ta-lib && ./configure --prefix=/usr && make && make install
###ACTION_DELIMITER###
cd /home/freqtrade && echo -e 'y\ny\ny\ny' | ./setup.sh --install
###ACTION_DELIMITER###
source .env/bin/activate && export TA_LIBRARY_PATH=/usr/lib && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
python3.10 -m venv .env && source .env/bin/activate && export TA_LIBRARY_PATH=/usr/lib && pip install --upgrade pip && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && export TA_LIBRARY_PATH=/usr/lib && pip install --upgrade pip && pip install git+https://github.com/ccxt/ccxt.git@1.93.98 && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
sed -i 's/ccxt==1.93.98/ccxt==1.9.398/' requirements.txt && source .env/bin/activate && export TA_LIBRARY_PATH=/usr/lib && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
sed -i 's/ccxt==1.9.398/ccxt==1.93.98/' requirements.txt && source .env/bin/activate && export TA_LIBRARY_PATH=/usr/lib && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
sed -i 's/ccxt==1.93.98/ccxt==1.93.1/' requirements.txt && source .env/bin/activate && export TA_LIBRARY_PATH=/usr/lib && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y libblosc-dev && source .env/bin/activate && export TA_LIBRARY_PATH=/usr/lib && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get install -y liblz4-dev libzstd-dev && source .env/bin/activate && export TA_LIBRARY_PATH=/usr/lib && export LD_LIBRARY_PATH=/usr/lib && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && export TA_INCLUDE_PATH=/usr/include && export TA_LIBRARY_PATH=/usr/lib && pip install TA-Lib && pip install blosc --no-binary :all: && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y cmake && source .env/bin/activate && export TA_INCLUDE_PATH=/usr/include && export TA_LIBRARY_PATH=/usr/lib && pip install blosc && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && export TA_INCLUDE_PATH=/usr/include && export TA_LIBRARY_PATH=/usr/lib && pip install TA-Lib --no-binary :all: && pip install blosc --no-binary :all: && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && export BLOSC_USE_SYSTEM_LIBS=1 && export TA_INCLUDE_PATH=/usr/include && export TA_LIBRARY_PATH=/usr/lib && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && export BLOSC_USE_SYSTEM_LIBS=1 && export TA_INCLUDE_PATH=/usr/include && export TA_LIBRARY_PATH=/usr/lib && pip install blosc --no-binary :all: --install-option='--use-system-blosc' && pip install TA-Lib --no-binary :all: && pip install -r requirements-dev.txt --upgrade-strategy eager
###ACTION_DELIMITER###
source .env/bin/activate && export TA_INCLUDE_PATH=/usr/include && export TA_LIBRARY_PATH=/usr/lib && export BLOSC_USE_SYSTEM_LIBS=1 && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && export TA_INCLUDE_PATH=/usr/include && export TA_LIBRARY_PATH=/usr/lib && export BLOSC_USE_SYSTEM_LIBS=1 && pip install numpy==1.23.3 && pip install TA-Lib && pip install blosc && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && export TA_INCLUDE_PATH=/usr/include && export TA_LIBRARY_PATH=/usr/lib && export BLOSC_USE_SYSTEM_LIBS=1 && pip install TA-Lib==0.4.25 && pip install blosc --no-binary :all: && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
wget https://downloads.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz && tar -xzf ta-lib-0.4.0-src.tar.gz && cd ta-lib && ./configure --prefix=/usr && make && make install && cd .. && source .env/bin/activate && export TA_INCLUDE_PATH=/usr/include && export TA_LIBRARY_PATH=/usr/lib && pip install TA-Lib==0.4.19 && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && export TA_INCLUDE_PATH=/usr/include && export TA_LIBRARY_PATH=/usr/lib && export CFLAGS="-I$VIRTUAL_ENV/include/python3.10/numpy" && pip install TA-Lib==0.4.19 && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && export TA_INCLUDE_PATH=/usr/include && export TA_LIBRARY_PATH=/usr/lib && export CFLAGS="-I$VIRTUAL_ENV/lib/python3.10/site-packages/numpy/core/include" && pip install TA-Lib==0.4.25 && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && export CMAKE_PREFIX_PATH=/usr && export BLOSC_USE_SYSTEM_LIBS=1 && pip install blosc && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && export CMAKE_PREFIX_PATH=/usr && pip install blosc --global-option="build_ext" --global-option="-DUSE_SYSTEM_BLOSC=ON" && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && export CMAKE_ARGS="-DUSE_SYSTEM_BLOSC=ON" && pip install blosc -v && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && export CMAKE_ARGS="-DUSE_SYSTEM_BLOSC=ON" && pip install blosc==1.10.6 && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo 'pytest -v' > /home/freqtrade/test_commands.sh && chmod +x /home/freqtrade/test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v

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
pytest -v

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
pytest -v

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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.10.7-slim-bullseye

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
RUN git clone https://github.com/freqtrade/freqtrade.git /home/freqtrade

WORKDIR /home/freqtrade
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("freqtrade", "freqtrade_7506_to_7396")
class FREQTRADE_7506_TO_7396(Instance):
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
        import json

        # Regex pattern to match test names and their statuses
        pattern = r"(tests\/[^:]+::[^ ]+)\s+(PASSED|FAILED|SKIPPED)|(PASSED|FAILED|SKIPPED)\s+(tests\/[^:]+::[^ ]+)"
        matches = re.findall(pattern, log)
        for match in matches:
            test1, status1, status2, test2 = match
            if test1 and status1:
                test_name = test1.strip()
                status = status1
            elif status2 and test2:
                test_name = test2.strip()
                status = status2
            else:
                continue
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status == "FAILED":
                failed_tests.add(test_name)
            elif status == "SKIPPED":
                skipped_tests.add(test_name)
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
