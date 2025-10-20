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
                """yarn lint --help
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
yarn add --dev cross-env
###ACTION_DELIMITER###
yarn add --dev cross-env@7.0.3
###ACTION_DELIMITER###
yarn lint
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
yarn test
###ACTION_DELIMITER###
NODE_OPTIONS=--openssl-legacy-provider yarn test
###ACTION_DELIMITER###
apt-get update && apt-get install -y libnss3 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libgbm1 libpango-1.0-0 libcairo2 libatspi2.0-0
###ACTION_DELIMITER###
echo fs.inotify.max_user_watches=524288 | tee -a /etc/sysctl.conf && sysctl -p
###ACTION_DELIMITER###
sysctl -w fs.inotify.max_user_watches=524288
###ACTION_DELIMITER###
NODE_OPTIONS=--openssl-legacy-provider yarn test -- --no-auto-watch
###ACTION_DELIMITER###
apt-get update && apt-get install -y libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrender1 libwayland-client0
###ACTION_DELIMITER###
apt-get update && apt-get install -y libx11-6 libxrandr2 libxshmfence1 && ldconfig
###ACTION_DELIMITER###
NODE_OPTIONS=--openssl-legacy-provider yarn test -- --single-run
###ACTION_DELIMITER###
echo 'NODE_OPTIONS=--openssl-legacy-provider yarn test -- --single-run' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
NODE_OPTIONS=--openssl-legacy-provider yarn test -- --single-run

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
NODE_OPTIONS=--openssl-legacy-provider yarn test -- --single-run

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
NODE_OPTIONS=--openssl-legacy-provider yarn test -- --single-run

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
RUN git clone https://github.com/Semantic-Org/Semantic-UI-React.git /home/Semantic-UI-React

WORKDIR /home/Semantic-UI-React
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Semantic-Org", "Semantic_UI_React_4449_to_4145")
class SEMANTIC_UI_REACT_4449_TO_4145(Instance):
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
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        stack = []
        for line in lines:
            # Remove line number prefix
            content = re.sub(r'^\[\s*\d+\]\s*', '', line)
            # Strip ANSI escape codes
            content = ansi_escape.sub('', content)
            # Skip empty lines
            if not content.strip():
                continue
            # Calculate leading spaces and indentation level (2 spaces per level)
            leading_spaces = len(content) - len(content.lstrip(' '))
            level = leading_spaces // 2
            # Check for test case indicators
            # Match test lines with symbol as first non-whitespace character
            # Capture symbol and test text, ignoring leading log metadata
            # Match status symbol followed by test text, ignoring all leading content
            # Match symbol and test text, ignoring all leading content
            # Require status symbol to be the first non-whitespace character
            # Capture status symbol even if preceded by metadata
            # Require status symbol to be the first non-whitespace character
            # Allow leading content before the status symbol
            test_match = re.search(r'^\s*([✔√✖x])\s+(.*)$', content)
            if test_match:
                status_symbol, test_text = test_match.groups()
                test_text = test_text.strip()
                # Remove metadata prefixes from test text
                # Skip lines with irrelevant metadata
                if re.search(r'(Error from chokidar|Browserslist|WARN|ERROR|404|Chrome Headless|AssertionError|INFO|ℹ|｢wdm｣|Entrypoint|Built at)', content):
                    continue
                if test_text:
                    full_test_name = ' '.join(stack) + ' ' + test_text if stack else test_text
                    full_test_name = full_test_name.strip()
                    if status_symbol in ['✔', '√']:
                        passed_tests.add(full_test_name)
                    elif status_symbol in ['✖', 'x']:
                        failed_tests.add(full_test_name)
            else:
                # Update group stack only for valid test hierarchy lines
                group_text = content.strip()
                # Skip lines starting with timestamps (e.g., [17:21:10])
                if re.match(r'^\[\d+:\d+:\d+\]', group_text) or re.match(r'^\(node:', group_text) or re.match(r'^\(Use `node --trace-deprecation', group_text) or re.match(r'^Warning: Setting `displayName`', group_text) or re.match(r'^\$ yarn', group_text) or re.match(r'^warning From Yarn 1.0 onwards', group_text) or re.match(r'^yarn run', group_text):
                    continue
                if not group_text:
                    continue
                # Skip non-hierarchy lines (errors, summaries, etc.)
                # Explicitly skip non-hierarchy lines
                skip_substrings = ['Error from chokidar', 'SUMMARY', 'Finished in', 'Done in', 'error Command failed', 'WARN', 'ERROR', '404', 'Chrome Headless', 'INFO', 'ℹ', '｢wdm｣', 'Entrypoint', 'Built at', 'START:', 'Browserslist: caniuse-lite is outdated', 'npx browserslist@latest --update-db', 'Finished \'build:docs:docgen\'', '(Use `node --trace-deprecation', '[DEP0111]', 'DeprecationWarning', 'Warning: Setting `displayName`', 'warning From Yarn 1.0 onwards', 'yarn run', '$ satisfied', '$ yarn', '$ cross-env']
                if any(substr in group_text for substr in skip_substrings):
                    continue
                # Adjust stack to current level (2 spaces per level)
                while len(stack) > level:
                    stack.pop()
                # Add valid group to stack
                if len(stack) <= level:
                    stack = stack[:level] + [group_text]
                else:
                    stack[-1] = group_text
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
