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
                """ls -la
###ACTION_DELIMITER###
ls -la .github
###ACTION_DELIMITER###
ls -la .github/workflows
###ACTION_DELIMITER###
apt-get update && apt-get install -y libssl-dev libbrotli-dev libzstd-dev
###ACTION_DELIMITER###
uv sync --dev
###ACTION_DELIMITER###
apt-get install -y curl && curl -LsSf https://astral.sh/uv/install.sh | sh -s -- --version 0.5.20
###ACTION_DELIMITER###
curl -LsSf https://astral.sh/uv/install.sh | UV_VERSION=0.5.20 sh
###ACTION_DELIMITER###
UV_VERSION=0.5.20 curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH=$HOME/.local/bin:$PATH
###ACTION_DELIMITER###
curl -L https://github.com/astral-sh/uv/releases/download/0.5.20/uv-x86_64-unknown-linux-gnu.tar.gz | tar xz -C ~/.local/bin --strip-components=1 && export PATH=$HOME/.local/bin:$PATH
###ACTION_DELIMITER###
uv --version
###ACTION_DELIMITER###
uv sync --dev
###ACTION_DELIMITER###
echo 'uvx nox -s test-3.10' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -ra --tb=native --durations=10 --strict-config --strict-markers --disable-socket --allow-unix-socket --allow-hosts=localhost,127.0.0.1,::1,127.0.0.0,240.0.0.0 test/' > test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -ra -n auto --tb=native --durations=10 --strict-config --strict-markers --disable-socket --allow-unix-socket --allow-hosts=localhost,127.0.0.1,::1,127.0.0.0,240.0.0.0 test/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo '.venv/bin/pytest -v -ra -n auto --tb=native --durations=10 --strict-config --strict-markers --disable-socket --allow-unix-socket --allow-hosts=localhost,127.0.0.1,::1,127.0.0.0,240.0.0.0 test/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
uv add --dev pytest-xdist && echo 'uv run pytest -v -ra -n auto --tb=native --durations=10 --strict-config --strict-markers --disable-socket --allow-unix-socket --allow-hosts=localhost,127.0.0.1,::1,127.0.0.0,240.0.0.0 test/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
uv run pytest -v -ra -n auto --tb=native --durations=10 --strict-config --strict-markers --disable-socket --allow-unix-socket --allow-hosts=localhost,127.0.0.1,::1,127.0.0.0,240.0.0.0 test/

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
uv run pytest -v -ra -n auto --tb=native --durations=10 --strict-config --strict-markers --disable-socket --allow-unix-socket --allow-hosts=localhost,127.0.0.1,::1,127.0.0.0,240.0.0.0 test/

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
uv run pytest -v -ra -n auto --tb=native --durations=10 --strict-config --strict-markers --disable-socket --allow-unix-socket --allow-hosts=localhost,127.0.0.1,::1,127.0.0.0,240.0.0.0 test/

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

# Choose an appropriate base image based on the project's requirements - replace python:3.10-slim with actual base image
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
RUN git clone https://github.com/urllib3/urllib3.git /home/urllib3

WORKDIR /home/urllib3
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("urllib3", "urllib3_3620_to_3527")
class URLLIB3_3620_TO_3527(Instance):
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
        # Extract test names and their statuses using regular expressions
        # Pattern for test names (includes '::' to ensure full test identifier)
        passed_matches = re.findall(r'.*PASSED (test/.*::.*?)(?:\s|$)', log)
        passed_tests.update(passed_matches)
        failed_matches = re.findall(r'.*FAILED (test/.*::.*?)(?:\s|$)', log)
        failed_tests.update(failed_matches)
        skipped_matches = re.findall(r'.*?SKIPPED (?:\[\d+\] )?(test/(?:.*?::.*?|.*?\.py:\d+))(?:[:\s]|$)', log)
        skipped_tests.update(skipped_matches)
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
