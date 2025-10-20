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
apt-get update && apt-get install -y sudo libatlas3-base curl sqlite3 libhdf5-serial-dev libgomp1 build-essential libssl-dev git libffi-dev libgfortran5 pkg-config cmake gcc
###ACTION_DELIMITER###
cd build_helpers && ./install_ta-lib.sh
###ACTION_DELIMITER###
./install_ta-lib.sh
###ACTION_DELIMITER###
sed -i 's|http://git.savannah.gnu.org|https://git.savannah.gnu.org|g' install_ta-lib.sh
###ACTION_DELIMITER###
./install_ta-lib.sh
###ACTION_DELIMITER###
sed -i '11,12 s/^/#/' install_ta-lib.sh
###ACTION_DELIMITER###
./install_ta-lib.sh
###ACTION_DELIMITER###
sed -i '11,12d' install_ta-lib.sh
###ACTION_DELIMITER###
./install_ta-lib.sh
###ACTION_DELIMITER###
cd .. && pip install --upgrade pip && pip install numpy && pip install -r requirements.txt -r requirements-dev.txt -r requirements-hyperopt.txt && pip install -e .
###ACTION_DELIMITER###
sed -i 's/ccxt==1.92.52/ccxt @ git+https://github.com/ccxt/ccxt.git@1.92.52/' requirements.txt
###ACTION_DELIMITER###
sed -i 's|ccxt==1.92.52|ccxt @ git+https://github.com/ccxt/ccxt.git@1.92.52|' requirements.txt
###ACTION_DELIMITER###
pip install --upgrade pip && pip install numpy && pip install -r requirements.txt -r requirements-dev.txt -r requirements-hyperopt.txt && pip install -e .
###ACTION_DELIMITER###
sed -i 's|ccxt @ git+https://github.com/ccxt/ccxt.git@1.92.52|ccxt @ git+https://github.com/ccxt/ccxt.git@v1.92.52|' requirements.txt && pip install -r requirements.txt -r requirements-dev.txt -r requirements-hyperopt.txt && pip install -e .
###ACTION_DELIMITER###
sed -i 's|ccxt @ git+https://github.com/ccxt/ccxt.git@v1.92.52|ccxt|' requirements.txt && pip install -r requirements.txt -r requirements-dev.txt -r requirements-hyperopt.txt && pip install -e .
###ACTION_DELIMITER###
apt-get update && apt-get install -y libblosc-dev && pip install TA-Lib blosc && pip install -r requirements.txt -r requirements-dev.txt -r requirements-hyperopt.txt && pip install -e .
###ACTION_DELIMITER###
ldconfig -p | grep ta_lib && apt-get install -y libblosc-dev && pip install TA-Lib --global-option=build_ext --global-option=-L/usr/local/lib && pip install blosc --install-option=--use-system-blosc && pip install -r requirements.txt -r requirements-dev.txt -r requirements-hyperopt.txt && pip install -e .
###ACTION_DELIMITER###
pip uninstall -y TA-Lib && pip install TA-Lib==0.4.24 --global-option=build_ext --global-option=-L/usr/local/lib && pip install blosc --config-settings=--use-system-blosc && pip install -r requirements.txt -r requirements-dev.txt -r requirements-hyperopt.txt && pip install -e .
###ACTION_DELIMITER###
pip install numpy==1.23.2 && pip install TA-Lib==0.6.6 --global-option=build_ext --global-option=-L/usr/local/lib && pip install -r requirements.txt -r requirements-dev.txt -r requirements-hyperopt.txt && pip install -e .
###ACTION_DELIMITER###
apt-get update && apt-get install -y autoconf automake libtool && pip install numpy==1.23.2 && pip install TA-Lib==0.6.6 --global-option=build_ext --global-option=-L/usr/local/lib && pip install -r requirements.txt -r requirements-dev.txt -r requirements-hyperopt.txt && pip install -e .
###ACTION_DELIMITER###
pip install Cython==0.29.36 && pip install TA-Lib==0.4.24 --global-option=build_ext --global-option=-L/usr/local/lib --global-option=-I/usr/local/include && pip install -r requirements.txt -r requirements-dev.txt -r requirements-hyperopt.txt && pip install -e .
###ACTION_DELIMITER###
pip install blosc --config-settings=--use-system-blosc && pip install -r requirements.txt -r requirements-dev.txt -r requirements-hyperopt.txt && pip install -e .
###ACTION_DELIMITER###
pip install blosc --config-settings=use-system-blosc=True && pip install -r requirements.txt -r requirements-dev.txt -r requirements-hyperopt.txt && pip install -e .
###ACTION_DELIMITER###
export CMAKE_ARGS="-DCMAKE_POLICY_VERSION_MINIMUM=3.5" && pip install blosc && pip install -r requirements.txt -r requirements-dev.txt -r requirements-hyperopt.txt && pip install -e .
###ACTION_DELIMITER###
pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/
###ACTION_DELIMITER###
pytest -v --no-header -rA --tb=no -p no:cacheprovider -p no:random_order tests/
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider -p no:random_order tests/' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v --no-header -rA --tb=no -p no:cacheprovider -p no:random_order tests/

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider -p no:random_order tests/

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider -p no:random_order tests/

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

# Choose an appropriate base image based on the project's requirements - replace python:3.10-slim with actual base image
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
RUN git clone https://github.com/freqtrade/freqtrade.git /home/freqtrade

WORKDIR /home/freqtrade
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("freqtrade", "freqtrade_7298_to_7258")
class FREQTRADE_7298_TO_7258(Instance):
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
        # Parse log content using regex patterns
        pattern = r'(PASSED|FAILED|SKIPPED)\s+(tests/[\w/\.::\[\]-]+)|(tests/[\w/\.::\[\]-]+)\s+(PASSED|FAILED|SKIPPED)'
        matches = re.findall(pattern, log)
        for match in matches:
            status1, test1, test2, status2 = match
            if status1 and test1:
                status = status1
                test = test1
            else:
                status = status2
                test = test2
            if status == 'PASSED':
                passed_tests.add(test)
            elif status == 'FAILED':
                failed_tests.add(test)
            elif status == 'SKIPPED':
                skipped_tests.add(test)
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
