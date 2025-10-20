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
                """ls -la
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && npm cache clean --force
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && yarn install
###ACTION_DELIMITER###
npm install -g npm@6 && npm install --legacy-peer-deps
###ACTION_DELIMITER###
check-node-version --package && lerna bootstrap && npm run build
###ACTION_DELIMITER###
npx check-node-version --package && lerna bootstrap && npm run build
###ACTION_DELIMITER###
npx check-node-version --package && npx lerna bootstrap && npm run build
###ACTION_DELIMITER###
npm cache clean --force && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && npx lerna bootstrap
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && npx lerna bootstrap --npm-client npm@6
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && npx lerna bootstrap --npm-client npm
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && npm cache clean --force && npm install --legacy-peer-deps && npx lerna bootstrap --force
###ACTION_DELIMITER###
cat .nvmrc && nvm install && nvm use && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && npx lerna bootstrap
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json yarn.lock && yarn install && npx lerna bootstrap
###ACTION_DELIMITER###
npm install -g npm@3 && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && npx lerna bootstrap
###ACTION_DELIMITER###
curl -O https://nodejs.org/dist/v6.17.1/node-v6.17.1-linux-x64.tar.xz && tar -xJf node-v6.17.1-linux-x64.tar.xz && export PATH=$PWD/node-v6.17.1-linux-x64/bin:$PATH && node -v && npm -v && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && npx lerna bootstrap
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && npm install --ignore-scripts --legacy-peer-deps && npx lerna bootstrap && npm run build
###ACTION_DELIMITER###
./node_modules/.bin/lerna bootstrap && npm run build
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
npm run test -- --verbose
npm run it:run -- --verbose' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e
npm run test -- --verbose
npm run it:run -- --verbose

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
npm run test -- --verbose
npm run it:run -- --verbose

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
npm run test -- --verbose
npm run it:run -- --verbose

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


@Instance.register("commercetools", "nodejs_330_to_unknown")
class NODEJS_330_TO_UNKNOWN(Instance):
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
        passed_tests = set() # Tests that passed successfully
        failed_tests = set() # Tests that failed
        skipped_tests = set() # Tests that were skipped
        import re
        # Strip ANSI escape codes
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        cleaned_log = ansi_escape.sub('', log)
        # Pattern for passed tests: ✓ at start of line, capture name, trim whitespace
        passed_pattern = re.compile(r'^\s*✓\s*(.*?)\s*(?:\(\d+ms\))?\s*$', re.MULTILINE)
        passed_tests = set(test.strip() for test in passed_pattern.findall(cleaned_log))
        # Pattern for failed tests: ✕ at start of line, capture name, trim whitespace
        failed_pattern = re.compile(r'^\s*✕\s*(.*?)\s*(?:\(\d+ms\))?\s*$', re.MULTILINE)
        failed_tests = set(test.strip() for test in failed_pattern.findall(cleaned_log))
        # Pattern for skipped tests: ○ at start of line, capture name, trim whitespace
        skipped_pattern = re.compile(r'^\s*○\s*(.*?)\s*$', re.MULTILINE)
        skipped_tests = set(test.strip() for test in skipped_pattern.findall(cleaned_log))
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
