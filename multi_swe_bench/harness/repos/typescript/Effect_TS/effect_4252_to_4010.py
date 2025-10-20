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
        return "node:20-bookworm"
    
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
                """vitest --help
###ACTION_DELIMITER###
pnpm test -- --help
###ACTION_DELIMITER###
npm install -g pnpm@9.10.0
###ACTION_DELIMITER###
pnpm install
###ACTION_DELIMITER###
pnpm test -- --help
###ACTION_DELIMITER###
echo 'pnpm test -- --run --reporter=verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pnpm test -- --run --reporter=verbose --exclude "packages/sql-kysely/test/**/*.test.ts"' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pnpm test -- --run --reporter=verbose --exclude "packages/@effect/sql-kysely/test/**/*.test.ts"' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pnpm test -- --run --reporter=verbose --exclude "packages/sql-kysely/test/**/*.test.ts"' > test_commands.sh
###ACTION_DELIMITER###
echo 'pnpm test -- --run --reporter=verbose --exclude "**/sql-kysely/test/**/*.test.ts"' > test_commands.sh
###ACTION_DELIMITER###
find . -name '*.test.ts' | grep sql-kysely
###ACTION_DELIMITER###
echo 'pnpm test -- --run --reporter=verbose --exclude "packages/sql-kysely/test/**/*.test.ts"' > test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
echo 'pnpm test -- --run --reporter=verbose --exclude "packages/sql-kysely/test/*.test.ts"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pnpm test -- --run --reporter=verbose --exclude "packages/sql-kysely/test/**/*.test.ts"' > test_commands.sh
###ACTION_DELIMITER###
echo 'pnpm test -- --run --reporter=verbose --exclude "**/sql-kysely/test/**/*.test.ts"' > test_commands.sh
###ACTION_DELIMITER###
echo 'pnpm test -- --run --reporter=verbose --exclude "packages/sql-kysely/test/**/*.test.ts"' > test_commands.sh
###ACTION_DELIMITER###
echo 'pnpm test --filter="!@effect/sql-kysely" -- --run --reporter=verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pnpm test --filter="!@effect/sql-kysely" -- --run --reporter=verbose --fake-timers' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/export default {/export default { fakeTimers: true,/' vitest.config.ts
###ACTION_DELIMITER###
echo 'import { defineConfig } from "vitest/config"; export default defineConfig({ test: { fakeTimers: true } });' > vitest.config.ts
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pnpm test --filter="!@effect/sql-kysely" -- --run --reporter=verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'import { defineConfig } from "vitest/config"; export default defineConfig({ test: { fakeTimers: true } });' > packages/effect/vitest.config.ts
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'import { defineConfig } from "vitest/config"; export default defineConfig({ test: { fakeTimers: true }, resolve: { alias: { effect: "./packages/effect/src" } } });' > vitest.config.ts
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'import { defineConfig } from "vitest/config"; import tsconfigPaths from "vite-tsconfig-paths"; export default defineConfig({ test: { fakeTimers: true }, plugins: [tsconfigPaths()] });' > vitest.config.ts
###ACTION_DELIMITER###
pnpm add -D vite-tsconfig-paths
###ACTION_DELIMITER###
pnpm add -Dw vite-tsconfig-paths
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'import { defineConfig } from "vitest/config"; import tsconfigPaths from "vite-tsconfig-paths"; export default defineConfig({ test: { fakeTimers: true }, resolve: { alias: { effect: "./packages/effect/src" } }, plugins: [tsconfigPaths()] });' > vitest.config.ts
###ACTION_DELIMITER###
pnpm build && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pnpm test --filter="!@effect/sql-kysely" -- --run --reporter=verbose --config ../../vitest.config.ts' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'import { defineConfig } from "vitest/config"; import tsconfigPaths from "vite-tsconfig-paths"; import { resolve } from "path"; export default defineConfig({ test: { fakeTimers: true }, resolve: { alias: { effect: resolve(__dirname, "packages/effect/src") } }, plugins: [tsconfigPaths()] });' > vitest.config.ts
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pnpm test --filter="!@effect/sql-kysely" -- --run --reporter=verbose --config ../../vitest.config.ts

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
pnpm test --filter="!@effect/sql-kysely" -- --run --reporter=verbose --config ../../vitest.config.ts

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
pnpm test --filter="!@effect/sql-kysely" -- --run --reporter=verbose --config ../../vitest.config.ts

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

# Choose an appropriate base image based on the project's requirements - replace node:20-bookworm with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:20-bookworm

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
RUN git clone https://github.com/Effect-TS/effect.git /home/effect

WORKDIR /home/effect
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Effect-TS", "effect_4252_to_4010")
class EFFECT_4252_TO_4010(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        pattern = r'packages/effect test:  (✓|FAIL|SKIP)\s+([^\[]*?)\s*$'
        matches = re.findall(pattern, log, re.MULTILINE)
        for status, test_name in matches:
            test_name = test_name.strip()
            if status == '✓':
                passed_tests.add(test_name)
            elif status == 'FAIL':
                failed_tests.add(test_name)
            elif status == 'SKIP':
                skipped_tests.add(test_name)
        # Remove overlapping tests (failed tests take precedence)
        passed_tests -= failed_tests
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
