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
        return "openjdk:17-jdk-slim"
    
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
mvn --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y maven
###ACTION_DELIMITER###
mvn clean install
###ACTION_DELIMITER###
node --version && yarn --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y nodejs yarn
###ACTION_DELIMITER###
apt-get remove -y cmdtest && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list && apt-get update && apt-get install -y yarn
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl gnupg && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list && apt-get update && apt-get install -y yarn
###ACTION_DELIMITER###
mvn clean install
###ACTION_DELIMITER###
node --version
###ACTION_DELIMITER###
cat comixed-webui/package.json
###ACTION_DELIMITER###
apt-get remove -y nodejs
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && apt-get install -y nodejs
###ACTION_DELIMITER###
node --version
###ACTION_DELIMITER###
cd comixed-webui && yarn install
###ACTION_DELIMITER###
yarn test
###ACTION_DELIMITER###
apt-get update && apt-get install -y chromium && export CHROME_BIN=/usr/bin/chromium
###ACTION_DELIMITER###
export CHROME_BIN=/usr/bin/chromium && yarn test
###ACTION_DELIMITER###
export CHROME_BIN=/usr/bin/chromium && yarn test -- --no-sandbox
###ACTION_DELIMITER###
export CHROME_BIN=/usr/bin/chromium && export CHROME_FLAGS="--no-sandbox" && yarn test
###ACTION_DELIMITER###
cat karma.conf.js
###ACTION_DELIMITER###
sed -i 's/browsers: \['ChromeHeadless'\],/browsers: ['ChromeHeadlessNoSandbox'],\n    customLaunchers: {\n      ChromeHeadlessNoSandbox: {\n        base: 'ChromeHeadless',\n        flags: ['--no-sandbox']\n      }\n    },/' karma.conf.js
###ACTION_DELIMITER###
export CHROME_BIN=/usr/bin/chromium && yarn test
###ACTION_DELIMITER###
sed -i "/browsers: \['ChromeHeadless'\],/c\    browsers: ['ChromeHeadlessNoSandbox'],\n    customLaunchers: {\n      ChromeHeadlessNoSandbox: {\n        base: 'ChromeHeadless',\n        flags: ['--no-sandbox']\n      }\n    }," karma.conf.js
###ACTION_DELIMITER###
cat karma.conf.js && export CHROME_BIN=/usr/bin/chromium && yarn test
###ACTION_DELIMITER###
cd /home/comixed && echo -e '#!/bin/bash
set -e
mvn test -Dstyle.color=never
cd comixed-webui
yarn test' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e
mvn test -Dstyle.color=never
cd comixed-webui
yarn test

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
mvn test -Dstyle.color=never
cd comixed-webui
yarn test

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
mvn test -Dstyle.color=never
cd comixed-webui
yarn test

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

# Choose an appropriate base image based on the project's requirements - replace openjdk:17-jdk-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM openjdk:17-jdk-slim

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
RUN git clone https://github.com/comixed/comixed.git /home/comixed

WORKDIR /home/comixed
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("comixed", "comixed_2257_to_unknown")
class COMIXED_2257_TO_UNKNOWN(Instance):
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
        # Extract individual test cases from surefire plugin output
        # Pattern 1: Capture test class name from 'Running' lines
        test_running_pattern = r'\[INFO\] Running (org\.comixedproject\.\S+)'
        test_classes = re.findall(test_running_pattern, log)
        # Pattern 2: Capture test results (pass/fail/skip) from summary lines
        test_result_pattern = r'\[INFO\] Tests run: \d+, Failures: (\d+), Errors: (\d+), Skipped: (\d+)'
        results = re.findall(test_result_pattern, log)
        # Pattern 3: Capture failed tests from error messages (Java file paths)
        error_pattern = r'\[ERROR\] .*/src/test/java/([\w/]+)\.java'
        failed_file_paths = re.findall(error_pattern, log)
        for path in failed_file_paths:
            class_name = path.replace('/', '.')
            failed_tests.add(class_name)
        # Map test classes to their results
        for i, test_class in enumerate(test_classes):
            # Handle cases where results may be missing (e.g., build failure)
            if i >= len(results):
                failed_tests.add(test_class)
                continue
            failures = int(results[i][0])
            errors = int(results[i][1])
            skipped = int(results[i][2])
            if skipped > 0:
                skipped_tests.add(test_class)
            elif failures > 0 or errors > 0:
                failed_tests.add(test_class)
            else:
                passed_tests.add(test_class)
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
