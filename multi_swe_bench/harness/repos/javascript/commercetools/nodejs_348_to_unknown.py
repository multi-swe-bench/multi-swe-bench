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

###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
npm install -g npm@6
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
npm test -- --verbose
###ACTION_DELIMITER###
lerna bootstrap
###ACTION_DELIMITER###

###ACTION_DELIMITER###
npx lerna bootstrap
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
npm run bootstrap
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && yarn install
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && source ~/.bashrc && nvm install 12 && nvm use 12 && rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
npm install lerna@2.5.1 && npm run bootstrap
###ACTION_DELIMITER###
source ~/.nvm/nvm.sh && nvm use 12 && rm -rf node_modules package-lock.json && yarn install && lerna bootstrap --use-yarn
###ACTION_DELIMITER###
npm cache clean -f && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && npx lerna bootstrap --legacy-peer-deps
###ACTION_DELIMITER###
source ~/.nvm/nvm.sh && nvm use 12 && rm -rf node_modules package-lock.json && yarn install --ignore-engines && npx lerna bootstrap --use-yarn --ignore-engines
###ACTION_DELIMITER###
source ~/.nvm/nvm.sh && nvm use 12 && rm -rf node_modules package-lock.json yarn.lock && yarn install && npx lerna bootstrap --use-yarn
###ACTION_DELIMITER###
source ~/.nvm/nvm.sh && nvm use 12 && rm -rf node_modules package-lock.json && npm install --ignore-scripts && npx lerna bootstrap --use-yarn
###ACTION_DELIMITER###
source ~/.nvm/nvm.sh && nvm use 12 && rm -rf node_modules package-lock.json yarn.lock && npm install --ignore-scripts && npx lerna bootstrap --force-local && npm run build
###ACTION_DELIMITER###
source ~/.nvm/nvm.sh && nvm use 12 && rm -rf node_modules package-lock.json yarn.lock && npm install --ignore-scripts && yarn install && npx lerna bootstrap --use-yarn && npm run build
###ACTION_DELIMITER###
source ~/.nvm/nvm.sh && nvm use 12 && rm -rf node_modules package-lock.json yarn.lock && yarn install --ignore-engines && npx lerna bootstrap --use-yarn --ignore-engines && npm run build
###ACTION_DELIMITER###
ls -la
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && yarn install
###ACTION_DELIMITER###
source ~/.nvm/nvm.sh && nvm use 12 && rm -rf node_modules && yarn install && npx lerna bootstrap --use-yarn && npm run build
###ACTION_DELIMITER###
sed -i 's/"npmClient": "npm"/"npmClient": "yarn"/' lerna.json && cat lerna.json
###ACTION_DELIMITER###
echo '{"lerna": "2.4.0", "version": "independent", "npmClient": "yarn", "useWorkspaces": true}' > lerna.json && cat lerna.json
###ACTION_DELIMITER###

###ACTION_DELIMITER###
npx lerna bootstrap
###ACTION_DELIMITER###
sed -i '/"private": true/a "workspaces": ["packages/*"],' package.json && cat package.json | grep workspaces
###ACTION_DELIMITER###
npx lerna bootstrap
###ACTION_DELIMITER###
rm -rf node_modules && yarn install --verbose
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json yarn.lock && yarn install --verbose
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json yarn.lock && yarn install --ignore-engines
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json yarn.lock && yarn install --ignore-scripts && npx lerna bootstrap --use-yarn && yarn run build
###ACTION_DELIMITER###
yarn cache clean && npm cache clean -f && rm -rf node_modules package-lock.json yarn.lock && yarn install && npx lerna bootstrap --use-yarn
###ACTION_DELIMITER###
yarn cache clean && npm cache clean -f && rm -rf node_modules package-lock.json yarn.lock && yarn install --ignore-scripts && npx lerna bootstrap --use-yarn && yarn run build
###ACTION_DELIMITER###
source ~/.nvm/nvm.sh && nvm use 12 && yarn cache clean && npm cache clean -f && rm -rf node_modules package-lock.json yarn.lock && yarn install --ignore-scripts && npx lerna bootstrap --use-yarn && yarn run build
###ACTION_DELIMITER###
source ~/.nvm/nvm.sh && nvm use 12 && yarn cache clean && npm cache clean -f && rm -rf node_modules package-lock.json yarn.lock && yarn install --ignore-scripts && npx lerna bootstrap --use-yarn && yarn run build
###ACTION_DELIMITER###
source ~/.nvm/nvm.sh && nvm use 12 && npm install --ignore-scripts && npx lerna bootstrap --use-yarn && npm run build
###ACTION_DELIMITER###
source ~/.nvm/nvm.sh && nvm use 12 && rm -rf node_modules package-lock.json yarn.lock && yarn install --ignore-scripts && yarn run build
###ACTION_DELIMITER###
source ~/.nvm/nvm.sh && nvm use 12 && yarn cache clean && npm cache clean -f && rm -rf node_modules package-lock.json yarn.lock && yarn install --ignore-scripts && npx lerna bootstrap --use-yarn && yarn run build
###ACTION_DELIMITER###
echo 'npm test -- --verbose' > test_commands.sh && chmod +x test_commands.sh && cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
npx lerna link && bash test_commands.sh
###ACTION_DELIMITER###
"""
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


@Instance.register("commercetools", "nodejs_348_to_unknown")
class NODEJS_348_TO_UNKNOWN(Instance):
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
        # Remove ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_log = ansi_escape.sub('', log)
        # Track latest status for each test
        test_status = {}
        for line in clean_log.split('\n'):
            line = line.strip()
            # Match passed tests
            pass_match = re.match(r'^[ \t]*(?:✓|✔|√|✅)\s+([^\n]+?)\s*\(\d+ms\)$', line)
            if pass_match:
                test_name = pass_match.group(1).strip()
                if not (test_name.lower().startswith(('at ', 'error:', 'npm')) or test_name.lower().endswith(('total', 'suites'))) and len(test_name) > 0:
                    test_status[test_name] = 'passed'
            # Match failed tests
            fail_match = re.match(r'^[ \t]*(?:✕|✖|×)\s+([^\n]+?)\s*\(\d+ms\)$', line)
            if fail_match:
                test_name = fail_match.group(1).strip()
                if not (test_name.lower().startswith(('at ', 'error:', 'npm')) or test_name.lower().endswith(('total', 'suites'))) and len(test_name) > 0:
                    test_status[test_name] = 'failed'
            # Match skipped tests
            skip_match = re.match(r'^[ \t]*○\s+([^\n]+?)\s*\(\d+ms\)$', line)
            if skip_match:
                test_name = skip_match.group(1).strip()
                if not (test_name.lower().startswith(('at ', 'error:', 'npm')) or test_name.lower().endswith(('total', 'suites'))) and len(test_name) > 0:
                    test_status[test_name] = 'skipped'
        # Populate sets based on latest status
        passed_tests = set(name for name, status in test_status.items() if status == 'passed')
        failed_tests = set(name for name, status in test_status.items() if status == 'failed')
        skipped_tests = set(name for name, status in test_status.items() if status == 'skipped')
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
