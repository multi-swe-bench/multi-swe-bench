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
        return "node:18-bullseye"

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
npm config set registry https://registry.npmjs.org/
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
npm config list
###ACTION_DELIMITER###
sed -i 's|https://npm.lisk.com|https://registry.npmjs.org|g' package-lock.json
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
apt-get update && apt-get install -y libudev-dev
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
source $HOME/.nvm/nvm.sh
###ACTION_DELIMITER###
nvm install 15.14.0
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgtk-3-0 libnotify4 libnss3 libxss1 libxtst6 xdg-utils libatspi2.0-0 libuuid1 libappindicator3-1
###ACTION_DELIMITER###
apt-get update && apt-get install -y libasound2 libgbm1
###ACTION_DELIMITER###
apt-get update && apt-get install -y libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxshmfence1
###ACTION_DELIMITER###
npm install --verbose
###ACTION_DELIMITER###
npx electron-builder install-app-deps --verbose
###ACTION_DELIMITER###
cat /root/.npm/_logs/2025-09-18T23_53_09_393Z-debug.log
###ACTION_DELIMITER###
npx electron-builder install-app-deps --debug
###ACTION_DELIMITER###
DEBUG=electron-builder* npx electron-builder install-app-deps
###ACTION_DELIMITER###
ls -la /home/lisk-desktop/app
###ACTION_DELIMITER###
cat app/package.json
###ACTION_DELIMITER###
npm install -g electron-rebuild && cd app && electron-rebuild
###ACTION_DELIMITER###
npm install -g @electron/rebuild && cd app && npx electron-rebuild
###ACTION_DELIMITER###
npm install -g --force @electron/rebuild && cd app && npx electron-rebuild
###ACTION_DELIMITER###
npm test --verbose
###ACTION_DELIMITER###
cd ..
###ACTION_DELIMITER###
npm test -- --verbose
###ACTION_DELIMITER###
echo 'npm test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh""",
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

# Choose an appropriate base image based on the project's requirements - replace node:18-bullseye with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:18-bullseye

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
RUN git clone https://github.com/LiskHQ/lisk-desktop.git /home/lisk-desktop

WORKDIR /home/lisk-desktop
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("LiskHQ", "lisk_desktop_4185_to_4150")
class LISK_DESKTOP_4185_TO_4150(Instance):
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
        import json

        # Extract test names using regex patterns
        # Passed tests: lines with indented ✓ followed by test name
        passed_matches = re.findall(
            r"^\s*✓\s+(.*?)(?:\s*\(\d+ ms\))?$", log, re.MULTILINE
        )
        passed_tests.update(passed_matches)
        # Failed tests: lines with indented ✕ followed by test name
        failed_matches = re.findall(
            r"^\s*✕\s+(.*?)(?:\s*\(\d+ ms\))?$", log, re.MULTILINE
        )
        failed_tests.update(failed_matches)
        # Skipped tests: lines with indented ○ followed by test name
        skipped_matches = re.findall(
            r"^\s*○\s+(.*?)(?:\s*\(\d+ ms\))?$", log, re.MULTILINE
        )
        skipped_tests.update(skipped_matches)
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
