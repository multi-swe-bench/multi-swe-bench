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
cd client && npm install
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip python-is-python3
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2 && export PYTHON=python2 && npm install
###ACTION_DELIMITER###
npm install -g node-gyp@latest && npm install
###ACTION_DELIMITER###
npm install --python=python3
###ACTION_DELIMITER###
sed -i 's/print "%s.%s.%s" % sys.version_info/print("%s.%s.%s" % sys.version_info)/g' node_modules/node-gyp/lib/configure.js && npm install
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm install 16 && nvm use 16 && npm install
###ACTION_DELIMITER###
npm install node-sass --sass-binary-site=https://npm.taobao.org/mirrors/node-sass/ && npm install
###ACTION_DELIMITER###
sed -i 's/print "%s.%s.%s" % sys.version_info/print("%s.%s.%s" % sys.version_info)/g' node_modules/node-gyp/lib/configure.js && npm install
###ACTION_DELIMITER###
sed -i '/node-sass-chokidar/d' package.json && sed -i 's/node-sass-chokidar/sass/g' package.json && npm install
###ACTION_DELIMITER###
npm test -- --verbose
###ACTION_DELIMITER###
npm test -- --verbose --watchAll=false
###ACTION_DELIMITER###
echo 'cd client && npm test -- --verbose --watchAll=false' > /home/renku-ui/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
cd client && npm test -- --verbose --watchAll=false

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
cd client && npm test -- --verbose --watchAll=false

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
cd client && npm test -- --verbose --watchAll=false

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
RUN git clone https://github.com/SwissDataScienceCenter/renku-ui.git /home/renku-ui

WORKDIR /home/renku-ui
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("SwissDataScienceCenter", "renku_ui_1333_to_1042")
class RENKU_UI_1333_TO_1042(Instance):
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
        passed_tests: set[str] = set()
        failed_tests: set[str] = set()
        skipped_tests: set[str] = set()
        import re
        # Parse passed tests: handle test names with parentheses and durations
        passed_pattern = re.compile(r'^\s*✓\s*((?:(?!\(\d+ms\)).)*?)\s*(?:\(\d+ms\))?\s*$', re.MULTILINE)
        for match in passed_pattern.finditer(log):
            test_name = match.group(1).strip()
            if test_name:
                passed_tests.add(test_name)
        # Parse failed tests: handle test names with parentheses and durations
        failed_pattern = re.compile(r'^\s*✕\s*((?:(?!\(\d+ms\)).)*?)\s*(?:\(\d+ms\))?\s*$', re.MULTILINE)
        for match in failed_pattern.finditer(log):
            test_name = match.group(1).strip()
            if test_name:
                failed_tests.add(test_name)
        # Parse skipped tests: handle test names with parentheses and durations
        skipped_pattern = re.compile(r'^\s*(?:→|SKIPPED|○)\s*((?:(?!\(\d+ms\)).)*?)\s*(?:\(\d+ms\))?\s*$', re.MULTILINE)
        for match in skipped_pattern.finditer(log):
            test_name = match.group(1).strip()
            if test_name:
                skipped_tests.add(test_name)
        # Parse suite-level failures (count 1 per failed suite to match summary)
        suite_failure_pattern = re.compile(r'^FAIL\s+(.+?\.test\.js)\s*$', re.MULTILINE)
        suite_failures = set()
        for match in suite_failure_pattern.finditer(log):
            suite_path = match.group(1)
            if f"FAIL {suite_path}" in log and "Test suite failed to run" in log:
                suite_failures.add(suite_path)
        # Add 1 failed test per suite to match summary
        failed_tests.update([f"{s} (suite failed)" for s in suite_failures])
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
