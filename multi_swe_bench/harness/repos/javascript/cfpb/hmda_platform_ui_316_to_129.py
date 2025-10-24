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
        return "node:18-slim"

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
npm install
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3 python-is-python3
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
apt-get install -y python2
###ACTION_DELIMITER###
apt-get install -y python2.7
###ACTION_DELIMITER###
npm install -g node-gyp
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
npm_config_node_gyp=$(which node-gyp) npm install --legacy-peer-deps
###ACTION_DELIMITER###
rm -rf node_modules && npm config set python python3 && npm install --legacy-peer-deps
###ACTION_DELIMITER###
rm -rf node_modules && export PYTHON=python3 && npm_config_node_gyp=$(which node-gyp) npm install --legacy-peer-deps
###ACTION_DELIMITER###
rm -rf node_modules && npm config set python /usr/bin/python3 && npm_config_node_gyp=$(which node-gyp) npm install --legacy-peer-deps
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && export PYTHON=python3 && npm_config_node_gyp=$(which node-gyp) npm install --legacy-peer-deps
###ACTION_DELIMITER###
echo -e '#!/bin/bash
python3 -c "$(echo "$@" | sed "s/print \(.*\)/print(\1)/")"' > python2_wrapper && chmod +x python2_wrapper
###ACTION_DELIMITER###
export PYTHON=./python2_wrapper && npm install --legacy-peer-deps
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian oldstable main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python2.7
###ACTION_DELIMITER###
npm install --legacy-peer-deps --ignore-engines
###ACTION_DELIMITER###
echo -e '#!/bin/bash
python3 -c "$(echo "$@" | sed "s/print \(.*\)/print(\1)/g")"' > python2_wrapper && chmod +x python2_wrapper && export PYTHON=$(pwd)/python2_wrapper && npm install --legacy-peer-deps
###ACTION_DELIMITER###
npm install node-sass@7 --legacy-peer-deps
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian oldstable main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python2.7 && export PYTHON=python2.7 && npm install --legacy-peer-deps
###ACTION_DELIMITER###
rm -rf node_modules && export PYTHON=python3 && npm_config_node_gyp=$(which node-gyp) npm install --legacy-peer-deps
###ACTION_DELIMITER###
echo -e '#!/bin/bash
python3 -c "$(echo "$@" | sed -E "s/print (.*)/print(\1)/g")"' > python2_wrapper && chmod +x python2_wrapper && export PYTHON=$(pwd)/python2_wrapper && npm install --legacy-peer-deps
###ACTION_DELIMITER###
echo -e '#!/bin/bash
if [ "$1" = "-c" ]; then
    code="$2"
    modified_code=$(echo "$code" | sed -E "s/print (.*)/print(\1)/g")
    python3 -c "$modified_code"
else
    python3 "$@"
fi' > python2_wrapper && chmod +x python2_wrapper && export PYTHON=$(pwd)/python2_wrapper && npm install --legacy-peer-deps
###ACTION_DELIMITER###
npm install --legacy-peer-deps --override node-sass@8.0.0
###ACTION_DELIMITER###
echo -e '#!/bin/bash
if [ "$1" = "-c" ]; then
    code="$2"
    modified_code=$(echo "$code" | sed -E "s/print (.*);/print(\1);/g")
    python3 -c "$modified_code"
else
    python3 "$@"
fi' > python2_wrapper && chmod +x python2_wrapper && export PYTHON=$(pwd)/python2_wrapper && npm install --legacy-peer-deps
###ACTION_DELIMITER###

###ACTION_DELIMITER###
ls -la
###ACTION_DELIMITER###
npm install --legacy-peer-deps --ignore-scripts
###ACTION_DELIMITER###
echo 'npm test -- --verbose' > test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npm test -- --verbose

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
npm test -- --verbose

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
npm test -- --verbose

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

# Choose an appropriate base image based on the project's requirements - replace node:18-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:18-slim

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
RUN git clone https://github.com/cfpb/hmda-platform-ui.git /home/hmda-platform-ui

WORKDIR /home/hmda-platform-ui
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("cfpb", "hmda_platform_ui_316_to_129")
class HMDA_PLATFORM_UI_316_TO_129(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re

        # TODO: Implement the parse_log function
        # Implement the log parsing logic here
        # Regex pattern to match test results (PASS/FAIL/SKIPPED followed by test path)
        pattern = re.compile(r".*(PASS|FAIL|SKIPPED)\s+(__tests__/[^ ]+\.js)")
        for line in log.split("\n"):
            match = pattern.search(line.strip())
            if match:
                status, test_name = match.groups()
                if status == "PASS":
                    passed_tests.add(test_name)
                elif status == "FAIL":
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
