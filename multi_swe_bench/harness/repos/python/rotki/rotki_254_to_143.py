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
                """apt-get update && apt-get install -y software-properties-common && add-apt-repository -y ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.8 python3.8-venv python3.8-dev sqlcipher libsqlcipher-dev libssl-dev libffi-dev libpq-dev libsecp256k1-dev libev-dev libgmp-dev
###ACTION_DELIMITER###
python3.8 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
apt-get install -y build-essential
###ACTION_DELIMITER###
source venv/bin/activate && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip install --only-binary=coincurve coincurve==7.1.0
###ACTION_DELIMITER###
sed -i 's/coincurve==7.1.0/coincurve==13.0.0/' requirements.txt && source venv/bin/activate && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip install typed-ast==1.4.3 && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && TYPED_AST_WITHOUT_PY2=1 pip install --force-reinstall typed-ast==1.4.3
###ACTION_DELIMITER###
source venv/bin/activate && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && TYPED_AST_WITHOUT_PY2=1 pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip install --only-binary=typed-ast typed-ast==1.4.3 && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
export TYPED_AST_WITHOUT_PY2=1 && source venv/bin/activate && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
export TYPED_AST_WITHOUT_PY2=1 && source venv/bin/activate && pip install typed-ast==1.5.4 && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
sed -i '/typed-ast/d' requirements.txt requirements_dev.txt && source venv/bin/activate && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && export TYPED_AST_WITHOUT_PY2=1 && pip install typed-ast==1.4.3 && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && export TYPED_AST_WITHOUT_PY2=1 && pip install --no-binary=typed-ast typed-ast==1.4.3 && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip install --only-binary=typed-ast typed-ast==1.4.3 && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip download typed-ast==1.4.3 --no-deps && tar xzf typed-ast-1.4.3.tar.gz && cd typed-ast-1.4.3 && sed -i 's/ext_modules=ext_modules/ext_modules=[ext for ext in ext_modules if not ext.name.startswith("_ast27")]/' setup.py && pip install . && cd .. && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip download --no-binary :all: typed-ast==1.4.3 && tar xzf typed-ast-1.4.3.tar.gz && cd typed-ast-1.4.3 && sed -i 's/ext_modules=ext_modules/ext_modules=[ext for ext in ext_modules if not ext.name.startswith("_ast27")]/' setup.py && pip install . && cd .. && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip download --no-binary :all: typed-ast==1.4.3 && tar xzf typed_ast-1.4.3.tar.gz && cd typed-ast-1.4.3 && sed -i 's/ext_modules=ext_modules/ext_modules=[ext for ext in ext_modules if not ext.name.startswith("_ast27")]/' setup.py && pip install . && cd .. && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip download --no-binary :all: typed-ast==1.4.3 && tar xzf typed_ast-1.4.3.tar.gz && cd typed_ast-1.4.3 && sed -i 's/ext_modules=ext_modules/ext_modules=[ext for ext in ext_modules if not ext.name.startswith("_ast27")]/' setup.py && pip install . && cd .. && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && sed -i '/typed-ast/d' requirements.txt requirements_dev.txt && pip download --no-binary :all: typed-ast==1.4.3 && tar xzf typed_ast-1.4.3.tar.gz && cd typed_ast-1.4.3 && sed -i 's/ext_modules=ext_modules/ext_modules=[ext for ext in ext_modules if not ext.name.startswith("_ast27")]/' setup.py && pip install . && cd .. && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && sed -i '/typed-ast/d' requirements.txt requirements_dev.txt && pip download --no-binary :all: typed-ast==1.4.3 && tar xzf typed_ast-1.4.3.tar.gz && cd typed_ast-1.4.3 && sed -i 's/ext_modules=ext_modules/ext_modules=[ext for ext in ext_modules if not ext.name.startswith("_ast27")]/' setup.py && pip install . && cd .. && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && sed -i '/typed-ast/d' requirements.txt requirements_dev.txt && pip download --no-binary :all: typed-ast==1.4.3 && tar xzf typed_ast-1.4.3.tar.gz && cd typed_ast-1.4.3 && sed -i 's/ext_modules=ext_modules/ext_modules=[ext for ext in ext_modules if not ext.name.startswith("_ast27")]/' setup.py && pip install . && cd .. && pip install -r requirements.txt -r requirements_dev.txt --no-upgrade
###ACTION_DELIMITER###
source venv/bin/activate && sed -i '/typed-ast/d' requirements.txt requirements_dev.txt && pip download --no-binary :all: typed-ast==1.4.3 && tar xzf typed_ast-1.4.3.tar.gz && cd typed_ast-1.4.3 && sed -i 's/ext_modules=ext_modules/ext_modules=[ext for ext in ext_modules if not ext.name.startswith("_ast27")]/' setup.py && pip install --force-reinstall . && cd .. && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip download --no-binary :all: typed-ast==1.4.3 && tar xzf typed_ast-1.4.3.tar.gz && cd typed_ast-1.4.3 && sed -i 's/ext_modules=ext_modules/ext_modules=[ext for ext in ext_modules if not ext.name.startswith("_ast27")]/' setup.py && pip wheel . -w ../ && cd .. && pip install typed_ast-1.4.3-cp38-cp38-linux_x86_64.whl && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip download --no-binary :all: typed-ast==1.4.3 && tar xzf typed_ast-1.4.3.tar.gz && cd typed_ast-1.4.3 && sed -i 's/ext_modules=ext_modules/ext_modules=[ext for ext in ext_modules if not ext.name.startswith("_ast27")]/' setup.py && pip wheel . -w ../ && cd .. && pip install --force-reinstall typed_ast-1.4.3-cp38-cp38-linux_x86_64.whl && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && sed -i '/typed-ast/d' requirements.txt requirements_dev.txt && pip download --no-binary :all: typed-ast==1.4.3 && tar xzf typed_ast-1.4.3.tar.gz && cd typed_ast-1.4.3 && sed -i 's/ext_modules=ext_modules/ext_modules=[ext for ext in ext_modules if not ext.name.startswith("_ast27")]/' setup.py && pip wheel . -w ../ && cd .. && pip install --force-reinstall typed_ast-1.4.3-cp38-cp38-linux_x86_64.whl && pip install -r requirements.txt -r requirements_dev.txt
###ACTION_DELIMITER###
echo 'pytest -v' > /home/rotki/test_commands.sh && chmod +x /home/rotki/test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && bash /home/rotki/test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install pytest && bash /home/rotki/test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install gevent==1.3.6 && bash /home/rotki/test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install greenlet==0.4.16 && pip install gevent==1.3.6 && bash /home/rotki/test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install -r requirements.txt -r requirements_dev.txt && bash /home/rotki/test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && echo 'typed-ast==1.4.3' >> requirements.txt && pip install -r requirements.txt -r requirements_dev.txt --no-upgrade && bash /home/rotki/test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip download --no-binary :all: typed-ast==1.4.3 && tar xzf typed_ast-1.4.3.tar.gz && cd typed_ast-1.4.3 && sed -i 's/ext_modules=ext_modules/ext_modules=[ext for ext in ext_modules if not ext.name.startswith("_ast27")]/' setup.py && pip wheel . -w ../ && cd .. && pip install --force-reinstall typed_ast-1.4.3-cp38-cp38-linux_x86_64.whl && pip install -r requirements.txt -r requirements_dev.txt --find-links .
###ACTION_DELIMITER###
sed -i 's/mypy==0.641/mypy==0.990/' requirements_dev.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip install -r requirements.txt -r requirements_dev.txt && bash /home/rotki/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pycryptodome==3.6.6/pycryptodome==3.18.0/' requirements.txt && sed -i 's/pycryptodomex==3.6.6/pycryptodomex==3.18.0/' requirements.txt && source venv/bin/activate && pip install -r requirements.txt -r requirements_dev.txt && bash /home/rotki/test_commands.sh""",
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
RUN git clone https://github.com/rotki/rotki.git /home/rotki

WORKDIR /home/rotki
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("rotki", "rotki_254_to_143")
class ROTKI_254_TO_143(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re

        # Regex pattern to match test names and their statuses (handles both 'test status' and 'status test' formats)
        pattern = re.compile(
            r"(.+?::test_.+?) (FAILED|PASSED|ERROR|SKIPPED)|(FAILED|PASSED|ERROR|SKIPPED) (.+?::test_.+?)"
        )
        # Split log into lines
        lines = log.split("\n")
        for line in lines:
            match = pattern.search(line)
            if match:
                # Extract test name and status from the match groups
                test_name = match.group(1) if match.group(1) else match.group(4)
                status = match.group(2) if match.group(2) else match.group(3)
                if test_name and status:
                    test_name = test_name.strip()
                    status = status.strip()
                    # Classify the test based on status
                    if status == "PASSED":
                        passed_tests.add(test_name)
                    elif status in ("FAILED", "ERROR"):
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
