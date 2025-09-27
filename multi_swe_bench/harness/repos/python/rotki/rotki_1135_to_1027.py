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
        return "python:3.9-slim"
    
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
                """sed -i 's/typing-extensions==3.7.4.2/typing-extensions>=3.10.0/' /home/rotki/requirements.txt
###ACTION_DELIMITER###
sed -i 's/setuptools==40.6.2/setuptools>=50.3.2/' /home/rotki/requirements.txt
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y build-essential
###ACTION_DELIMITER###
apt-get install -y libsqlcipher-dev
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
sed -i 's/gevent==1.5a2/gevent==21.12.0/' /home/rotki/requirements.txt
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
apt-get install -y libsecp256k1-dev
###ACTION_DELIMITER###
CFLAGS="-I/usr/include/sqlcipher" LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lsqlcipher" pip install pysqlcipher3==1.0.3 coincurve==13.0.0
###ACTION_DELIMITER###
sed -i 's/pysqlcipher3==1.0.3/pysqlcipher3>=1.2.0/' /home/rotki/requirements.txt
###ACTION_DELIMITER###
CFLAGS="$(pkg-config --cflags sqlcipher)" LDFLAGS="$(pkg-config --libs sqlcipher)" pip install pysqlcipher3>=1.2.0
###ACTION_DELIMITER###
pip check
###ACTION_DELIMITER###
echo 'pytest --no-header -rA --tb=no -p no:cacheprovider -v' > /home/rotki/test_commands.sh && chmod +x /home/rotki/test_commands.sh
###ACTION_DELIMITER###
bash /home/rotki/test_commands.sh
###ACTION_DELIMITER###
pip install -r requirements_dev.txt
###ACTION_DELIMITER###
bash /home/rotki/test_commands.sh
###ACTION_DELIMITER###
echo 'pytest --no-header -rA --tb=no -p no:cacheprovider -p no:typeguard -v' > /home/rotki/test_commands.sh && chmod +x /home/rotki/test_commands.sh
###ACTION_DELIMITER###
bash /home/rotki/test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -rA --tb=no -p no:cacheprovider -p no:typeguard -v' > /home/rotki/test_commands.sh && chmod +x /home/rotki/test_commands.sh
###ACTION_DELIMITER###
bash /home/rotki/test_commands.sh
###ACTION_DELIMITER###
python -c 'import rotkehlchen' 2>&1
###ACTION_DELIMITER###
pytest --collect-only -v
###ACTION_DELIMITER###
pip uninstall -y typeguard
###ACTION_DELIMITER###
pip install setuptools==58.0.0
###ACTION_DELIMITER###
pip install zope-event==4.5.0
###ACTION_DELIMITER###
bash /home/rotki/test_commands.sh
###ACTION_DELIMITER###
pytest --collect-only -v
###ACTION_DELIMITER###
pip install Jinja2==2.11.3
###ACTION_DELIMITER###
bash /home/rotki/test_commands.sh
###ACTION_DELIMITER###
pytest --collect-only -v
###ACTION_DELIMITER###
pip install MarkupSafe==1.1.1
###ACTION_DELIMITER###
pip install Werkzeug==1.0.1
###ACTION_DELIMITER###
echo 'pytest -rA --tb=no -p no:cacheprovider -p no:typeguard -p no:web3 -v' > /home/rotki/test_commands.sh && chmod +x /home/rotki/test_commands.sh
###ACTION_DELIMITER###
bash /home/rotki/test_commands.sh
###ACTION_DELIMITER###
ls -l /home/rotki/rotkehlchen/tests/conftest.py
###ACTION_DELIMITER###
python -c 'from rotkehlchen.tests.fixtures import *' 2>&1
###ACTION_DELIMITER###
pip install itsdangerous==1.1.0
###ACTION_DELIMITER###
bash /home/rotki/test_commands.sh
###ACTION_DELIMITER###
pip install pytest-xdist
###ACTION_DELIMITER###
echo 'pytest -rA --tb=no -p no:cacheprovider -p no:typeguard -p no:web3 -v -n auto' > /home/rotki/test_commands.sh && chmod +x /home/rotki/test_commands.sh
###ACTION_DELIMITER###
bash /home/rotki/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pytest -rA --tb=no -p no:cacheprovider -p no:typeguard -p no:web3 -v -n auto' > /home/rotki/test_commands.sh && chmod +x /home/rotki/test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
pytest -rA --tb=no -p no:cacheprovider -p no:typeguard -p no:web3 -v -n auto

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
pytest -rA --tb=no -p no:cacheprovider -p no:typeguard -p no:web3 -v -n auto

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
pytest -rA --tb=no -p no:cacheprovider -p no:typeguard -p no:web3 -v -n auto

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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.9-slim

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
RUN git clone https://github.com/rotki/rotki.git /home/rotki

WORKDIR /home/rotki
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("rotki", "rotki_1135_to_1027")
class ROTKI_1135_TO_1027(Instance):
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
        # Regex pattern to match test status lines
        pattern = r'\[\s*gw\d+\s*\] \[\s*\d+%\s*\] (PASSED|FAILED|ERROR|SKIPPED) (rotkehlchen/[^:]+::[^ ]+)'
        matches = re.findall(pattern, log)
        for status, test_name in matches:
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ('FAILED', 'ERROR'):
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
        # Add handling for SKIPPED if present in logs
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
