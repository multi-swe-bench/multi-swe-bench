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
        return "ubuntu:22.04"
    
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
                """ls -la /home/comixed
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-11-jdk maven
###ACTION_DELIMITER###
mvn clean install
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-17-jdk && update-alternatives --set java /usr/lib/jvm/java-17-openjdk-amd64/bin/java && update-alternatives --set javac /usr/lib/jvm/java-17-openjdk-amd64/bin/javac
###ACTION_DELIMITER###
mvn clean install
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && apt-get install -y nodejs && npm install -g yarn
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && apt-get install -y nodejs && npm install -g yarn
###ACTION_DELIMITER###
apt-get remove -y libnode72 && apt-get update && apt-get install -y curl && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && apt-get install -y nodejs && npm install -g yarn
###ACTION_DELIMITER###
apt-get remove -y libnode72 && apt-get autoremove -y && apt-get install -y nodejs && npm install -g yarn
###ACTION_DELIMITER###
apt-get remove -y libnode72 nodejs && apt-get autoremove -y && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && apt-get install -y nodejs && npm install -g yarn
###ACTION_DELIMITER###
mvn clean install
###ACTION_DELIMITER###
ls -la comixed-webui
###ACTION_DELIMITER###
cat comixed-webui/package.json
###ACTION_DELIMITER###
cat comixed-webui/karma.conf.js
###ACTION_DELIMITER###
apt-get update && apt-get install -y chromium-browser
###ACTION_DELIMITER###
mvn clean install
###ACTION_DELIMITER###
cd comixed-webui && yarn test
###ACTION_DELIMITER###
export CHROME_BIN=/usr/bin/chromium-browser && yarn test
###ACTION_DELIMITER###
apt-get remove -y chromium-browser && curl -fsSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o chrome.deb && dpkg -i chrome.deb && apt-get install -f -y && export CHROME_BIN=/usr/bin/google-chrome && yarn test
###ACTION_DELIMITER###
apt-get update && apt-get install -y fonts-liberation libgbm1 libgtk-3-0 libvulkan1 libxkbcommon0 wget xdg-utils && dpkg -i chrome.deb && apt-get install -f -y && export CHROME_BIN=/usr/bin/google-chrome && yarn test
###ACTION_DELIMITER###
apt --fix-broken install -y
###ACTION_DELIMITER###
export CHROME_BIN=/usr/bin/google-chrome && yarn test
###ACTION_DELIMITER###
echo -e '#!/bin/bash
exec /usr/bin/google-chrome --no-sandbox "$@"' > /tmp/chrome-wrapper.sh && chmod +x /tmp/chrome-wrapper.sh && export CHROME_BIN=/tmp/chrome-wrapper.sh && yarn test
###ACTION_DELIMITER###
cd /home/comixed && mvn clean install
###ACTION_DELIMITER###
echo 'mvn clean test -Dstyle.color=never' > /home/comixed/test_commands.sh && chmod +x /home/comixed/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
mvn clean test -Dstyle.color=never

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
mvn clean test -Dstyle.color=never

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
mvn clean test -Dstyle.color=never

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
FROM ubuntu:22.04

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


@Instance.register("comixed", "comixed_2263_to_unknown")
class COMIXED_2263_TO_UNKNOWN(Instance):
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
        import json
        # Parse test run lines (e.g., [INFO] Tests run: ... -- in <test_name>)
        test_run_pattern = re.compile(r"\[INFO\] Tests run: \d+, Failures: (\d+), Errors: (\d+), Skipped: (\d+), .* -- in (.*)")
        error_test_run_pattern = re.compile(r"\[ERROR\] Tests run: \d+, Failures: (\d+), Errors: (\d+), Skipped: (\d+), .* <<< FAILURE! -- in (.*)")
        # Process test run lines
        for match in test_run_pattern.findall(log):
            failures, errors, skipped, test_name = match
            failures = int(failures)
            errors = int(errors)
            skipped = int(skipped)
            if failures > 0 or errors > 0:
                failed_tests.add(test_name)
            elif skipped > 0:
                skipped_tests.add(test_name)
            else:
                passed_tests.add(test_name)
        # Process error test run lines (explicit failures)
        for match in error_test_run_pattern.findall(log):
            _, _, _, test_name = match  # Failures/errors are non-zero
            failed_tests.add(test_name)
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
