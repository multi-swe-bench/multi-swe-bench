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
                """apt-get update && apt-get install -y software-properties-common && add-apt-repository -y ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.7 python3.7-venv python3.7-dev build-essential libssl-dev libffi-dev libta-lib0 libta-lib-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential wget && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && tar -xzf ta-lib-0.4.0-src.tar.gz && cd ta-lib && ./configure --prefix=/usr/local && make && make install && ldconfig && cd ..
###ACTION_DELIMITER###
python3.7 -m venv .env && source .env/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.7 python3.7-venv python3.7-dev
###ACTION_DELIMITER###
python3.7 -m venv .env && source .env/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
sed -i 's/ccxt==1.33.52/ccxt==1.33.1/' requirements-common.txt && python3.7 -m venv .env && source .env/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
python3.7 -m venv .env && source .env/bin/activate && pip install --upgrade pip && pip install numpy && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
python3.7 -m venv .env && source .env/bin/activate && pip install --upgrade pip && pip install numpy==1.19.1 && pip install TA-Lib==0.4.18 && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
python3.7 -m venv .env && source .env/bin/activate && pip install --upgrade pip && pip install numpy==1.19.1 && pip install --no-build-isolation TA-Lib==0.4.18 && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
python3.7 -m venv .env && source .env/bin/activate && pip install --upgrade pip && pip install wheel && pip install numpy==1.19.1 && pip install --no-build-isolation TA-Lib==0.4.18 && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo -e 'source .env/bin/activate
pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source .env/bin/activate && pip uninstall -y numpy && pip install numpy==1.21.6
###ACTION_DELIMITER###
source .env/bin/activate && pip uninstall -y py_find_1st && pip install --no-binary :all: --no-cache-dir py_find_1st==1.1.4
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source .env/bin/activate
pytest -v --no-header -rA --tb=no -p no:cacheprovider -p no:random-order tests/' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source .env/bin/activate && pip uninstall -y pytest-random-order && echo -e 'source .env/bin/activate
pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source .env/bin/activate
pytest -v --no-header -rA --tb=full tests/rpc/test_rpc_apiserver.py' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source .env/bin/activate
pytest -v --no-header -rA --tb=long tests/rpc/test_rpc_apiserver.py' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source .env/bin/activate && pip uninstall -y markupsafe && pip install markupsafe==1.1.1 && bash test_commands.sh
###ACTION_DELIMITER###
source .env/bin/activate && pip uninstall -y itsdangerous && pip install itsdangerous==1.1.0 && bash test_commands.sh
###ACTION_DELIMITER###
source .env/bin/activate && pip uninstall -y werkzeug && pip install werkzeug==1.0.1 && bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
echo -e 'source .env/bin/activate
pytest -v --no-header -rA --tb=long tests/' > test_commands.sh && chmod +x test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
source .env/bin/activate
pytest -v --no-header -rA --tb=long tests/

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
source .env/bin/activate
pytest -v --no-header -rA --tb=long tests/

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
source .env/bin/activate
pytest -v --no-header -rA --tb=long tests/

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
RUN git clone https://github.com/freqtrade/freqtrade.git /home/freqtrade

WORKDIR /home/freqtrade
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("freqtrade", "freqtrade_3719_to_3682")
class FREQTRADE_3719_TO_3682(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re
        import json

        # Extract PASSED tests
        passed_pattern = r"(\btests/[^:]+::[^ ]+)\s+PASSED"
        passed_matches = re.findall(passed_pattern, log)
        for test in passed_matches:
            passed_tests.add(test)
        # Extract FAILED tests
        failed_pattern = r"FAILED\s+(\btests/[^:]+::[^ ]+)"
        failed_matches = re.findall(failed_pattern, log)
        for test in failed_matches:
            failed_tests.add(test)
        # Extract SKIPPED tests
        skipped_pattern = r"SKIPPED\s+.*?(\btests/[^:]+:\d+)"
        skipped_matches = re.findall(skipped_pattern, log)
        for test in skipped_matches:
            skipped_tests.add(test)
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
