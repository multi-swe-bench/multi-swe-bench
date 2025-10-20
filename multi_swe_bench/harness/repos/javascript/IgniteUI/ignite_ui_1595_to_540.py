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
                """ls
###ACTION_DELIMITER###
node -v
###ACTION_DELIMITER###
npm install -g npm@6
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
npm install -g grunt-cli
###ACTION_DELIMITER###
bower install --allow-root
###ACTION_DELIMITER###
npm install -g bower
###ACTION_DELIMITER###
bower install --allow-root
###ACTION_DELIMITER###
grunt qunit --verbose
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
###ACTION_DELIMITER###
nvm install 10
###ACTION_DELIMITER###
rm -rf node_modules npm-shrinkwrap.json && npm install
###ACTION_DELIMITER###
grunt qunit --verbose --stack
###ACTION_DELIMITER###
npm install grunt-qunit-istanbul@latest
###ACTION_DELIMITER###
npm install grunt-qunit-istanbul@0.8.0
###ACTION_DELIMITER###
npm install grunt-qunit-istanbul@0.6.0
###ACTION_DELIMITER###
npm uninstall phantomjs && npm install phantomjs-prebuilt
###ACTION_DELIMITER###
grunt qunit --verbose --stack
###ACTION_DELIMITER###
sed -i '57s/unlink();/unlink(function() {});/' node_modules/grunt-lib-phantomjs-istanbul/lib/phantomjs.js
###ACTION_DELIMITER###
grunt qunit --verbose --stack
###ACTION_DELIMITER###
sed -i '140s/fs.writeFile(/fs.writeFile(..., function() {});/' build/ReporterQUnit.js
###ACTION_DELIMITER###
grunt qunit --verbose --stack
###ACTION_DELIMITER###
sed -i '140s/);/, function() {});/' build/ReporterQUnit.js
###ACTION_DELIMITER###
grunt qunit --verbose --stack
###ACTION_DELIMITER###
sed -i '140s/fs.writeFile(..., function() {}, function() {});/fs.writeFile("./qunit/err", "Failed due to an error", function() {});/' build/ReporterQUnit.js
###ACTION_DELIMITER###
sed -i '140s|fs.writeFile(..., function() {}, function() {});|fs.writeFile("./qunit/err", "Failed due to an error", function() {});|' build/ReporterQUnit.js
###ACTION_DELIMITER###
grunt qunit --verbose --stack
###ACTION_DELIMITER###
sed -i '140s|.*|fs.writeFile("./qunit/err", "Failed due to an error", function() {});|' build/ReporterQUnit.js
###ACTION_DELIMITER###
sed -i '140c fs.writeFile("./qunit/err", "Failed due to an error", function() {});' build/ReporterQUnit.js
###ACTION_DELIMITER###
grunt qunit --verbose --stack
###ACTION_DELIMITER###
echo 'grunt qunit --verbose' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
grunt qunit --verbose

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
grunt qunit --verbose

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
grunt qunit --verbose

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
RUN git clone https://github.com/IgniteUI/ignite-ui.git /home/ignite-ui

WORKDIR /home/ignite-ui
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("IgniteUI", "ignite_ui_1595_to_540")
class IGNITE_UI_1595_TO_540(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        import json
        # Remove ANSI escape codes from log content
        cleaned_log = re.sub(r'\x1b\[[0-9;]*m', '', log)
        # Split lines and extract test names by splitting on '...'
        for line in cleaned_log.split('\n'):
            line = line.strip()
            if '...' in line:
                parts = line.split('...', 1)
                if len(parts) == 2:
                    test_part, status_part = parts
                    # Extract passed tests
                    if 'OK' in status_part:
                        test_name = re.sub(r'^\s*\[\s*\d+\]\s*', '', test_part).strip()
                        if test_name:
                            passed_tests.add(test_name)
                    # Extract failed tests
                    elif 'ERROR' in status_part or 'FAILED' in status_part:
                        test_name = re.sub(r'^\s*\[\s*\d+\]\s*', '', test_part).strip()
                        if test_name:
                            failed_tests.add(test_name)
        # Add handling for SKIPPED if present in logs
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
