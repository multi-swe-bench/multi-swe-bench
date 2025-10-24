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
        return "node:18"
    
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
                """ls -la
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo 'yarn test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
yarn build
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'yarn test -- --verbose --timeout 30000' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'lerna run test --concurrency 1 -- --verbose --timeout 30000' > test_commands.sh
###ACTION_DELIMITER###
echo 'yarn test -- --verbose --timeout 30000' > test_commands.sh
###ACTION_DELIMITER###
echo 'lerna run test --concurrency 1 -- --verbose --timeout 30000' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'yarn test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo 'yarn test -- --verbose --hook-timeout 30000' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'lerna run test --concurrency 1 -- --verbose --hook-timeout 30000' > test_commands.sh
###ACTION_DELIMITER###
echo 'yarn lerna run test --concurrency 1 -- --verbose --hook-timeout 30000' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'npx lerna run test --concurrency 1 -- --verbose --hook-timeout 30000' > test_commands.sh
###ACTION_DELIMITER###
echo 'npx lerna run test --concurrency 1 -- --verbose --hook-timeout 30000' > test_commands.sh
###ACTION_DELIMITER###
echo 'npx lerna run test --concurrency 1 -- --verbose --hook-timeout 30000' > test_commands.sh
###ACTION_DELIMITER###
echo 'npx lerna exec --concurrency 1 -- vitest --run --verbose --hook-timeout 30000' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'VITEST_HOOK_TIMEOUT=30000 yarn test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'yarn test -- -- --hook-timeout 30000 --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo 'yarn test -- -- --verbose --hookTimeout 30000' > test_commands.sh
###ACTION_DELIMITER###
echo 'VITEST_HOOK_TIMEOUT=30000 yarn test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo 'yarn test -- -- --hookTimeout 30000 --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo 'npx lerna run test --concurrency 1 -- --verbose --hookTimeout 30000' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'VITEST_HOOK_TIMEOUT=30000 VITEST_VERBOSE=1 yarn test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'import { defineConfig } from "vitest/config"; export default defineConfig({ test: { hookTimeout: 30000, verbose: true } });' > vitest.config.ts
###ACTION_DELIMITER###
echo 'yarn test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export VITEST_HOOK_TIMEOUT=30000\nexport VITEST_VERBOSE=1\nyarn test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'env VITEST_HOOK_TIMEOUT=30000 VITEST_VERBOSE=1 yarn test -- --hookTimeout 30000' > test_commands.sh
###ACTION_DELIMITER###
echo 'export VITEST_HOOK_TIMEOUT=30000 && yarn test -- --hookTimeout 30000 --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'export VITEST_HOOK_TIMEOUT=30000\nyarn test -- --hookTimeout 30000 --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'export VITEST_HOOK_TIMEOUT=30000\nexport VITEST_VERBOSE=1\nyarn test' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'export VITEST_HOOK_TIMEOUT=30000\nexport VITEST_VERBOSE=1\nyarn test' > test_commands.sh
###ACTION_DELIMITER###
echo 'npx lerna exec -- vitest --run --hookTimeout 30000 --verbose --coverage' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export VITEST_HOOK_TIMEOUT=30000\nyarn test -- --hook-timeout 30000 --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'export VITEST_HOOK_TIMEOUT=30000\nexport VITEST_VERBOSE=1\nyarn test' > test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
export VITEST_HOOK_TIMEOUT=30000
export VITEST_VERBOSE=1
yarn test

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
export VITEST_HOOK_TIMEOUT=30000
export VITEST_VERBOSE=1
yarn test

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
export VITEST_HOOK_TIMEOUT=30000
export VITEST_VERBOSE=1
yarn test

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

# Choose an appropriate base image based on the project's requirements - replace node:18 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:18

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
RUN git clone https://github.com/ChainSafe/lodestar.git /home/lodestar

WORKDIR /home/lodestar
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ChainSafe", "lodestar_6309_to_6155")
class LODESTAR_6309_TO_6155(Instance):
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
        passed_tests = set() # Tests that passed successfully
        failed_tests = set() # Tests that failed
        skipped_tests = set() # Tests that were skipped
        import re
        # Remove ANSI escape codes to simplify parsing
        clean_log = re.sub(r'\x1b\[[0-9;]*m', '', log)
        # Passed tests: match ✓ followed by test file path
        passed_matches = re.findall(r'✓\s+([\w\/\-\.]+\.test\.ts)', clean_log)
        passed_tests = set(passed_matches)
        # Failed tests: match FAIL followed by test file, and test files with errors
        failed_matches = re.findall(r'FAIL\s+([\w\/\-\.]+\.test\.ts)', clean_log)
        # Match test files with compilation errors (e.g., 'test.ts:123:45 - error')
        error_matches = re.findall(r'([\w\/\-\.]+\.test\.ts):\d+:\d+ - error', clean_log)
        failed_tests = set(failed_matches + error_matches)
        # Remove overlap: failed tests cannot be passed
        passed_tests -= failed_tests
        # Skipped tests (no patterns observed in logs)
        skipped_tests = set()
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
