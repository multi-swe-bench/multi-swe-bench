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
                """apt-get update && apt-get install -y xvfb
###ACTION_DELIMITER###
apt-get update && apt-get install -y chromium chromium-driver
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py --browser headlesschrome --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install robotstatuschecker==3.0.0
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py headlesschrome --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py headlesschrome' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum sh -c "CHROME_OPTIONS=\"--user-data-dir=/tmp/chrome-$(date +%s) --headless=new\" python atest/run.py headlesschrome"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py headlesschrome --variable BROWSER_OPTIONS:"--user-data-dir=/tmp/chrome-$(date +%s%N) --headless=new"' > test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py chrome --variable BROWSER_OPTIONS:"--headless=new --user-data-dir=/tmp/chrome-$(date +%s%N)"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --user-data-dir=$(mktemp -d)"' > test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --disable-dev-shm-usage --user-data-dir=$(mktemp -d)"' > test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --user-data-dir=$(mktemp -d)"' > test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage"' > test_commands.sh
###ACTION_DELIMITER###
echo 'python atest/run.py chromium --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage"' > test_commands.sh
###ACTION_DELIMITER###
echo 'python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --user-data-dir=$(mktemp -d)"' > test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py chromium --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --user-data-dir=$(mktemp -d)"' > test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libnss3 libgconf-2-4 libxss1 libappindicator3-1 libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxtst6 ca-certificates fonts-liberation libappindicator1 lsb-release xdg-utils wget
###ACTION_DELIMITER###
echo 'python atest/run.py chromium --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage"' > test_commands.sh
###ACTION_DELIMITER###
echo 'python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --user-data-dir=$(mktemp -d)"' > test_commands.sh
###ACTION_DELIMITER###
echo 'python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --binary=/usr/bin/chromium"' > test_commands.sh
###ACTION_DELIMITER###
echo 'python atest/run.py chromium --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --binary=/usr/bin/chromium"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --binary=/usr/bin/chromium"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --binary=/usr/bin/chromium"' > test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --user-data-dir=$(mktemp -d) --binary=/usr/bin/chromium"' > test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=chrome --no-sandbox --disable-dev-shm-usage --user-data-dir=$(mktemp -d)"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --user-data-dir=/tmp/chrome-$(date +%s%N)"' > test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py chrome --variable BROWSER_OPTIONS="--headless --no-sandbox --disable-dev-shm-usage --user-data-dir=/tmp/chrome-$(date +%s%N)"' > test_commands.sh
###ACTION_DELIMITER###
echo 'python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --user-data-dir=$(mktemp -d) --binary=/usr/bin/chromium"' > test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --incognito"' > test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --incognito --user-data-dir=$(mktemp -d) --binary=/usr/bin/chromium"' > test_commands.sh
###ACTION_DELIMITER###
echo 'python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --user-data-dir=$(mktemp -d) --binary=/usr/bin/chromium"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --temp-profile --binary=/usr/bin/chromium"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run --auto-servernum python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --incognito --binary=/usr/bin/chromium"' > test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
ln -s /usr/bin/chromium-driver /usr/bin/chromedriver
###ACTION_DELIMITER###
echo 'python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --user-data-dir=$(mktemp -d) --binary=/usr/bin/chromium"' > test_commands.sh
###ACTION_DELIMITER###
echo 'python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --incognito --user-data-dir=$(mktemp -d) --binary=/usr/bin/chromium"' > test_commands.sh
###ACTION_DELIMITER###
echo 'python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --user-data-dir=\$(mktemp -d) --binary=/usr/bin/chromium"' > test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --user-data-dir=\$(mktemp -d) --binary=/usr/bin/chromium"

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
python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --user-data-dir=\$(mktemp -d) --binary=/usr/bin/chromium"

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
python atest/run.py chrome --variable BROWSER_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --user-data-dir=\$(mktemp -d) --binary=/usr/bin/chromium"

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
RUN git clone https://github.com/robotframework/SeleniumLibrary.git /home/SeleniumLibrary

WORKDIR /home/SeleniumLibrary
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("robotframework", "SeleniumLibrary_1909_to_1879")
class SELENIUMLIBRARY_1909_TO_1879(Instance):
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
        # Regex pattern to match test cases with status
        pattern = re.compile(r'^(?:\[\s*\d+\s*\]\s*)?([^|]+)\s*\|\s*(PASS|FAIL|SKIP|PASSED|FAILED|SKIPPED)\s*\|?.*$', re.MULTILINE | re.IGNORECASE)
        for match in pattern.finditer(log):
            test_name = match.group(1).strip()
            status = match.group(2).upper()
            if status in ('PASS', 'PASSED'):
                passed_tests.add(test_name)
            elif status in ('FAIL', 'FAILED'):
                failed_tests.add(test_name)
            elif status in ('SKIP', 'SKIPPED'):
                skipped_tests.add(test_name)
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
