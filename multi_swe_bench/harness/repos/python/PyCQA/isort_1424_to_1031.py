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
                """ls
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH"
###ACTION_DELIMITER###
poetry install
###ACTION_DELIMITER###
sed -i 's/"pip-shims<=0.3.4"/"pip-shims"/' pyproject.toml
###ACTION_DELIMITER###
poetry install
###ACTION_DELIMITER###
poetry lock
###ACTION_DELIMITER###
sed -i 's/\[tool.poetry.dev-dependencies\]/\[tool.poetry.group.dev.dependencies\]/' pyproject.toml
###ACTION_DELIMITER###
poetry lock
###ACTION_DELIMITER###
rm poetry.lock && poetry lock
###ACTION_DELIMITER###
poetry install
###ACTION_DELIMITER###
echo 'poetry run pytest -v' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
sed -i 's/black = {version = "^20.08b1", allow-prereleases = true}/black = {version = "^22.3.0", allow-prereleases = true}/' pyproject.toml
###ACTION_DELIMITER###
poetry lock && poetry install
###ACTION_DELIMITER###
sed -i 's/black = {version = "^22.3.0", allow-prereleases = true}/black = {version = "^20.08b1", allow-prereleases = true}/' pyproject.toml
###ACTION_DELIMITER###
poetry lock && poetry install
###ACTION_DELIMITER###
echo 'typed_ast = "1.4.3"' >> pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3-dev build-essential && poetry add typed_ast@1.5.4
###ACTION_DELIMITER###
poetry add typed-ast@1.4.3 && poetry lock && poetry install
###ACTION_DELIMITER###
sed -i '/\[tool.poetry.group.dev.dependencies\]/a typed-ast = "1.4.3"' pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
sed -i 's/mypy = "^0.761.0"/mypy = "^0.900"/' pyproject.toml && poetry remove typed_ast && poetry add --no-binary :all: typed_ast@1.5.4 && poetry lock && poetry install
###ACTION_DELIMITER###
poetry run pip install --no-binary :all: typed_ast==1.5.4
###ACTION_DELIMITER###
poetry run pip install --no-binary :all: typed_ast==1.4.3
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
sed -i '/example_isort_formatting_plugin/d' pyproject.toml && sed -i 's/black = {version = "^20.08b1", allow-prereleases = true}/black = {version = "^21.0", allow-prereleases = true}/' pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
sed -i 's/python = "^3.6"/python = ">=3.6.2,<3.10"/' pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
./test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
poetry run pytest -v

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
poetry run pytest -v

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
poetry run pytest -v

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
RUN git clone https://github.com/PyCQA/isort.git /home/isort

WORKDIR /home/isort
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("PyCQA", "isort_1424_to_1031")
class ISORT_1424_TO_1031(Instance):
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
        passed_tests = set[str]() # Tests that passed successfully
        failed_tests = set[str]() # Tests that failed
        skipped_tests = set[str]() # Tests that were skipped
        import re
        # Regex patterns to match both detailed test lines and summary lines
        pattern_detailed = re.compile(r'tests/.*?::([^-\s]+)\s+(PASSED|FAILED|SKIPPED)\b')
        pattern_summary = re.compile(r'\[\d+\]\s+(PASSED|FAILED|SKIPPED)\s+tests/.*?::([^-\s]+)(?=[\s-]|$)')
        # Extract matches from both patterns
        matches_detailed = pattern_detailed.findall(log)
        matches_summary = pattern_summary.findall(log)
        # Process detailed matches (test_name, status)
        for test_name, status in matches_detailed:
            test_name = test_name.strip()
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
        # Process summary matches (status, test_name)
        for status, test_name in matches_summary:
            test_name = test_name.strip()
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
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
