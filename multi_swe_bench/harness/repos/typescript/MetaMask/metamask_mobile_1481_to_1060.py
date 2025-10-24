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
        return "ubuntu:latest"

    def image_prefix(self) -> str:
        return "envagent"

    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:
        repo_name = self.pr.repo
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
                """curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
###ACTION_DELIMITER###
nvm install
###ACTION_DELIMITER###
npm install -g yarn@1
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
sed -i 's/git@github.com:/https:\/\/github.com\//g' /home/metamask-mobile/.gitmodules
###ACTION_DELIMITER###
git submodule sync
###ACTION_DELIMITER###
sed -i 's/git+ssh:\/\/git@github.com\//https:\/\/github.com\//g' package.json && sed -i 's/git@github.com:/https:\/\/github.com\//g' package.json
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
# Run unit tests with verbose output
yarn test:unit --verbose
# Run E2E tests with verbose output
yarn test:e2e --verbose' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls node_modules/.bin/jest
###ACTION_DELIMITER###
yarn add --dev jest@24.5.0
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2.7 python3 make g++
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 make g++
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
PYTHON=python3 yarn install
###ACTION_DELIMITER###
npm install -g node-gyp@5.x && PYTHON=python3 yarn install
###ACTION_DELIMITER###
npm install -g node-gyp@latest && PYTHON=python3 yarn install
###ACTION_DELIMITER###
npm_config_node_gyp=$(which node-gyp) PYTHON=python3 yarn install
###ACTION_DELIMITER###
npm install -g node-gyp@5 && npm_config_node_gyp=$(which node-gyp) PYTHON=python3 yarn install
###ACTION_DELIMITER###
npm install -g node-gyp@3 && npm_config_node_gyp=$(which node-gyp) PYTHON=python3 yarn install
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository universe && apt-get update && apt-get install -y python2.7 && PYTHON=python2.7 yarn install
###ACTION_DELIMITER###
yarn install --ignore-optional
###ACTION_DELIMITER###
yarn add --dev jest
###ACTION_DELIMITER###
yarn add --dev jest@24.5.0
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2.7 && PYTHON=python2.7 yarn install
###ACTION_DELIMITER###
ln -s /usr/bin/python3 /usr/bin/python && apt-get update && apt-get install -y build-essential && PYTHON=python3 yarn install
###ACTION_DELIMITER###
npm install -g jest@24.5.0
###ACTION_DELIMITER###
jest ./app/ --verbose
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
jest ./app/ --verbose' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e
jest ./app/ --verbose

""".replace("[[REPO_NAME]]", repo_name),
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
jest ./app/ --verbose

""".replace("[[REPO_NAME]]", repo_name),
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
jest ./app/ --verbose

""".replace("[[REPO_NAME]]", repo_name),
            ),
        ]

    def dockerfile(self) -> str:
        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        dockerfile_content = """
# This is a template for creating a Dockerfile to test patches
# LLM should fill in the appropriate values based on the context

# Choose an appropriate base image based on the project's requirements - replace ubuntu:latest with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:latest

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


@Instance.register("MetaMask", "metamask_mobile_1481_to_1060")
class METAMASK_MOBILE_1481_TO_1060(Instance):
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

        return "bash /home/run.sh"

    def test_patch_run(self, test_patch_run_cmd: str = "") -> str:
        if test_patch_run_cmd:
            return test_patch_run_cmd

        return "bash /home/test-run.sh"

    def fix_patch_run(self, fix_patch_run_cmd: str = "") -> str:
        if fix_patch_run_cmd:
            return fix_patch_run_cmd

        return "bash /home/fix-run.sh"

    def parse_log(self, log: str) -> TestResult:
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re

        current_suite = None
        # Regex patterns to match test suite and cases
        suite_pattern = re.compile(
            r"^\s{2}(\w+)\s*$"
        )  # Matches suite names (e.g., '  Transactions')
        passed_test_pattern = re.compile(
            r"^\s{4}✓\s(.*?)\s*\(\d+ms\)$"
        )  # Matches passed tests (e.g., '    ✓ should render correctly (20ms)')
        failed_test_pattern = re.compile(
            r"^\s{4}✕\s(.*?)\s*\(\d+ms\)$"
        )  # Matches failed tests (e.g., '    ✕ should render correctly (7ms)')
        failed_indicator_pattern = re.compile(
            r"^\s{2}●\s(.*?) › (.*?)$"
        )  # Matches failed test indicators (e.g., '  ● AssetIcon › should render correctly')
        for line in log.split("\n"):
            # Update current suite name if line matches suite pattern
            suite_match = suite_pattern.match(line)
            if suite_match:
                current_suite = suite_match.group(1)
                continue
            # Capture passed tests
            passed_match = passed_test_pattern.match(line)
            if passed_match and current_suite:
                test_desc = passed_match.group(1)
                passed_tests.add(f"{current_suite} {test_desc}")
                continue
            # Capture failed tests from ✕ lines
            failed_match = failed_test_pattern.match(line)
            if failed_match and current_suite:
                test_desc = failed_match.group(1)
                failed_tests.add(f"{current_suite} {test_desc}")
                continue
            # Capture failed tests from ● indicators
            failed_indicator_match = failed_indicator_pattern.match(line)
            if failed_indicator_match:
                suite = failed_indicator_match.group(1)
                test_desc = failed_indicator_match.group(2)
                failed_tests.add(f"{suite} {test_desc}")
                continue
        parsed_results = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
        }

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
