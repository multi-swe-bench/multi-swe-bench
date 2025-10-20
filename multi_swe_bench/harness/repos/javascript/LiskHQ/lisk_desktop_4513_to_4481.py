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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y build-essential python3 libusb-1.0-0-dev libudev-dev
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
ls -la
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
###ACTION_DELIMITER###
nvm install
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
grep '@liskhq/lisk-client' package.json
###ACTION_DELIMITER###
npm view @liskhq/lisk-client versions
###ACTION_DELIMITER###
sed -i 's/"@liskhq\/lisk-client": "6.0.0-alpha.4"/"@liskhq\/lisk-client": "6.0.0-beta.0"/' package.json
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
echo '@liskhq:registry=https://registry.npmjs.org/' >> .npmrc
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
echo 'registry=https://registry.npmjs.org/' >> .npmrc
###ACTION_DELIMITER###
rm -rf package-lock.json node_modules && npm install
###ACTION_DELIMITER###
sed -i 's/git+ssh:\/\/git@github.com\/BitGo\/blake2b.git/git+https:\/\/github.com\/BitGo\/blake2b.git/' package.json
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
grep 'blake2b' package.json
###ACTION_DELIMITER###
git config --global url."https://github.com/".insteadOf ssh://git@github.com/
###ACTION_DELIMITER###
npm cache clean --force && rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
npm install git+https://github.com/BitGo/blake2b.git
###ACTION_DELIMITER###
npm install blake2b@2.1.4
###ACTION_DELIMITER###
sed -i 's/"blake2b": "2.1.4"/"blake2b": "git+https:\/\/github.com\/BitGo\/blake2b.git#v2.1.4"/' package.json
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
sed -i 's/"blake2b": "git+https:\/\/github.com\/BitGo\/blake2b.git#v2.1.4"/"blake2b": "2.1.4"/' package.json && npm install
###ACTION_DELIMITER###
git config --global --list && npm cache clean --force && rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
npm install blake2b@2.1.4
###ACTION_DELIMITER###
grep 'blake2b' package.json && sed -i 's/git+https:\/\/github.com\/BitGo\/blake2b.git#v2.1.4/2.1.4/' package.json && npm install
###ACTION_DELIMITER###
npm cache clean --force && rm -rf node_modules package-lock.json && npm install blake2b@2.1.4 && npm install
###ACTION_DELIMITER###
git config --global url."https://github.com/".insteadOf ssh://git@github.com/ && npm install blake2b@2.1.4 --force
###ACTION_DELIMITER###
echo '{"overrides": {"blake2b": "2.1.4"}}' >> package.json && npm install
###ACTION_DELIMITER###
sed -i '$ d' package.json && jq '.overrides = {"blake2b": "2.1.4"}' package.json > temp.json && mv temp.json package.json && npm cache clean --force && rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
apt-get update && apt-get install -y jq && sed -i '$ d' package.json && echo '  ,"overrides": {"blake2b": "2.1.4"}
}' >> package.json && npm cache clean --force && rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
echo 'npm test -- --verbose' > test_commands.sh"""
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
RUN git clone https://github.com/LiskHQ/lisk-desktop.git /home/lisk-desktop

WORKDIR /home/lisk-desktop
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("LiskHQ", "lisk_desktop_4513_to_4481")
class LISK_DESKTOP_4513_TO_4481(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        # Pattern for passed tests: ✓ followed by test name (optional time)
        passed_pattern = re.compile(r'^\s*✓\s+(.*?)\s*(?:\(\d+ ms\))?$', re.MULTILINE)
        passed_tests.update([t.strip() for t in passed_pattern.findall(log)])
        # Pattern for failed tests: ✕ followed by test name (optional time)
        failed_pattern = re.compile(r'^\s*✕\s+(.*?)\s*(?:\(\d+ ms\))?$', re.MULTILINE)
        failed_tests.update([t.strip() for t in failed_pattern.findall(log)])
        # Capture test suite failures (e.g., "FAIL path/to/test.js")
        suite_failure_pattern = re.compile(r'^FAIL\s+(.*?)\s*$', re.MULTILINE)
        for suite in suite_failure_pattern.findall(log):
            # Skip summary lines (e.g., "Test Suites: 71 failed...")
            if not re.match(r'^(Test Suites|Tests):', suite):
                failed_tests.add(suite.strip())
        # Pattern for skipped tests: ○ followed by test name (optional time)
        skipped_pattern = re.compile(r'^\s*○\s+(.*?)\s*(?:\(\d+ ms\))?$', re.MULTILINE)
        skipped_tests.update([t.strip() for t in skipped_pattern.findall(log) if t.strip()])
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
