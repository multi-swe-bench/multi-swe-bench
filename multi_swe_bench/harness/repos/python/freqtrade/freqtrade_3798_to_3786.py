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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip python3-venv build-essential libopenblas-dev
###ACTION_DELIMITER###
python3 -m venv .env
###ACTION_DELIMITER###
source .env/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && pip install --upgrade setuptools && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.8 python3.8-venv python3.8-dev
###ACTION_DELIMITER###
python3.8 -m venv .env && source .env/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
sed -i 's/ccxt==1.34.40/ccxt==1.34.1/' requirements.txt && source .env/bin/activate && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && pip install numpy==1.19.2 && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && pip install numpy==1.19.2 && pip install TA-Lib==0.4.18 && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && pip install numpy==1.19.2 && pip install --no-build-isolation TA-Lib==0.4.18 && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get install -y libta-lib0 libta-lib-dev && source .env/bin/activate && pip install wheel && pip install --no-build-isolation TA-Lib==0.4.18 && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get install -y wget build-essential && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && tar -xzf ta-lib-0.4.0-src.tar.gz && cd ta-lib && ./configure --prefix=/usr && make && make install && cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz && source .env/bin/activate && pip install --no-build-isolation TA-Lib==0.4.18 && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && pip install wheel && pip install --upgrade setuptools && pip install --no-build-isolation TA-Lib==0.4.18 && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get install -y liblz4-dev libzstd-dev zlib1g-dev && source .env/bin/activate && pip install --no-build-isolation blosc && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get install -y cmake && source .env/bin/activate && pip install scikit-build && pip install --no-build-isolation blosc && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && pip install --upgrade pip && pip install --verbose --no-build-isolation blosc && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get install -y libsnappy-dev && source .env/bin/activate && pip install --no-build-isolation --verbose blosc && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && pip install --no-build-isolation --verbose blosc==1.9.2 && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get install -y ninja-build && source .env/bin/activate && pip install --no-build-isolation blosc==1.9.2 && pip install -r requirements.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo -e '#!/bin/bash
source .env/bin/activate
pytest -v --no-header -rA --tb=no -p no:cacheprovider' > /home/freqtrade/test_commands.sh && chmod +x /home/freqtrade/test_commands.sh
###ACTION_DELIMITER###
bash /home/freqtrade/test_commands.sh
###ACTION_DELIMITER###
source .env/bin/activate && pip uninstall -y py_find_1st && pip install --no-binary :all: py_find_1st
###ACTION_DELIMITER###
source .env/bin/activate && pip install --no-build-isolation py_find_1st
###ACTION_DELIMITER###
bash /home/freqtrade/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pytest -v/pytest -v -p no:random_order/' /home/freqtrade/test_commands.sh && bash /home/freqtrade/test_commands.sh
###ACTION_DELIMITER###
source .env/bin/activate && pytest -v tests/rpc/test_rpc_apiserver.py
###ACTION_DELIMITER###
source .env/bin/activate && pip install markupsafe==2.0.1 && pytest -v tests/rpc/test_rpc_apiserver.py
###ACTION_DELIMITER###
source .env/bin/activate && pip install itsdangerous==1.1.0 && pytest -v tests/rpc/test_rpc_apiserver.py
###ACTION_DELIMITER###
source .env/bin/activate && pip install werkzeug==1.0.1 && pytest -v tests/rpc/test_rpc_apiserver.py
###ACTION_DELIMITER###
source .env/bin/activate && pip install PyJWT==1.7.1 && pytest -v tests/rpc/test_rpc_apiserver.py
###ACTION_DELIMITER###
sed -i 's/pytest -v/pytest -v -p no:random_order/' /home/freqtrade/test_commands.sh && bash /home/freqtrade/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
source .env/bin/activate
pytest -v -p no:random_order -p no:random_order --no-header -rA --tb=no -p no:cacheprovider

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
#!/bin/bash
source .env/bin/activate
pytest -v -p no:random_order -p no:random_order --no-header -rA --tb=no -p no:cacheprovider

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
#!/bin/bash
source .env/bin/activate
pytest -v -p no:random_order -p no:random_order --no-header -rA --tb=no -p no:cacheprovider

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
RUN git clone https://github.com/freqtrade/freqtrade.git /home/freqtrade

WORKDIR /home/freqtrade
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("freqtrade", "freqtrade_3798_to_3786")
class FREQTRADE_3798_TO_3786(Instance):
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
        # Compile regex patterns for test statuses
        passed_pattern = re.compile(r'(tests/[^:]+::test[^\s]+)\s+PASSED|PASSED\s+(tests/[^:]+::test[^\s]+)')
        failed_pattern = re.compile(r'(tests/[^:]+::test[^\s]+)\s+FAILED|FAILED\s+(tests/[^:]+::test[^\s]+)')
        skipped_pattern = re.compile(r'(tests/[^:]+::test[^\s]+)\s+SKIPPED|SKIPPED\s+(tests/[^:]+::test[^\s]+)')
        # Process each line to extract test names and statuses
        for line in log.split('\n'):
            # Extract passed tests
            match = passed_pattern.search(line)
            if match:
                test_name = match.group(1) if match.group(1) else match.group(2)
                passed_tests.add(test_name.strip())
            # Extract failed tests
            match = failed_pattern.search(line)
            if match:
                test_name = match.group(1) if match.group(1) else match.group(2)
                failed_tests.add(test_name.strip())
            # Extract skipped tests
            match = skipped_pattern.search(line)
            if match:
                test_name = match.group(1) if match.group(1) else match.group(2)
                skipped_tests.add(test_name.strip())
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
