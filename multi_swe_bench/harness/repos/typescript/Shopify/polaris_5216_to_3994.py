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
        return "node:18-bookworm"
    
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
                """yarn install
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential python3
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
apt-get update && apt-get install -y jq
###ACTION_DELIMITER###
npm install -g node-gyp
###ACTION_DELIMITER###
export PYTHON=python3 && npm rebuild node-sass
###ACTION_DELIMITER###
sed -i 's/"rU"/"r"/g' /home/polaris/node_modules/node-gyp/gyp/pylib/gyp/input.py
###ACTION_DELIMITER###
export PYTHON=python3 && npm rebuild node-sass
###ACTION_DELIMITER###
apt-get update && apt-get install -y libsass-dev
###ACTION_DELIMITER###
jq '.resolutions += {"node-sass": "7.0.0"}' package.json > temp.json && mv temp.json package.json
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
sed -i 's/"rU"/"r"/g' /home/polaris/node_modules/node-gyp/gyp/pylib/gyp/input.py
###ACTION_DELIMITER###
grep -n '"rU"' /home/polaris/node_modules/node-gyp/gyp/pylib/gyp/input.py
###ACTION_DELIMITER###
export PYTHON=python3 && npm rebuild node-sass
###ACTION_DELIMITER###
jq '.resolutions["node-sass"] = "8.0.0"' package.json > temp.json && mv temp.json package.json
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
jq 'del(.resolutions["node-sass"]) | (.dependencies["node-sass"] = "sass") | (.devDependencies["node-sass"] = "sass")' package.json > temp.json && mv temp.json package.json
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
jq 'del(.dependencies["node-sass"]) | del(.devDependencies["node-sass"]) | del(.resolutions["node-sass"]) | .dependencies["sass"] = "^1.77.6" | .devDependencies["sass"] = "^1.77.6"' package.json > temp.json && mv temp.json package.json
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
npm run test
###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i 's/const nodeSass = require(\'node-sass\');/const sass = require(\'sass\');/' /home/polaris/config/rollup/plugin-styles.js
###ACTION_DELIMITER###
sed -i "s/const nodeSass = require('node-sass');/const sass = require('sass');/" /home/polaris/config/rollup/plugin-styles.js
###ACTION_DELIMITER###
sed -i 's/nodeSass\.renderSync/sass.renderSync/g' /home/polaris/config/rollup/plugin-styles.js
###ACTION_DELIMITER###
npm run test
###ACTION_DELIMITER###
jest --maxWorkers=4 --testTimeout=30000 --verbose
###ACTION_DELIMITER###
npx jest --maxWorkers=4 --testTimeout=30000 --verbose
###ACTION_DELIMITER###
echo 'module.exports = { testEnvironment: "jsdom", moduleNameMapper: { "^tests/(.*)$": "<rootDir>/tests/$1" }, maxWorkers: 4, testTimeout: 30000 };'> jest.config.js
###ACTION_DELIMITER###
npx jest --config jest.config.js --verbose
###ACTION_DELIMITER###

###ACTION_DELIMITER###
npm install --save-dev identity-obj-proxy
###ACTION_DELIMITER###
sed -i 's/moduleNameMapper: {/moduleNameMapper: { "\\.(css|scss)$": "identity-obj-proxy", /' jest.config.js
###ACTION_DELIMITER###
npx jest --config jest.config.js --verbose
###ACTION_DELIMITER###
echo '#!/bin/bash
npx jest --config jest.config.js --verbose --maxWorkers=2 --testTimeout=30000' > /home/polaris/test_commands.sh && chmod +x /home/polaris/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
npx jest --config jest.config.js --verbose --maxWorkers=2 --testTimeout=30000

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
npx jest --config jest.config.js --verbose --maxWorkers=2 --testTimeout=30000

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
npx jest --config jest.config.js --verbose --maxWorkers=2 --testTimeout=30000

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
FROM node:18-bookworm

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
RUN git clone https://github.com/Shopify/polaris.git /home/polaris

WORKDIR /home/polaris
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Shopify", "polaris_5216_to_3994")
class POLARIS_5216_TO_3994(Instance):
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
        # Parse test results, excluding timestamps and capturing skipped tests
        passed_tests = set(re.findall(r'^PASS (.*?)(?: \(\d+\.\d+ s\))?$', log, re.MULTILINE))
        failed_tests = set(re.findall(r'^FAIL (.*?)(?: \(\d+\.\d+ s\))?$', log, re.MULTILINE))
        skipped_tests = set(re.findall(r'^(?:SKIP|SKIPPED|XSKIP):? (.*?)(?: \(\d+\.\d+ s\))?$', log, re.MULTILINE))
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
