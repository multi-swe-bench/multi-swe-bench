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
        return "node:18-bookworm"
    
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
                """npm install
###ACTION_DELIMITER###
wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 && tar xjf phantomjs-2.1.1-linux-x86_64.tar.bz2 && cp phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/ && chmod +x /usr/local/bin/phantomjs && export PHANTOMJS_BIN=/usr/local/bin/phantomjs
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
rm /usr/local/bin/phantomjs && wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.8-linux-x86_64.tar.bz2 && tar xjf phantomjs-1.9.8-linux-x86_64.tar.bz2 && cp phantomjs-1.9.8-linux-x86_64/bin/phantomjs /usr/local/bin/ && chmod +x /usr/local/bin/phantomjs && export PHANTOMJS_BIN=/usr/local/bin/phantomjs && npm install
###ACTION_DELIMITER###
grunt qunit
###ACTION_DELIMITER###
sed -i '/coverage: {/,/},/d' Gruntfile.js && grunt qunit
###ACTION_DELIMITER###
sed -i 's/"--web-security": "no",/phantomjs: { "web-security": "no" },/' Gruntfile.js && grunt qunit
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && source ~/.bashrc && nvm install 6 && nvm use 6 && npm install && grunt qunit
###ACTION_DELIMITER###
sed -i 's/npm install -g grunt-cli/npm install -g grunt-cli@1.3.2/' package.json && nvm use 6 && npm install && grunt qunit
###ACTION_DELIMITER###
sed -i 's/grunt-cli@1.3.2/grunt-cli@1.2.0/' package.json && nvm use 6 && npm install --unsafe-perm && grunt qunit
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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:18-bookworm

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


@Instance.register("IgniteUI", "ignite_ui_507_to_375")
class IGNITE_UI_507_TO_375(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re
        lines = log.split('\n')
        same_line_passed = re.compile(r'^(.*?)\x1b\[32mOK\x1b\[39m')
        same_line_failed = re.compile(r'^(.*?)\x1b\[31mERROR\x1b\[39m')
        same_line_skipped = re.compile(r'^(.*?)\x1b\[33mSKIPPED\x1b\[39m')  # Assuming SKIPPED uses yellow (33m)
        for i, line in enumerate(lines):
            # Check same-line status
            passed_match = same_line_passed.search(line)
            if passed_match:
                test_name = passed_match.group(1).rstrip('. ').strip()
                passed_tests.add(test_name)
                continue
            failed_match = same_line_failed.search(line)
            if failed_match:
                test_name = failed_match.group(1).rstrip('. ').strip()
                failed_tests.add(test_name)
                continue
            # Check same-line skipped
            skipped_match = same_line_skipped.search(line)
            if skipped_match:
                test_name = skipped_match.group(1).rstrip('. ').strip()
                skipped_tests.add(test_name)
                continue
            # Check if line ends with '...'
            if line.endswith('...'):
                test_name = line.rstrip('...').strip()
                # Check next line for status
                if i + 1 < len(lines):
                    next_line = lines[i+1]
                    # Check for error indicators in next line
                    if any(indicator in next_line for indicator in ['ERROR', 'timed out', 'TypeError', 'Expected', 'Message:']):
                        failed_tests.add(test_name)
                    # Check for skipped indicators in next line
                    elif any(indicator in next_line for indicator in ['SKIPPED', '\x1b\[33mSKIPPED\x1b\[39m']):
                        skipped_tests.add(test_name)
                    # Check for passed indicators in next line
                    elif 'OK' in next_line or '\x1b\[32mOK\x1b\[39m' in next_line:
                        passed_tests.add(test_name)
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
