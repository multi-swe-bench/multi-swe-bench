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
cat Makefile
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl -LsSf https://astral.sh/uv/install.sh | sh
###ACTION_DELIMITER###
source /root/.local/bin/env
###ACTION_DELIMITER###
uv pip install hatch
###ACTION_DELIMITER###
uv pip install --system hatch
###ACTION_DELIMITER###
npm install -g pnpm
###ACTION_DELIMITER###
apt-get install -y npm
###ACTION_DELIMITER###
npm install -g pnpm
###ACTION_DELIMITER###
make install-all
###ACTION_DELIMITER###
uv pip install --system -e ".[dev]"
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e

# Run Python tests with verbose mode
 hatch run typos
 hatch run +py=3.12 test-optional:test -v

# Run frontend tests with verbose mode
CI=true pnpm turbo --filter @marimo-team/frontend test -- --run --verbose

# Run end-to-end tests
pnpm run e2e' > test_commands.sh && chmod +x test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e

# Run Python tests with verbose mode
 hatch run typos
 hatch run +py=3.12 test-optional:test -v

# Run frontend tests with verbose mode
CI=true pnpm turbo --filter @marimo-team/frontend test -- --run --verbose

# Run end-to-end tests
pnpm run e2e

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
set -e

# Run Python tests with verbose mode
 hatch run typos
 hatch run +py=3.12 test-optional:test -v

# Run frontend tests with verbose mode
CI=true pnpm turbo --filter @marimo-team/frontend test -- --run --verbose

# Run end-to-end tests
pnpm run e2e

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
set -e

# Run Python tests with verbose mode
 hatch run typos
 hatch run +py=3.12 test-optional:test -v

# Run frontend tests with verbose mode
CI=true pnpm turbo --filter @marimo-team/frontend test -- --run --verbose

# Run end-to-end tests
pnpm run e2e

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
RUN git clone https://github.com/marimo-team/marimo.git /home/marimo

WORKDIR /home/marimo
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("marimo-team", "marimo_5678_to_5548")
class MARIMO_5678_TO_5548(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re

        # Parsing logic here
        # Parse passed tests (e.g., [1182] tests/...::test PASSED)
        passed_pattern = re.compile(r"[.*?] (tests/.*?) PASSED")
        passed_tests.update(passed_pattern.findall(log))
        # Parse failed tests (e.g., [5830] FAILED tests/...::test)
        failed_pattern = re.compile(r"[.*?] FAILED (tests/.*?)(?: |$)")
        failed_tests.update(failed_pattern.findall(log))
        # Parse skipped tests (assumes similar format, adjust if needed)
        skipped_pattern = re.compile(r"[.*?] (tests/.*?) SKIPPED")
        skipped_tests.update(skipped_pattern.findall(log))
        # Parse passed tests
        passed_pattern = re.compile(r"tests/.*? PASSED")
        for match in passed_pattern.findall(log):
            test_name = match.replace(" PASSED", "").strip()
            passed_tests.add(test_name)
        # Parse failed tests
        failed_pattern = re.compile(r"FAILED tests/.*")
        for match in failed_pattern.findall(log):
            test_name = match.replace("FAILED ", "").strip()
            failed_tests.add(test_name)
        # Parse skipped tests
        skipped_pattern = re.compile(r"tests/.*? SKIPPED")
        for match in skipped_pattern.findall(log):
            test_name = match.replace(" SKIPPED", "").strip()
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
