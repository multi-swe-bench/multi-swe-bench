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
                """ls -l
###ACTION_DELIMITER###
apt-get update && apt-get install -y maven
###ACTION_DELIMITER###
echo 'mvn clean test -Dstyle.color=never -Dmaven.test.verbose=true -fae' > test_commands.sh
###ACTION_DELIMITER###
mvn install -DskipTests
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls comixed-webui
###ACTION_DELIMITER###
apt-get update && apt-get install -y nodejs yarn
###ACTION_DELIMITER###
apt-get remove -y cmdtest && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list && apt-get update && apt-get install -y yarn
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl gnupg && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list && apt-get update && apt-get install -y yarn
###ACTION_DELIMITER###
cd comixed-webui && yarn install
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && apt-get install -y nodejs
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
cd comixed-webui && yarn run test
###ACTION_DELIMITER###
apt-get update && apt-get install -y chromium && export CHROME_BIN=/usr/bin/chromium
###ACTION_DELIMITER###
export CHROME_BIN=/usr/bin/chromium && cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
export CHROME_BIN=/usr/bin/chromium && cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
cd comixed-webui && cat package.json && yarn run test --verbose
###ACTION_DELIMITER###
echo 'export CHROME_BIN=/usr/bin/chromium && mvn clean test -Dstyle.color=never -Dmaven.test.verbose=true -fae' > /home/comixed/test_commands.sh && cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export CHROME_BIN=/usr/bin/chromium
mvn clean test -Dstyle.color=never -Dmaven.test.verbose=true -fae' > /home/comixed/test_commands.sh && cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
cd comixed-webui && sed -i 's/"test": "ng test --code-coverage"/"test": "ng test --code-coverage --browsers ChromeHeadless --no-watch --no-progress --disable-gpu --no-sandbox"/' package.json && cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libnss3 libgdk-pixbuf2.0-0 libgtk-3-0 libxss1 libasound2 && cd /home/comixed && echo -e 'export CHROME_BIN=/usr/bin/chromium
mvn clean test -Dstyle.color=never -Dmaven.test.verbose=true -X -fae' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
cd comixed-webui && sed -i 's/--no-sandbox/--no-sandbox --verbose/' package.json && cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
cd comixed-webui && yarn run test --verbose
###ACTION_DELIMITER###
sed -i 's/--disable-gpu --no-sandbox//' comixed-webui/package.json && sed -i 's/--verbose//g' comixed-webui/package.json && echo 'module.exports = function(config) { config.set({ customLaunchers: { ChromeHeadlessCustom: { base: "ChromeHeadless", flags: ["--no-sandbox", "--disable-gpu"] } }, browsers: ["ChromeHeadlessCustom"] }) }; ' > comixed-webui/karma.conf.js && cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/--disable-gpu --no-sandbox//' package.json && sed -i 's/--verbose//g' package.json && echo 'module.exports = function(config) { config.set({ customLaunchers: { ChromeHeadlessCustom: { base: "ChromeHeadless", flags: ["--no-sandbox", "--disable-gpu"] } }, browsers: ["ChromeHeadlessCustom"] }) }; ' > karma.conf.js && cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
cd /home/comixed/comixed-webui && sed -i 's/--browsers ChromeHeadless --no-watch --no-progress --disable-gpu --no-sandbox --verbose//' package.json && echo 'module.exports = function(config) { config.set({ browsers: ["ChromeHeadless"], customLaunchers: { ChromeHeadless: { base: "Chrome", flags: ["--headless", "--disable-gpu", "--no-sandbox"] } }, singleRun: true }) }; ' > karma.conf.js && cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
cd /home/comixed/comixed-webui && sed -i 's/--browsers ChromeHeadless --no-watch --no-progress --disable-gpu --no-sandbox --verbose//' package.json && echo 'module.exports = function(config) { config.set({ browsers: ["ChromeHeadless"], customLaunchers: { ChromeHeadless: { base: "Chrome", flags: ["--headless=new", "--disable-gpu", "--no-sandbox"] } }, singleRun: true }) }; ' > karma.conf.js && cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
cd /home/comixed/comixed-webui && sed -i 's/"test": ".*"/"test": "ng test --code-coverage --browsers ChromeHeadless --no-watch --no-progress"/' package.json && echo 'module.exports = function(config) { config.set({ browsers: ["ChromeHeadless"], customLaunchers: { ChromeHeadless: { base: "Chrome", flags: ["--headless=new", "--disable-gpu", "--no-sandbox"] } }, singleRun: true }) }; ' > karma.conf.js && export CHROME_BIN=/usr/bin/chromium && yarn run test && cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
cd /home/comixed/comixed-webui && echo 'module.exports = function(config) { config.set({ frameworks: ["jasmine"], plugins: [require("karma-jasmine"), require("karma-chrome-launcher"), require("karma-jasmine-html-reporter"), require("karma-coverage")], customLaunchers: { ChromeHeadless: { base: "Chrome", flags: ["--headless=new", "--disable-gpu", "--no-sandbox"] } }, browsers: ["ChromeHeadless"], reporters: ["progress", "kjhtml"], port: 9876, colors: true, logLevel: config.LOG_INFO, autoWatch: false, singleRun: true, concurrency: Infinity }) }; ' > karma.conf.js && yarn run test && cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
cd /home/comixed/comixed-webui && ls src/**/*.spec.ts && cat karma.conf.js && cat angular.json && cd /home/comixed
###ACTION_DELIMITER###
cd /home/comixed/comixed-webui && cat src/test.ts && echo '---' && cat karma.conf.js && cd /home/comixed
###ACTION_DELIMITER###
cd /home/comixed/comixed-webui && echo '{ "extends": "./tsconfig.json", "compilerOptions": { "outDir": "./out-tsc/spec", "types": [ "jasmine", "node" ] }, "files": [ "src/test.ts", "src/polyfills.ts" ], "include": [ "src/**/*.spec.ts", "src/**/*.d.ts" ] }' > tsconfig.spec.json && ng test --code-coverage --browsers ChromeHeadless --no-watch --no-progress && cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
cd /home/comixed/comixed-webui && npm install && sed -i 's/"ng /".\/node_modules\/.bin\/ng /' package.json && yarn run test && cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
cd /home/comixed/comixed-webui && npm install --legacy-peer-deps && ./node_modules/.bin/ng test --code-coverage --browsers ChromeHeadless --no-watch --no-progress && cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
cd /home/comixed/comixed-webui && ./node_modules/.bin/ng test --code-coverage --browsers ChromeHeadless --no-watch --no-progress --verbose && cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
cd /home/comixed/comixed-webui && ./node_modules/.bin/ng test --code-coverage --browsers ChromeHeadless --no-watch --no-progress && cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
cd /home/comixed/comixed-webui && echo '{ "extends": "./tsconfig.json", "compilerOptions": { "outDir": "./out-tsc/spec", "types": [ "jasmine", "node" ] }, "files": [ "src/test.ts", "src/polyfills.ts" ], "include": [ "src/**/*.spec.ts", "src/**/*.d.ts" ] }' > tsconfig.spec.json && ./node_modules/.bin/ng test --code-coverage --browsers ChromeHeadless --no-watch --no-progress && cd /home/comixed && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
export CHROME_BIN=/usr/bin/chromium
mvn clean test -Dstyle.color=never -Dmaven.test.verbose=true -X -fae

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
export CHROME_BIN=/usr/bin/chromium
mvn clean test -Dstyle.color=never -Dmaven.test.verbose=true -X -fae

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
export CHROME_BIN=/usr/bin/chromium
mvn clean test -Dstyle.color=never -Dmaven.test.verbose=true -X -fae

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


@Instance.register("comixed", "comixed_2221_to_1523")
class COMIXED_2221_TO_1523(Instance):
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
        import json
        # TODO: Implement the parse_log function
        # Use regex to find all test results
        pattern = re.compile(r'\[INFO\]\s+([\w-]+)\s+\.{2,}\s+(SUCCESS|FAILURE|SKIPPED)\s+\[.+\]')
        matches = pattern.findall(log)
        for test_name, status in matches:
            if status == 'SUCCESS':
                passed_tests.add(test_name)
            elif status == 'FAILURE':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
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
