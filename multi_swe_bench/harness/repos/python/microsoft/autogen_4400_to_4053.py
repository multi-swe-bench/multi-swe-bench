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
ls -la python
###ACTION_DELIMITER###
ls -la python/packages
###ACTION_DELIMITER###
ls -la python/packages/autogen-core
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && uv run pytest -v --no-header -rA --tb=no -p no:cacheprovider ./packages/**/tests' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
cat /home/autogen/test_commands.sh
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
pip install uv
###ACTION_DELIMITER###
cd python && uv sync
###ACTION_DELIMITER###
cd /home/autogen && bash test_commands.sh
###ACTION_DELIMITER###
cd python && uv run pytest -v packages/autogen-ext/tests/test_tools.py
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && shopt -s globstar && uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider ./packages/**/tests' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
cat /home/autogen/test_commands.sh
###ACTION_DELIMITER###
cd /home/autogen && bash test_commands.sh
###ACTION_DELIMITER###
find python/packages -name 'test_tools.py'
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider $(find ./packages -type d -name "tests")' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
cat /home/autogen/test_commands.sh
###ACTION_DELIMITER###
cd /home/autogen && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider $(find ./packages -type f -name "*.py" -path "*/tests/*")' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
cat /home/autogen/test_commands.sh
###ACTION_DELIMITER###
cd /home/autogen && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider --import-mode=importlib $(find ./packages -type f -name "*.py" -path "*/tests/*")' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
cat /home/autogen/test_commands.sh
###ACTION_DELIMITER###
cd /home/autogen && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && PYTHONPATH=./packages uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider --import-mode=importlib $(find ./packages -type f -name "*.py" -path "*/tests/*")' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
cat /home/autogen/test_commands.sh
###ACTION_DELIMITER###
cd /home/autogen && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && PYTHONPATH=./packages uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider $(find ./packages -type f -name "*.py" -path "*/tests/*")' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider $(find ./packages -type d -name "tests")' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
cd /home/autogen && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} +
for test_dir in $(find ./packages -type d -name "tests"); do
  uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider "$test_dir"
done' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
cat /home/autogen/test_commands.sh
###ACTION_DELIMITER###
cd /home/autogen && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && PYTHONPATH=./packages uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider --import-mode=append $(find ./packages -type d -name "tests")' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
cat /home/autogen/test_commands.sh
###ACTION_DELIMITER###
cd /home/autogen && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} +
for test_dir in $(find ./packages -type d -name "tests"); do
  PYTHONPATH=./ uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider --import-mode=importlib "$test_dir"
done' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} +
for test_dir in $(find ./packages -type d -name "tests"); do
  PYTHONPATH=./packages uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider --import-mode=append "$test_dir"
done' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && PYTHONPATH=./ uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider --import-mode=append $(find ./packages -type d -name "tests")' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && PYTHONPATH=./packages uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider --import-mode=append $(find ./packages -type d -name "tests")' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && PYTHONPATH=./packages uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider --import-mode=append $(find ./packages -type d -name "tests")' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && PYTHONPATH=../ uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider --import-mode=importlib $(find ./packages -type d -name "tests")' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} +
for test_dir in $(find ./packages -type d -name "tests"); do
  PYTHONPATH=./packages uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider "$test_dir"
done' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
cd /home/autogen && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && PYTHONPATH=../ uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider --import-mode=append -n auto $(find ./packages -type d -name "tests")' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && PYTHONPATH=./packages uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider --import-mode=append -n 2 $(find ./packages -type d -name "tests")' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && PYTHONPATH=. uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider --import-mode=importlib -n 2 $(find ./packages -type d -name "tests")' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && PYTHONPATH=./packages uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider --import-mode=importlib -n 2 $(find ./packages -type d -name "tests")' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && PYTHONPATH=./packages uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider --import-mode=importlib -n auto $(find ./packages -type d -name "tests")' > /home/autogen/test_commands.sh
###ACTION_DELIMITER###
""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && PYTHONPATH=./packages uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider --import-mode=importlib -n auto $(find ./packages -type d -name "tests")

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
#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && PYTHONPATH=./packages uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider --import-mode=importlib -n auto $(find ./packages -type d -name "tests")

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
#!/bin/bash
cd python && find . -name "__pycache__" -exec rm -rf {} + && PYTHONPATH=./packages uv run pytest -v --no-header -rA --tb=short -p no:cacheprovider --import-mode=importlib -n auto $(find ./packages -type d -name "tests")

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
RUN git clone https://github.com/microsoft/autogen.git /home/autogen

WORKDIR /home/autogen
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("microsoft", "autogen_4400_to_4053")
class AUTOGEN_4400_TO_4053(Instance):
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

        # Regular expressions to match test status lines
        failed_pattern = re.compile(r"^FAILED (.*)$")
        skipped_pattern = re.compile(r"^SKIPPED \[\d+\] (.*?): .*$")
        passed_pattern = re.compile(r"PASSED (.*)$")
        for line in log.split("\n"):
            line = line.strip()
            # Check for failed tests
            failed_match = failed_pattern.match(line)
            if failed_match:
                failed_tests.add(failed_match.group(1))
            # Check for skipped tests
            skipped_match = skipped_pattern.match(line)
            if skipped_match:
                skipped_tests.add(skipped_match.group(1))
            # Check for passed tests
            passed_match = passed_pattern.match(line)
            if passed_match:
                passed_tests.add(passed_match.group(1))
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
