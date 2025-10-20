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
                """apt-get install -y libgtk-3-0 libnotify4 libgconf-2-4 libnss3 libxss1 libasound2
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
sed -i 's/git+ssh:\/\/git@github.com\/brave\/node-sha3.git/git+https:\/\/github.com\/brave\/node-sha3.git/g' package.json
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
export CHROMEDRIVER_SKIP_DOWNLOAD=true && npm install --legacy-peer-deps --force
###ACTION_DELIMITER###
wget https://chromedriver.storage.googleapis.com/2.35/chromedriver_linux64.zip -O chromedriver-v2.35-linux-x64.zip && unzip chromedriver-v2.35-linux-x64.zip && mv chromedriver /usr/local/bin/
###ACTION_DELIMITER###
export CHROMEDRIVER_SKIP_DOWNLOAD=true && export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver && npm install --legacy-peer-deps --force
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && export CHROMEDRIVER_SKIP_DOWNLOAD=true && export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver && npm install --legacy-peer-deps --force
###ACTION_DELIMITER###
export CHROMEDRIVER_SKIP_DOWNLOAD=true && export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver && npm install --ignore-scripts --legacy-peer-deps --force
###ACTION_DELIMITER###
cat /root/.npm/_logs/2025-09-20T19_57_55_614Z-debug-0.log | grep 'webtorrent'
###ACTION_DELIMITER###
sed -i '/"engines": {/i "overrides": { "http-node": "github:feross/http-node#master" },' package.json
###ACTION_DELIMITER###
export CHROMEDRIVER_SKIP_DOWNLOAD=true && export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver && npm install --legacy-peer-deps --force
###ACTION_DELIMITER###
export CHROMEDRIVER_SKIP_DOWNLOAD=true && export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver && npm install --ignore-scripts --legacy-peer-deps --force
###ACTION_DELIMITER###
export CHROMEDRIVER_SKIP_DOWNLOAD=true && export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver && npm run postinstall
###ACTION_DELIMITER###
export NODE_OPTIONS=--openssl-legacy-provider && export CHROMEDRIVER_SKIP_DOWNLOAD=true && export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver && npm run postinstall
###ACTION_DELIMITER###
echo 'npm test -- --verbose' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npm test -- --verbose

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
npm test -- --verbose

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
npm test -- --verbose

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
RUN git clone https://github.com/brave/browser-laptop.git /home/browser-laptop

WORKDIR /home/browser-laptop
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("brave", "browser_laptop_13607_to_11977")
class BROWSER_LAPTOP_13607_TO_11977(Instance):
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
        passed_tests = set[str]()
        failed_tests = set[str]()
        skipped_tests = set[str]()
        import re
        # Patterns to capture test name, skipping recoveryWallet errors and metadata
        passed_pattern = re.compile(r'^\s+✓\s+(?:Error in "recoveryWallet": ".*?" )?(.*?)(?:\s+should loosely deep-equal.*|\s*\} \+.*)?$', re.MULTILINE)
        failed_pattern = re.compile(r'^\s+\d+\)\s+(?:Error in "recoveryWallet": ".*?" )?(.*?)(?:\s+should loosely deep-equal.*|\s*\} \+.*)?$', re.MULTILINE)
        # Remove leading warnings
        warning_pattern = re.compile(r'^\(Use `node.*?\) ', re.DOTALL)
        context = []  # Track nested describe blocks
        for line in log.split('\n'):
            line = line.rstrip('\r')
            indent = len(line) - len(line.lstrip())
            # Update context, excluding errors and command lines
            if not (passed_pattern.match(line) or failed_pattern.match(line)):
                describe_name = line.strip()
                if describe_name and not (
                    describe_name.startswith('>') or  # Skip command lines
                    'Error in "recoveryWallet"' in describe_name or  # Skip recoveryWallet errors
                    describe_name.startswith('(node:') or
                    describe_name.startswith('(Use `node') or
                    'Warning' in describe_name or
                    'Error:' in describe_name or
                    'at ' in describe_name or
                    '{}'.format('{}') in describe_name
                ):
                    # Remove deeper contexts
                    while context and context[-1]['indent'] >= indent:
                        context.pop()
                    context.append({'indent': indent, 'name': describe_name})
            # Capture passed tests with full context
            passed_match = passed_pattern.match(line)
            if passed_match:
                test_name = passed_match.group(1).strip()
                test_name = warning_pattern.sub('', test_name)  # Remove warning prefixes
                full_name = ' '.join([c['name'] for c in context] + [test_name])
                passed_tests.add(full_name)
            # Capture failed tests with full context
            failed_match = failed_pattern.match(line)
            if failed_match:
                test_name = failed_match.group(1).strip()
                test_name = warning_pattern.sub('', test_name)  # Remove warning prefixes
                full_name = ' '.join([c['name'] for c in context] + [test_name])
                failed_tests.add(full_name)
        # Skipped tests: no pattern identified in logs, leaving as empty set
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
