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
        return "python:3.11-slim"

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
python install-poetry.py
###ACTION_DELIMITER###
poetry install
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH"
###ACTION_DELIMITER###
poetry --version
###ACTION_DELIMITER###
python install-poetry.py
###ACTION_DELIMITER###
python install-poetry.py --uninstall
###ACTION_DELIMITER###
python install-poetry.py
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pytest -v tests/
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH" && poetry install
###ACTION_DELIMITER###
pip install cleo==1.0.0a4
###ACTION_DELIMITER###
poetry --version
###ACTION_DELIMITER###
/root/.local/share/pypoetry/venv/bin/pip install cleo==1.0.0a4
###ACTION_DELIMITER###
pip install -e ".[dev]"
###ACTION_DELIMITER###
pip install pytest pytest-cov pytest-mock pre-commit tox pytest-sugar httpretty zipp deepdiff
###ACTION_DELIMITER###
echo 'pytest -v tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install poetry-core>=1.1.0a6
###ACTION_DELIMITER###
echo 'PYTHONPATH=. pytest -v tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install poetry-core==1.1.0a6
###ACTION_DELIMITER###
pip install poetry-core==1.9.1
###ACTION_DELIMITER###
pip install poetry-core==1.1.0a6
###ACTION_DELIMITER###
python install-poetry.py --uninstall && python install-poetry.py && export PATH="/root/.local/bin:$PATH" && poetry install && poetry run pytest -v tests/
###ACTION_DELIMITER###
python install-poetry.py --uninstall && python install-poetry.py --version 1.2.0a2 && export PATH="/root/.local/bin:$PATH" && poetry install && poetry run pytest -v tests/
###ACTION_DELIMITER###
pip install virtualenv==20.4.4 setuptools==58.0.4 && poetry install && poetry run pytest -v tests/
###ACTION_DELIMITER###
pip uninstall -y poetry cleo poetry-core virtualenv setuptools && python install-poetry.py --version 1.2.0a2 && export PATH="/root/.local/bin:$PATH" && poetry install && poetry run pytest -v tests/
###ACTION_DELIMITER###
pip uninstall -y poetry cleo poetry-core virtualenv setuptools && rm -rf /root/.local/share/pypoetry && python install-poetry.py --version 1.2.0a2 && export PATH="/root/.local/bin:$PATH" && poetry install && poetry run pytest -v tests/
###ACTION_DELIMITER###
python -m venv .venv && source .venv/bin/activate && pip install poetry-core==1.1.0a6 cleo==1.0.0a4 crashtest==0.3.0 && pip install -e . && pip install pytest && pytest -v tests/
###ACTION_DELIMITER###
python -m venv .venv && source .venv/bin/activate && pip install poetry-core==1.1.0a6 cleo==1.0.0a4 crashtest>=0.3.0 && pip install -e . && pip install pytest && pytest -v tests/
###ACTION_DELIMITER###
pip install httpretty && pytest -v tests/
###ACTION_DELIMITER###
pip install -e ".[dev]" && pip install urllib3==1.26.15 && pytest -v tests/
###ACTION_DELIMITER###
pip install pytest-mock deepdiff urllib3==1.26.15 && pytest -v tests/
###ACTION_DELIMITER###
echo -e 'source .venv/bin/activate
pytest -v tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
source .venv/bin/activate
pytest -v tests/

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
source .venv/bin/activate
pytest -v tests/

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
source .venv/bin/activate
pytest -v tests/

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

# Choose an appropriate base image based on the project's requirements - replace python:3.11-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.11-slim

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
RUN git clone https://github.com/python-poetry/poetry.git /home/poetry

WORKDIR /home/poetry
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("python-poetry", "poetry_4433_to_3743")
class POETRY_4433_TO_3743(Instance):
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
        passed_tests: set[str] = set()
        failed_tests: set[str] = set()
        skipped_tests: set[str] = set()
        import re

        # Pattern to match test lines with status
        test_pattern = re.compile(
            r"^(?:(.*?)\s+(PASSED|FAILED|SKIPPED)|(PASSED|FAILED|SKIPPED)\s+(.*?))\b(?:\s+\[\s*\d+%\])?"
        )
        for line in log.splitlines():
            line = line.strip()
            match = test_pattern.match(line)
            if match:
                # Extract test name and status from the appropriate groups
                test_name = match.group(1) or match.group(4)
                status = match.group(2) or match.group(3)
                # Clean test name by removing trailing hyphen and extra info
                test_name = test_name.split(" - ")[0].strip()
                if status == "PASSED":
                    passed_tests.add(test_name)
                elif status == "FAILED":
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
