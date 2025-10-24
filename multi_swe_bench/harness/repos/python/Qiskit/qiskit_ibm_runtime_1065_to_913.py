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
pip install -r requirements.txt
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo 'python -m unittest -v' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install qiskit==0.46.0
###ACTION_DELIMITER###
pip install -c constraints.txt -r requirements.txt && pip install -c constraints.txt -r requirements-dev.txt
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install -e . -c constraints.txt
###ACTION_DELIMITER###
pip install runningman==2.1.0
###ACTION_DELIMITER###
pip install qiskit-ibm-runtime==0.22.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y qiskit qiskit-terra qiskit-ibm-runtime qiskit-ibm-provider && pip install -r requirements.txt -r requirements-dev.txt && pip install qiskit-ibm-runtime==0.22.0
###ACTION_DELIMITER###
pip uninstall -y qiskit qiskit-terra qiskit-ibm-runtime qiskit-ibm-provider && pip install qiskit==0.46.0 qiskit-ibm-provider==0.11.0 qiskit-ibm-runtime==0.22.0 && pip install -r requirements.txt -r requirements-dev.txt
###ACTION_DELIMITER###
pip install qiskit==1.0.0 qiskit-ibm-provider==0.11.0 qiskit-ibm-runtime==0.22.0 && pip install -r requirements.txt -r requirements-dev.txt
###ACTION_DELIMITER###
pip install qiskit==1.0.0 qiskit-ibm-provider==0.11.0 qiskit-ibm-runtime==0.22.0 && pip install --no-upgrade -r requirements.txt -r requirements-dev.txt
###ACTION_DELIMITER###
pip uninstall -y qiskit qiskit-terra qiskit-ibm-provider qiskit-ibm-runtime qiskit-aer && pip install qiskit==1.0.0 qiskit-ibm-provider==0.11.0 qiskit-ibm-runtime==0.22.0 qiskit-aer==0.17.0 && pip install -r requirements.txt -r requirements-dev.txt
###ACTION_DELIMITER###
pip uninstall -y qiskit qiskit-ibm-provider qiskit-ibm-runtime qiskit-aer && pip install qiskit==1.1.0 qiskit-ibm-provider==0.11.0 qiskit-ibm-runtime==0.22.0 qiskit-aer==0.17.0 && pip install -r requirements.txt -r requirements-dev.txt
###ACTION_DELIMITER###
pip uninstall -y qiskit qiskit-ibm-provider qiskit-ibm-runtime qiskit-aer runningman && pip install qiskit==2.1.2 qiskit-ibm-provider==0.11.0 qiskit-ibm-runtime==0.41.1 qiskit-aer==0.17.2 runningman==2.2.0 && pip install -r requirements.txt -r requirements-dev.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y qiskit qiskit-ibm-provider qiskit-ibm-runtime qiskit-aer && pip install qiskit==0.46.0 qiskit-ibm-provider==0.11.0 qiskit-ibm-runtime==0.22.0 qiskit-aer==0.17.0 && pip install -r requirements.txt -r requirements-dev.txt
###ACTION_DELIMITER###
pip uninstall -y qiskit qiskit-ibm-provider qiskit-ibm-runtime qiskit-aer && pip install qiskit==0.46.0 qiskit-ibm-provider==0.11.0 qiskit-ibm-runtime==0.21.0 qiskit-aer==0.17.0 && pip install -r requirements.txt -r requirements-dev.txt
###ACTION_DELIMITER###
pip uninstall -y qiskit qiskit-ibm-provider qiskit-ibm-runtime qiskit-aer && pip install qiskit==0.46.0 qiskit-ibm-provider==0.11.0 qiskit-ibm-runtime==0.20.0 qiskit-aer==0.17.0 && pip install -r requirements.txt -r requirements-dev.txt
###ACTION_DELIMITER###
pip uninstall -y qiskit qiskit-ibm-provider qiskit-ibm-runtime qiskit-aer && pip install qiskit==0.46.0 qiskit-ibm-provider==0.11.0 qiskit-ibm-runtime==0.20.0 qiskit-aer==0.12.0 && pip install -r requirements.txt -r requirements-dev.txt
###ACTION_DELIMITER###
pip uninstall -y qiskit qiskit-ibm-provider qiskit-ibm-runtime qiskit-aer && pip install qiskit==0.46.0 qiskit-ibm-provider==0.11.0 qiskit-ibm-runtime==0.20.0 qiskit-aer==0.12.0 && pip install --no-upgrade -r requirements.txt -r requirements-dev.txt
###ACTION_DELIMITER###
pip install qiskit==0.46.0 qiskit-ibm-provider==0.11.0 qiskit-ibm-runtime==0.20.0 qiskit-aer==0.12.0 runningman==2.0.0 && pip install -r requirements.txt -r requirements-dev.txt
###ACTION_DELIMITER###
pip uninstall -y runningman && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y qiskit qiskit-terra qiskit-ibm-runtime qiskit-ibm-provider qiskit-aer && pip install qiskit==0.46.0 qiskit-ibm-provider==0.11.0 qiskit-ibm-runtime==0.20.0 qiskit-aer==0.12.0 && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y qiskit qiskit-terra qiskit-ibm-runtime qiskit-ibm-provider qiskit-aer && pip install qiskit==0.46.0 qiskit-terra==0.46.0 qiskit-ibm-provider==0.11.0 qiskit-ibm-runtime==0.19.0 qiskit-aer==0.12.0 && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libopenblas-dev && pip uninstall -y qiskit qiskit-terra qiskit-ibm-runtime qiskit-ibm-provider qiskit-aer && pip install qiskit==0.46.0 qiskit-terra==0.46.0 qiskit-ibm-provider==0.11.0 qiskit-ibm-runtime==0.19.0 qiskit-aer==0.12.0 && python -c "from qiskit.providers.backend import BackendV1; from qiskit.circuit import QuantumCircuit; from qiskit.providers.fake_provider import FakeQasmSimulator; print('Imports successful')" && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libopenblas-dev libgomp1 && pip uninstall -y qiskit qiskit-terra qiskit-ibm-runtime qiskit-ibm-provider qiskit-aer && pip install --force-reinstall qiskit==0.46.0 qiskit-terra==0.46.0 qiskit-ibm-provider==0.11.0 qiskit-ibm-runtime==0.19.0 qiskit-aer==0.12.0 && python -c "from qiskit.providers.backend import BackendV1; from qiskit.circuit import QuantumCircuit; from qiskit.providers.fake_provider import FakeQasmSimulator; print('Imports successful')" && bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
python -m unittest -v

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
python -m unittest -v

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
python -m unittest -v

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim with actual base image
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
RUN git clone https://github.com/Qiskit/qiskit-ibm-runtime.git /home/qiskit-ibm-runtime

WORKDIR /home/qiskit-ibm-runtime
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Qiskit", "qiskit_ibm_runtime_1065_to_913")
class QISKIT_IBM_RUNTIME_1065_TO_913(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re

        test_name = None
        lines = log.split("\n")
        for line in lines:
            # Strip leading line number (e.g., [123] )
            stripped_line = re.sub(r"^\[\s*\d+\]\s*", "", line).strip()
            # Check if this line is a test name (starts with test_ and has class in parentheses)
            if re.match(r"^test_\w+ \([\w\.]+\)$", stripped_line):
                test_name = stripped_line
            # Check for status in the line (ok, ERROR, skipped)
            status_match = re.search(r"(\.\.\. |^)(ok|ERROR|skipped)$", stripped_line)
            if status_match:
                status = status_match.group(2)
                if test_name:
                    if status == "ok":
                        passed_tests.add(test_name)
                    elif status == "ERROR":
                        failed_tests.add(test_name)
                    elif status == "skipped":
                        skipped_tests.add(test_name)
                    test_name = None  # Reset after processing
            # Check for FAIL lines (e.g., "FAIL: test_name (test.module.Class)")
            fail_match = re.match(r"^FAIL:\s*(test_\w+ \([\w\.]+\))$", stripped_line)
            if fail_match:
                failed_test = fail_match.group(1)
                failed_tests.add(failed_test)
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
