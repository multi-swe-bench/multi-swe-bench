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
        return "python:3.6"
    
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
                """ls -al
###ACTION_DELIMITER###

###ACTION_DELIMITER###
pip install -U setuptools pip && pip install -U -r requirements.txt && pip install -U .
###ACTION_DELIMITER###
pip install -U -r benchmarks/requirements.txt && pip install -U -r docs/requirements.txt && pip install -U attrs==18.1.0 coverage==4.5.1 flake8==3.5.0 isort==4.3.4 mypy==0.600 pycodestyle==2.3.1 pytest==3.6.0 pytest-cov==2.5.1 pytest-isort==0.2.0 pytest-mock==1.10.0 pytest-sugar==0.9.1 && pip install -U msgpack-python==0.5.6 ujson==1.35 email-validator==1.0.3 && pip install -U .
###ACTION_DELIMITER###
echo 'pytest --cov=pydantic --no-header -rA --tb=no -p no:cacheprovider
pip uninstall -y msgpack-python ujson email-validator
pytest --cov=pydantic --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
echo 'pytest --cov=pydantic -rA --tb=no -p no:cacheprovider
pip uninstall -y msgpack-python ujson email-validator
pytest --cov=pydantic -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
pip install -U 'pytest>=4.0.0' 'pytest-cov>=2.6.0'
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
echo 'pytest --cov=pydantic -rA --tb=no -p no:cacheprovider -p no:pytest_isort
pip uninstall -y msgpack-python ujson email-validator
pytest --cov=pydantic -rA --tb=no -p no:cacheprovider -p no:pytest_isort' > test_commands.sh
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y pytest-isort
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
sed -i '/addopts =/s/--isort//' setup.cfg
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest --cov=pydantic -rA --tb=no -p no:cacheprovider -p no:pytest_isort
pip uninstall -y msgpack-python ujson email-validator
pytest --cov=pydantic -rA --tb=no -p no:cacheprovider -p no:pytest_isort

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
pytest --cov=pydantic -rA --tb=no -p no:cacheprovider -p no:pytest_isort
pip uninstall -y msgpack-python ujson email-validator
pytest --cov=pydantic -rA --tb=no -p no:cacheprovider -p no:pytest_isort

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
pytest --cov=pydantic -rA --tb=no -p no:cacheprovider -p no:pytest_isort
pip uninstall -y msgpack-python ujson email-validator
pytest --cov=pydantic -rA --tb=no -p no:cacheprovider -p no:pytest_isort

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
FROM python:3.6

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
RUN git clone https://github.com/pydantic/pydantic.git /home/pydantic

WORKDIR /home/pydantic
RUN git reset --hard
RUN git checkout 9021d94e3193c171be158877f359f402001d88f9

RUN git checkout {pr.base.sha}"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pydantic", "pydantic_v0_9_1")
class PYDANTIC_V0_9_1(Instance):
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
        # Extract PASSED and FAILED test names
        passed_pattern = re.compile(r"PASSED ([^\s]+)")
        failed_pattern = re.compile(r"FAILED ([^\s]+)")
        skipped_pattern = re.compile(r"SKIPPED \[\d+\] ([^:]+):(\d+):")
        for line in log.splitlines():
            m_passed = passed_pattern.search(line)
            if m_passed:
                passed_tests.add(m_passed.group(1))
                continue
            m_failed = failed_pattern.search(line)
            if m_failed:
                failed_tests.add(m_failed.group(1))
                continue
            m_skipped = skipped_pattern.search(line)
            if m_skipped:
                # Map file and line number to function name
                file_path = m_skipped.group(1)
                line_num = int(m_skipped.group(2))
                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        lines = f.readlines()
                    # Find the nearest preceding function definition
                    func_name = None
                    for i in range(line_num-1, -1, -1):
                        match = re.match(r"\s*def (test_[\w\[\]-]+)", lines[i])
                        if match:
                            func_name = match.group(1)
                            break
                    if func_name:
                        skipped_tests.add(f"{file_path}::{func_name}")
                except Exception:
                    # If file can't be read, skip
                    continue
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
