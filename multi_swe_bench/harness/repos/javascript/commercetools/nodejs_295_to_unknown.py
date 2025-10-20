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
                """npm install
###ACTION_DELIMITER###
npm install -g npm@6
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
npm test -- --verbose
###ACTION_DELIMITER###
lerna bootstrap
###ACTION_DELIMITER###
npx lerna bootstrap
###ACTION_DELIMITER###
rm -rf package-lock.json node_modules && npm install
###ACTION_DELIMITER###
npx lerna bootstrap
###ACTION_DELIMITER###
cat /root/.npm/_logs/2025-09-23T15_21_17_508Z-debug.log
###ACTION_DELIMITER###
npm install graceful-fs@4.2.10
###ACTION_DELIMITER###
npm dedupe
###ACTION_DELIMITER###
npx lerna bootstrap
###ACTION_DELIMITER###
npm install -g npm@8
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
echo '{"resolutions": {"graceful-fs": "4.2.10"}}' >> package.json && rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
jq '.resolutions = {"graceful-fs": "4.2.10"}' package.json > temp.json && mv temp.json package.json && rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
apt-get update && apt-get install -y jq
###ACTION_DELIMITER###
jq '.resolutions = {"graceful-fs": "4.2.10"}' package.json > temp.json && mv temp.json package.json && rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
git checkout package.json && jq '.resolutions = {"graceful-fs": "4.2.10"}' package.json > temp.json && mv temp.json package.json && rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
sed -i 's/"devDependencies": {/"overrides": {"graceful-fs": "4.2.10"},
  "devDependencies": {/' package.json && rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
jq '.overrides = {"graceful-fs": "4.2.10"}' package.json > temp.json && mv temp.json package.json && rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
jq '. + {"overrides": {"graceful-fs": "4.2.10"}}' package.json > temp.json && mv temp.json package.json && rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
cat /root/.npm/_logs/2025-09-23T15_26_19_127Z-debug.log
###ACTION_DELIMITER###
npm install -g npm@8 && rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
npm install -g npm@8 && npm --version && jq '.overrides = {"graceful-fs": "4.2.10"}' package.json > temp.json && mv temp.json package.json && rm -rf node_modules package-lock.json && npm install && npx lerna bootstrap
###ACTION_DELIMITER###
jq '.overrides = {"graceful-fs": "4.2.10"}' package.json > temp.json && mv temp.json package.json && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && npm test -- --verbose
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && nvm install 6 && nvm use 6 && npm install && npx lerna bootstrap && npm test -- --verbose
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && nvm install 6 && nvm use 6 && npm install -g npm@5.10.1 && npm install && npx lerna bootstrap && npm test -- --verbose
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && nvm use 6 && npm install && npx lerna bootstrap && npm test -- --verbose
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && nvm use 6 && jq '.overrides = {"graceful-fs": "4.2.10"}' package.json > temp.json && mv temp.json package.json && rm -rf node_modules package-lock.json && npm install && npx lerna bootstrap && npm test -- --verbose
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && nvm use 6 && npm install --ignore-scripts && npx lerna bootstrap && npm run build && npm test -- --verbose
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && nvm use 6 && npm install --ignore-scripts && npx lerna bootstrap && npm run build && npm test -- --verbose
###ACTION_DELIMITER###
echo 'npm test -- --verbose' > /home/nodejs/test_commands.sh && chmod +x /home/nodejs/test_commands.sh"""
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
RUN git clone https://github.com/commercetools/nodejs.git /home/nodejs

WORKDIR /home/nodejs
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("commercetools", "nodejs_295_to_unknown")
class NODEJS_295_TO_UNKNOWN(Instance):
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
        # Remove ANSI escape codes
        log_clean = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', log)
        lines = log_clean.split('\n')
        # Patterns for test statuses (Jest-style)
        passed_pattern = re.compile(r'^\s*✓\s*(.*?)\s*\(\d+ms\)$')
        failed_pattern = re.compile(r'^\s*✕\s*(.*?)\s*\(\d+ms\)$')
        skipped_pattern = re.compile(r'^\s*○\s*(.*?)\s*\(\d+ms\)$')
        for line in lines:
            # Check for passed tests
            pass_match = passed_pattern.match(line)
            if pass_match:
                test_name = pass_match.group(1).strip()
                passed_tests.add(test_name)
            # Check for failed tests
            fail_match = failed_pattern.match(line)
            if fail_match:
                test_name = fail_match.group(1).strip()
                failed_tests.add(test_name)
            # Check for skipped tests
            skip_match = skipped_pattern.match(line)
            if skip_match:
                test_name = skip_match.group(1).strip()
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
