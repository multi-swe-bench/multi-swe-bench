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
                """ls -la
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
npm install --ignore-scripts
###ACTION_DELIMITER###
gulp --tasks
###ACTION_DELIMITER###
npx gulp --tasks
###ACTION_DELIMITER###
npm install graceful-fs@4.2.11 --save-dev
###ACTION_DELIMITER###
npm install npm-force-resolutions --save-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y jq
###ACTION_DELIMITER###
jq '.resolutions = { "graceful-fs": "4.2.11" } | .scripts.preinstall = "npx npm-force-resolutions"' package.json > temp.json && mv temp.json package.json
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
jq 'del(.scripts.prepublish)' package.json > temp.json && mv temp.json package.json
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
npx gulp travis
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && source ~/.bashrc && nvm install 12 && nvm use 12 && npm install
###ACTION_DELIMITER###
npm test
###ACTION_DELIMITER###
npm install -g yarn && yarn install
###ACTION_DELIMITER###
jq '.resolutions += {"graceful-fs": "4.2.11", "minimatch": "3.1.2"}' package.json > temp.json && mv temp.json package.json && yarn install
###ACTION_DELIMITER###
npm test
###ACTION_DELIMITER###
echo 'GULP_TASK=test-server npx gulp travis' > test_commands.sh && echo 'GULP_TASK=test-client-travis npx gulp travis' >> test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
GULP_TASK=test-server npx gulp travis
GULP_TASK=test-client-travis npx gulp travis

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
GULP_TASK=test-server npx gulp travis
GULP_TASK=test-client-travis npx gulp travis

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
GULP_TASK=test-server npx gulp travis
GULP_TASK=test-client-travis npx gulp travis

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
RUN git clone https://github.com/DevExpress/testcafe-hammerhead.git /home/testcafe-hammerhead

WORKDIR /home/testcafe-hammerhead
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("DevExpress", "testcafe_hammerhead_1627_to_843")
class TESTCAFE_HAMMERHEAD_1627_TO_843(Instance):
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
        # Pattern for passed tests: ✓ followed by test name
        passed_re = re.compile(r'^\s*✓\s+(.*)$')
        # Pattern for failed tests: number) followed by test name
        failed_re = re.compile(r'^\s*\d+\)\s+(.*)$')
        for line in log.split('\n'):
            line = line.strip()
            # Check for passed tests
            passed_match = passed_re.match(line)
            if passed_match:
                test_name = passed_match.group(1).strip()
                passed_tests.add(test_name)
            # Check for failed tests
            failed_match = failed_re.match(line)
            if failed_match:
                test_name = failed_match.group(1).strip()
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
