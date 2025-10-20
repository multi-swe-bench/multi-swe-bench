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
                """apt-get update && apt-get install -y clang clang-tidy build-essential curl doxygen gcc-multilib python-virtualenv python-dev thrift-compiler
###ACTION_DELIMITER###
apt-get update && apt-get install -y clang clang-tidy build-essential curl doxygen gcc-multilib python2.7 virtualenv python2-dev thrift-compiler
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye main' >> /etc/apt/sources.list && apt-get update && apt-get install -y clang clang-tidy build-essential curl doxygen gcc-multilib python2.7 python2-dev thrift-compiler
###ACTION_DELIMITER###
make venv
###ACTION_DELIMITER###
curl -O https://bootstrap.pypa.io/pip/2.7/get-pip.py && python2.7 get-pip.py && pip2.7 install virtualenv
###ACTION_DELIMITER###
make venv
###ACTION_DELIMITER###
echo -e '. venv/bin/activate
make test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
. venv/bin/activate && pip install pycodestyle
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '. venv/bin/activate
PYCODESTYLE="pycodestyle --ignore=E741" make test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '. venv/bin/activate
make test PYCODESTYLE="pycodestyle --ignore=E741"' > test_commands.sh
###ACTION_DELIMITER###
echo -e '[pycodestyle]
ignore = E741' > .pycodestyle
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cat /home/codechecker/analyzer/tests/Makefile
###ACTION_DELIMITER###
echo -e '. venv/bin/activate
make test PYCODESTYLE_TEST_CMD="pycodestyle --ignore=E741 bin codechecker_analyzer tests"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '. venv/bin/activate
make test PYCODESTYLE_TEST_CMD="pycodestyle --ignore=E741,W504,E126,E226,W503,E123 bin codechecker_analyzer tests"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
. venv/bin/activate && pip install pylint
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
. venv/bin/activate && pip install nose
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - && echo 'deb http://apt.llvm.org/buster/ llvm-toolchain-buster-7 main' >> /etc/apt/sources.list && apt-get update && apt-get install -y clang-7 clang-tidy-7 && update-alternatives --install /usr/bin/clang clang /usr/bin/clang-7 100 && update-alternatives --install /usr/bin/clang-tidy clang-tidy /usr/bin/clang-tidy-7 100
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | gpg --dearmor -o /usr/share/keyrings/llvm-archive-keyring.gpg && echo 'deb [signed-by=/usr/share/keyrings/llvm-archive-keyring.gpg] http://apt.llvm.org/buster/ llvm-toolchain-buster-7 main' >> /etc/apt/sources.list.d/llvm.list && apt-get update && apt-get install -y clang-7 clang-tidy-7 && update-alternatives --install /usr/bin/clang clang /usr/bin/clang-7 100 && update-alternatives --install /usr/bin/clang-tidy clang-tidy /usr/bin/clang-tidy-7 100
###ACTION_DELIMITER###
apt-get update && apt-get install -t bullseye -y clang-7 clang-tidy-7
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian buster main' >> /etc/apt/sources.list && apt-get update && apt-get install -t buster -y clang-7 clang-tidy-7
###ACTION_DELIMITER###
echo 'deb [trusted=yes] http://archive.debian.org/debian buster main' >> /etc/apt/sources.list && apt-get update && apt-get install -t buster -y clang-7 clang-tidy-7
###ACTION_DELIMITER###
sed -i '/deb http:\/\/deb.debian.org\/debian buster/d' /etc/apt/sources.list && echo 'deb [trusted=yes] http://archive.debian.org/debian buster main' >> /etc/apt/sources.list && echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99allow-old-repos && apt-get update && apt-get install -t buster -y clang-7 clang-tidy-7
###ACTION_DELIMITER###
apt-get update && apt-get install -t buster -y python-yaml && apt-get install -t buster -y clang-7 clang-tidy-7
###ACTION_DELIMITER###
echo -e 'Package: python2.7* libpython2.7* python-yaml clang-7 clang-tidy-7 libllvm7 libstdc++-8-dev libgcc-8-dev
Pin: release n=buster
Pin-Priority: 900' > /etc/apt/preferences.d/buster-pin && apt-get update && apt-get install -y python-yaml clang-7 clang-tidy-7
###ACTION_DELIMITER###
. venv/bin/activate && pip install python-yaml && apt-get update && apt-get install -t buster -y g++-8 && apt-get install -t buster -y clang-7 clang-tidy-7
###ACTION_DELIMITER###
echo -e 'Package: python2.7* libpython2.7* python-yaml
Pin: release n=buster
Pin-Priority: 900' > /etc/apt/preferences.d/buster-python && apt-get update && apt-get install -t buster -y python2.7 python-yaml && apt-get install -t buster -y clang-7 clang-tidy-7
###ACTION_DELIMITER###
. venv/bin/activate && pip install pyyaml==5.4.1 && apt-get update && apt-get install -t buster -y clang-7 clang-tidy-7
###ACTION_DELIMITER###
. venv/bin/activate && apt-get update && apt-get install -t buster -y clang-7
###ACTION_DELIMITER###
wget https://releases.llvm.org/7.0.1/clang+llvm-7.0.1-x86_64-linux-gnu-ubuntu-18.04.tar.xz && tar xvf clang+llvm-7.0.1-x86_64-linux-gnu-ubuntu-18.04.tar.xz && export PATH=$PWD/clang+llvm-7.0.1-x86_64-linux-gnu-ubuntu-18.04/bin:$PATH && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libtinfo5 && bash test_commands.sh
###ACTION_DELIMITER###
. venv/bin/activate && make package && bash test_commands.sh
###ACTION_DELIMITER###
mkdir -p /home/codechecker/web/server/vendor/jsplumb && git clone https://github.com/sporritt/jsPlumb.git /home/codechecker/web/server/vendor/jsplumb && cd /home/codechecker/web/server/vendor/jsplumb && git checkout 2.2.0 && cd /home/codechecker && . venv/bin/activate && make package && bash test_commands.sh
###ACTION_DELIMITER###
git tag && git checkout v2.2.0 && cd /home/codechecker && . venv/bin/activate && make package && bash test_commands.sh
###ACTION_DELIMITER###
cd /home/codechecker/web/server/vendor && rm -rf jsplumb && git clone --depth 1 https://github.com/sporritt/jsPlumb.git jsplumb && cd jsplumb && git checkout 2.2.0 && cd /home/codechecker && . venv/bin/activate && make package && bash test_commands.sh
###ACTION_DELIMITER###
cd /home/codechecker/web/server/vendor && rm -rf jsplumb && git clone https://github.com/sporritt/jsPlumb.git jsplumb && cd jsplumb && git checkout $(git describe --tags $(git rev-list --tags --max-count=1)) && cd /home/codechecker && . venv/bin/activate && make package && bash test_commands.sh
###ACTION_DELIMITER###
cd /home/codechecker/web/server/vendor && rm -rf jsplumb && mkdir -p jsplumb/dist/js && curl -sSfLk https://cdnjs.cloudflare.com/ajax/libs/jsplumb/2.2.0/jsplumb.min.js -o jsplumb/dist/js/jsPlumb-2.2.0-min.js && cd /home/codechecker && . venv/bin/activate && make package && bash test_commands.sh
###ACTION_DELIMITER###
cd /home/codechecker/web/server/vendor && rm -rf jsplumb && git clone https://github.com/jsplumb/jsplumb.git && cd jsplumb && git checkout v2.2.0 && cd ../../../../ && . venv/bin/activate && make package && bash test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
. venv/bin/activate
make test PYCODESTYLE_TEST_CMD="pycodestyle --ignore=E741,W504,E126,E226,W503,E123 bin codechecker_analyzer tests"

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
. venv/bin/activate
make test PYCODESTYLE_TEST_CMD="pycodestyle --ignore=E741,W504,E126,E226,W503,E123 bin codechecker_analyzer tests"

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
. venv/bin/activate
make test PYCODESTYLE_TEST_CMD="pycodestyle --ignore=E741,W504,E126,E226,W503,E123 bin codechecker_analyzer tests"

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
RUN git clone https://github.com/Ericsson/codechecker.git /home/codechecker

WORKDIR /home/codechecker
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Ericsson", "codechecker_1970_to_1862")
class CODECHECKER_1970_TO_1862(Instance):
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
        # Implement the log parsing logic here
        test_pattern = re.compile(r'^(Test .+?) \.\.\. (ok|ERROR|FAILED|SKIPPED)$', re.MULTILINE)
        for match in test_pattern.finditer(log):
            test_name = match.group(1)
            status = match.group(2)
            if status == 'ok':
                passed_tests.add(test_name)
            elif status in ('ERROR', 'FAILED'):
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
