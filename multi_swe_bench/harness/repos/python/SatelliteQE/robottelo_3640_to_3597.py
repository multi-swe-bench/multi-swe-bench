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
                """ls -la
###ACTION_DELIMITER###
cat Makefile
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
cat requirements.txt
###ACTION_DELIMITER###
pip3 install --break-system-packages -r requirements.txt
###ACTION_DELIMITER###
python3 -c 'import nailgun; print("nailgun imported successfully")'
###ACTION_DELIMITER###
echo 'pytest -v -n auto -m "not stubbed" --junit-xml=test-results.xml -rA tests/robottelo tests/foreman' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip3 install --break-system-packages pytest-xdist
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cat README.rst && cat setup.py
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2.7 python-pip
###ACTION_DELIMITER###
apt-get update && apt-get install -y git build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl
###ACTION_DELIMITER###
wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz
###ACTION_DELIMITER###
tar xzf Python-2.7.18.tgz
###ACTION_DELIMITER###
cd Python-2.7.18 && ./configure --prefix=/usr/local --enable-shared && make && make install
###ACTION_DELIMITER###
python2.7 --version
###ACTION_DELIMITER###
echo '/usr/local/lib' > /etc/ld.so.conf.d/python27.conf && ldconfig
###ACTION_DELIMITER###
python2.7 --version
###ACTION_DELIMITER###
wget https://bootstrap.pypa.io/pip/2.7/get-pip.py && python2.7 get-pip.py
###ACTION_DELIMITER###
cd /home/robottelo && pip2.7 install --break-system-packages -r requirements.txt && pip2.7 install --break-system-packages -e .
###ACTION_DELIMITER###
pip2.7 install -r requirements.txt && pip2.7 install -e .
###ACTION_DELIMITER###
sed -i 's|git+https://github.com/SatelliteQE/nailgun.git|git+https://github.com/SatelliteQE/nailgun.git@596a4b5dadbafa849d049f5fd0d54f46ceb9620b|' requirements.txt
###ACTION_DELIMITER###
sed -i 's|git+https://github.com/SatelliteQE/nailgun.git|git+https://github.com/SatelliteQE/nailgun.git@0.32.0#egg=nailgun|' requirements.txt
###ACTION_DELIMITER###
pip2.7 install -r requirements.txt && pip2.7 install -e .
###ACTION_DELIMITER###
sed -i 's|^.*nailgun.*$|git+https://github.com/SatelliteQE/nailgun.git@596a4b5dadbafa849d049f5fd0d54f46ceb9620b#egg=nailgun|' requirements.txt
###ACTION_DELIMITER###
echo 'git+https://github.com/SatelliteQE/nailgun.git@596a4b5dadbafa849d049f5fd0d54f46ceb9620b#egg=nailgun' > requirements.txt && echo '--editable .' >> requirements.txt
###ACTION_DELIMITER###
cat requirements.txt
###ACTION_DELIMITER###
pip2.7 install -r requirements.txt
###ACTION_DELIMITER###
echo 'git+https://github.com/SatelliteQE/nailgun.git@0.30.0#egg=nailgun' > requirements.txt && echo '--editable .' >> requirements.txt && pip2.7 install -r requirements.txt
###ACTION_DELIMITER###
pip2.7 install cython && pip2.7 install -r requirements.txt
###ACTION_DELIMITER###
pip2.7 uninstall -y cython && pip2.7 install cython==0.29.36 && pip2.7 install --no-use-pep517 -r requirements.txt
###ACTION_DELIMITER###
rm -f pyproject.toml && pip2.7 install setuptools==44.1.1 && pip2.7 install -r requirements.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y libssl-dev libffi-dev && pip2.7 install --no-use-pep517 PyYAML==3.13 && pip2.7 install --no-use-pep517 -r requirements.txt
###ACTION_DELIMITER###
pip2.7 install pytest-xdist==1.34.0 && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/-n auto//' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip2.7 uninstall -y fauxfactory && pip2.7 install fauxfactory==2.2.0 && bash test_commands.sh
###ACTION_DELIMITER###
pip2.7 install fauxfactory==2.1.2 && bash test_commands.sh
###ACTION_DELIMITER###
pip2.7 install -r requirements-optional.txt && cp robottelo.properties.sample robottelo.properties && echo 'make test-robottelo' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip2.7 uninstall -y python-bugzilla cachetools && pip2.7 install python-bugzilla==2.5.0 cachetools==2.1.0 && bash test_commands.sh
###ACTION_DELIMITER###
pip2.7 install -U pytest && echo '[pytest]
markers =
    tier1: mark a test as tier1
    tier2: mark a test as tier2
    tier3: mark a test as tier3
    tier4: mark a test as tier4
    run_in_one_thread: mark a test to run in one thread' > pytest.ini && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from cachetools import lru_cache/from cachetools.func import lru_cache/' robottelo/helpers.py && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -s tests/robottelo/' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v -s tests/robottelo/

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
pytest -v -s tests/robottelo/

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
pytest -v -s tests/robottelo/

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
RUN git clone https://github.com/SatelliteQE/robottelo.git /home/robottelo

WORKDIR /home/robottelo
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("SatelliteQE", "robottelo_3640_to_3597")
class ROBOTTELO_3640_TO_3597(Instance):
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

        pattern = re.compile(
            r"^(tests/.*?)\s+(PASSED|FAILED|SKIPPED)\s*$", re.MULTILINE | re.IGNORECASE
        )
        matches = pattern.findall(log)
        for test_name, status in matches:
            if status.upper() == "PASSED":
                passed_tests.add(test_name)
            elif status.upper() == "FAILED":
                failed_tests.add(test_name)
            elif status.upper() == "SKIPPED":
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
