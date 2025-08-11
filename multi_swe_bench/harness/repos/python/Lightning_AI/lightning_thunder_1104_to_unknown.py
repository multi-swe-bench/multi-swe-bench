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
                """pip install looseversion
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
echo 'pytest -v -rA thunder/tests' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -r requirements/test.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgomp1
###ACTION_DELIMITER###
echo 'THUNDER_DRIVER=cpu pytest -v -rA thunder/tests' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgfortran5 libopenblas-dev
###ACTION_DELIMITER###
pip install --pre nvfuser-cu121-torch24
###ACTION_DELIMITER###
pip install nvidia-cudnn-frontend
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y torch && pip install torch==2.4.0
###ACTION_DELIMITER###
echo 'THUNDER_EXECUTORS=nvfuser,torch_compile THUNDER_DEVICE=cpu pytest -v -rA thunder/tests' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'THUNDER_EXECUTORS=torch_compile THUNDER_DEVICE=cpu pytest -v -rA --maxfail=1 thunder/tests' > test_commands.sh
###ACTION_DELIMITER###
echo 'THUNDER_EXECUTORS=torch_compile THUNDER_DEVICE=cpu pytest -v -rA -n auto --maxfail=1 thunder/tests' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'THUNDER_EXECUTORS=torch_compile THUNDER_DEVICE=cpu pytest -v -rA -n auto -m "not cuda" --ignore=thunder/tests/test_cudnn_executor.py thunder/tests' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'THUNDER_EXECUTORS=torch_compile THUNDER_DEVICE=cpu pytest -v -rA -n auto -m "not cuda" --ignore=thunder/tests/test_cudnn_executor.py --deselect thunder/tests/test_autocast.py::test_torch_compile_autocast --deselect thunder/tests/test_inplace_functionalization.py::test_single_tensor_adam_like_torchcompile_cpu_None --deselect thunder/tests/test_torch_compile_executor.py::test_torch_compile_litgpt thunder/tests' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
THUNDER_EXECUTORS=torch_compile THUNDER_DEVICE=cpu pytest -v -rA -n auto -m "not cuda" --ignore=thunder/tests/test_cudnn_executor.py --deselect thunder/tests/test_autocast.py::test_torch_compile_autocast --deselect thunder/tests/test_inplace_functionalization.py::test_single_tensor_adam_like_torchcompile_cpu_None --deselect thunder/tests/test_torch_compile_executor.py::test_torch_compile_litgpt thunder/tests

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
THUNDER_EXECUTORS=torch_compile THUNDER_DEVICE=cpu pytest -v -rA -n auto -m "not cuda" --ignore=thunder/tests/test_cudnn_executor.py --deselect thunder/tests/test_autocast.py::test_torch_compile_autocast --deselect thunder/tests/test_inplace_functionalization.py::test_single_tensor_adam_like_torchcompile_cpu_None --deselect thunder/tests/test_torch_compile_executor.py::test_torch_compile_litgpt thunder/tests

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
THUNDER_EXECUTORS=torch_compile THUNDER_DEVICE=cpu pytest -v -rA -n auto -m "not cuda" --ignore=thunder/tests/test_cudnn_executor.py --deselect thunder/tests/test_autocast.py::test_torch_compile_autocast --deselect thunder/tests/test_inplace_functionalization.py::test_single_tensor_adam_like_torchcompile_cpu_None --deselect thunder/tests/test_torch_compile_executor.py::test_torch_compile_litgpt thunder/tests

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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
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
RUN git clone https://github.com/Lightning-AI/lightning-thunder.git /home/lightning-thunder

WORKDIR /home/lightning-thunder
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Lightning-AI", "lightning-thunder_1104_to_unknown")
class LIGHTNING_THUNDER_1104_TO_UNKNOWN(Instance):
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
        passed_tests = set()  # type: set[str]
        failed_tests = set()  # type: set[str]
        skipped_tests = set()  # type: set[str]
        import re
        # Remove ANSI escape codes
        clean_log = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', log)
        lines = clean_log.split('\n')
        # Use regex to match test names reliably
        test_pattern = re.compile(r'thunder/tests/.*?(?= - |$)')
        for line in lines:
            line = line.strip()
            if 'PASSED' in line:
                match = test_pattern.search(line)
                if match:
                    passed_tests.add(match.group())
            elif 'FAILED' in line:
                match = test_pattern.search(line)
                if match:
                    failed_tests.add(match.group())
            elif 'SKIPPED' in line:
                match = test_pattern.search(line)
                if match:
                    skipped_tests.add(match.group())
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
