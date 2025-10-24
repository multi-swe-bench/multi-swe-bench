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
        return "ubuntu:22.04"

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
apt-get update
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && apt-get install -y nodejs
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
apt-get remove -y nodejs && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && apt-get install -y nodejs
###ACTION_DELIMITER###
apt-get remove -y libnode72 && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && apt-get install -y nodejs
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
yarn i
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo -e 'yarn workspace shared build
concurrently "yarn test:backend --verbose" "yarn test:frontend --verbose"' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn workspace shared build\nyarn run concurrently "yarn test:backend --verbose" "yarn test:frontend --verbose"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn workspace shared build\nconcurrently "yarn workspace backend test --verbose" "yarn workspace frontend test --verbose"' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn workspace shared build\nconcurrently "yarn workspace backend test -v" "yarn workspace frontend test -v"' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn workspace shared build\nyarn run concurrently "yarn workspace backend test -- --verbose" "yarn workspace frontend test -- --verbose"' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn workspace shared build\nyarn run concurrently "yarn workspace backend test -v" "yarn workspace frontend test -v"' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn workspace shared build\nyarn run concurrently "yarn workspace backend test" "yarn workspace frontend test"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn workspace shared build\nyarn test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn workspace shared build\nyarn prisma:generate\nyarn test:backend --run\nyarn test:frontend --run' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn workspace shared build\nyarn prisma:generate\nyarn workspace backend test --run\nyarn workspace frontend test --run' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn workspace shared build\nyarn prisma:generate\ncd src/backend && npx prisma migrate reset --force && cd ../../\nyarn test:backend --run\nyarn test:frontend --run' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn workspace shared build\nyarn prisma:generate\nyarn workspace backend test --run\nyarn workspace frontend test --run' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn workspace shared build\nyarn prisma:generate\nCI=true yarn workspace backend test --run\nCI=true yarn workspace frontend test --run' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn prisma:generate\nCI=true yarn test:backend --run\nCI=true yarn test:frontend --run' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn prisma:generate\nCI=true yarn test --run' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn prisma:generate\nCI=true yarn test:backend -- --run\nCI=true yarn test:frontend -- --run' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn prisma:generate\nyarn workspace shared build\nyarn run concurrently "yarn test:backend --run" "yarn test:frontend --run"' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn prisma:generate
CI=true yarn test' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn prisma:generate
CI=true yarn test:backend --run
CI=true yarn test:frontend --run' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn workspace shared build\nyarn prisma:generate\nCI=true yarn run concurrently "yarn test:backend -- --run" "yarn test:frontend -- --run"' > test_commands.sh
###ACTION_DELIMITER###
echo 'CI=true yarn test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn workspace shared build
cd src/backend && npx prisma generate && cd ../../
CI=true yarn test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn workspace shared build
cd src/backend && npx prisma generate && cd ../../
CI=true yarn test

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
yarn workspace shared build
cd src/backend && npx prisma generate && cd ../../
CI=true yarn test

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
yarn workspace shared build
cd src/backend && npx prisma generate && cd ../../
CI=true yarn test

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:22.04 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:22.04

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
RUN git clone https://github.com/Northeastern-Electric-Racing/FinishLine.git /home/FinishLine

WORKDIR /home/FinishLine
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Northeastern-Electric-Racing", "FinishLine_1237_to_1193")
class FINISHLINE_1237_TO_1193(Instance):
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
        passed_tests = set[str]()
        failed_tests = set[str]()
        skipped_tests = set[str]()
        import re
        import json

        # Remove ANSI escape codes
        clean_log = re.sub(r"\x1b\[[0-9;]*m", "", log)
        # Extract passed tests
        passed_pattern = re.compile(r"✓\s+([^(]+?)\s+\(")
        passed_matches = passed_pattern.findall(clean_log)
        passed_tests = set(match.strip() for match in passed_matches)
        # Extract failed tests
        failed_pattern = re.compile(r"(?:FAIL|❯)\s+(.+?)(?=:\d|\\n)")
        failed_matches = failed_pattern.findall(clean_log)
        failed_tests = set(match.strip() for match in failed_matches)
        # Extract skipped tests
        skipped_pattern = re.compile(r"❯\s+([^(]+?)\s+\(0 test\)")
        skipped_matches = skipped_pattern.findall(clean_log)
        skipped_tests = set(match.strip() for match in skipped_matches)
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
