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
        return "node:20-bullseye"
    
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
                """yarn setup
###ACTION_DELIMITER###
apt-get update && apt-get install -y ca-certificates curl gnupg && mkdir -p /etc/apt/keyrings && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_16.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && apt-get update && apt-get install -y nodejs
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
yarn setup
###ACTION_DELIMITER###
node -v
###ACTION_DELIMITER###
which node
###ACTION_DELIMITER###
/usr/bin/node -v
###ACTION_DELIMITER###
rm /usr/local/bin/node && ln -s /usr/bin/node /usr/local/bin/node
###ACTION_DELIMITER###
node -v
###ACTION_DELIMITER###
yarn setup
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
# Run dependency check
 yarn test:depcheck
# Run TGZ check
 yarn test:tgz-check
# Run attribution check
 yarn test:attribution-check
# Run iOS E2E tests with verbose and JSON output
 yarn wdio ./wdio/config/ios.config.debug.js --verbose --reporter json
# Run Android E2E tests with verbose and JSON output
 yarn wdio ./wdio/config/android.config.debug.js --verbose --reporter json' > /home/metamask-mobile/test_commands.sh && chmod +x /home/metamask-mobile/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e
# Run dependency check
 yarn test:depcheck
# Run TGZ check
 yarn test:tgz-check
# Run attribution check
 yarn test:attribution-check
# Run iOS E2E tests with verbose and JSON output
 yarn wdio ./wdio/config/ios.config.debug.js --verbose --reporter json
# Run Android E2E tests with verbose and JSON output
 yarn wdio ./wdio/config/android.config.debug.js --verbose --reporter json

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
#!/bin/bash
set -e
# Run dependency check
 yarn test:depcheck
# Run TGZ check
 yarn test:tgz-check
# Run attribution check
 yarn test:attribution-check
# Run iOS E2E tests with verbose and JSON output
 yarn wdio ./wdio/config/ios.config.debug.js --verbose --reporter json
# Run Android E2E tests with verbose and JSON output
 yarn wdio ./wdio/config/android.config.debug.js --verbose --reporter json

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
#!/bin/bash
set -e
# Run dependency check
 yarn test:depcheck
# Run TGZ check
 yarn test:tgz-check
# Run attribution check
 yarn test:attribution-check
# Run iOS E2E tests with verbose and JSON output
 yarn wdio ./wdio/config/ios.config.debug.js --verbose --reporter json
# Run Android E2E tests with verbose and JSON output
 yarn wdio ./wdio/config/android.config.debug.js --verbose --reporter json

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
FROM node:20-bullseye

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
RUN git clone https://github.com/MetaMask/metamask-mobile.git /home/metamask-mobile

WORKDIR /home/metamask-mobile
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("MetaMask", "metamask_mobile_7035_to_unknown")
class METAMASK_MOBILE_7035_TO_UNKNOWN(Instance):
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
        passed_tests = set[str]() # Tests that passed successfully
        failed_tests = set[str]() # Tests that failed
        skipped_tests = set[str]() # Tests that were skipped
        import re
        # Regex patterns for test files, suites, and test cases
        test_file_pattern = re.compile(r'^(PASS|FAIL) (.*\.test\.(ts|js|tsx|jsx))')
        test_case_pattern = re.compile(r'^(\s+)(✓|✕)\s+(.*?)(\s+\(\d+ ms\))?$')
        suite_pattern = re.compile(r'^(\s+)(.*?)\s*$')
        current_suites = []
        for line in log.split('\n'):
            # Check if the line is a test file (top-level suite)
            file_match = test_file_pattern.match(line)
            if file_match:
                test_file = file_match.group(2)
                current_suites = [test_file]
                continue
            # Check if the line is a test case
            test_match = test_case_pattern.match(line)
            if test_match:
                indentation = test_match.group(1)
                status = test_match.group(2)
                test_desc = test_match.group(3)
                # Indentation level: 2 spaces per level
                indent_level = len(indentation) // 2
                # Parent suites are all suites up to indent_level
                parent_suites = current_suites[:indent_level]
                full_test_name = ' > '.join(parent_suites) + ' > ' + test_desc if parent_suites else test_desc
                full_test_name = full_test_name.strip()
                if status == '✓':
                    passed_tests.add(full_test_name)
                elif status == '✕':
                    failed_tests.add(full_test_name)
                continue
            # Check if the line is a nested suite
            suite_match = suite_pattern.match(line)
            if suite_match:
                indentation = suite_match.group(1)
                suite_name = suite_match.group(2)
                if not suite_name or '#' in suite_name:  # Skip empty lines/comments
                    continue
                indent_level = len(indentation) // 2
                # Update current_suites to include the new suite at correct level
                current_suites = current_suites[:indent_level] + [suite_name]
                continue
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
