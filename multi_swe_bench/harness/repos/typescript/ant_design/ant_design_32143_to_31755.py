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
                """cat README.md
###ACTION_DELIMITER###
cat package.json
###ACTION_DELIMITER###
cat .jest.js
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
npm install --legacy-peer-deps --save-dev web-streams-polyfill @wojtekmaj/enzyme-adapter-react-17
###ACTION_DELIMITER###
cat tests/setup.js
###ACTION_DELIMITER###
sed -i '1i const { TextEncoder, TextDecoder } = require(\'util\');\nglobal.TextEncoder = TextEncoder;\nglobal.TextDecoder = TextDecoder;\nconst { ReadableStream } = require(\'web-streams-polyfill\');\nglobal.ReadableStream = ReadableStream;' tests/setup.js
###ACTION_DELIMITER###
sed -i '1i const { TextEncoder, TextDecoder } = require('\''util'\'');\nglobal.TextEncoder = TextEncoder;\nglobal.TextDecoder = TextDecoder;\nconst { ReadableStream } = require('\''web-streams-polyfill'\'');\nglobal.ReadableStream = ReadableStream;' tests/setup.js
###ACTION_DELIMITER###
echo 'npm test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/"license": "MIT"/a \  "overrides": { "undici": "5.28.4" },' package.json && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/"license": "MIT"/a \  "overrides": { "cheerio": "1.0.0-rc.10" },' package.json && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps
###ACTION_DELIMITER###
sed -i '/"license": "MIT"/a \  "overrides": { "undici": "5.28.4", "cheerio": "0.22.0" },' package.json && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps
###ACTION_DELIMITER###
sed -i '/"license": "MIT"/a \  "overrides": { "undici": "5.28.4", "cheerio": "1.0.0-rc.10" },' package.json && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/"license": "MIT"/a \  "overrides": { "undici": "5.28.4", "cheerio": "0.22.0" },' package.json && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/"license": "MIT"/a \  "overrides": { "undici": "5.28.4", "cheerio": "1.0.0-rc.0" },' package.json && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/"overrides": {/,/}/d' package.json && sed -i '/"license": "MIT"/a \  "overrides": { "undici": "5.28.4", "cheerio": "0.22.0" },' package.json && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/"overrides": {/,/}/d' package.json && sed -i '/"license": "MIT"/a \  "overrides": { "undici": "5.28.4", "enzyme>cheerio": "0.22.0" },' package.json && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/"overrides": {/,/}/d' package.json && sed -i '/"license": "MIT"/a \  "overrides": { "undici": "5.28.4", "enzyme": { "cheerio": "0.22.0" } },' package.json && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/"license": "MIT",/a \  "overrides": { "undici": "5.28.4", "enzyme": { "cheerio": "0.22.0" } },' package.json && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/"license": "MIT",/a \  "overrides": { "undici": "5.28.4", "enzyme": { "cheerio": "0.22.0" } },' package.json && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y jq && jq '.overrides = { "undici": "5.28.4", "enzyme": { "cheerio": "0.22.0" } }' package.json > package.tmp && mv package.tmp package.json && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && bash test_commands.sh
###ACTION_DELIMITER###
jq 'del(.overrides)' package.json > package.tmp && mv package.tmp package.json && jq '.overrides = { "undici": "5.28.4", "enzyme": { "cheerio": "0.22.0" } }' package.json > package.tmp && mv package.tmp package.json && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && bash test_commands.sh
###ACTION_DELIMITER###
jq . package.json > package.tmp && mv package.tmp package.json && jq '.overrides = { "undici": "5.28.4", "enzyme": { "cheerio": "0.22.0" } }' package.json > package.tmp && mv package.tmp package.json && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && bash test_commands.sh
###ACTION_DELIMITER###
jq 'del(.overrides)' package.json 2>/dev/null | jq . > package.tmp && mv package.tmp package.json && jq '.overrides = { "undici": "5.28.4", "enzyme": { "cheerio": "0.22.0" } }' package.json > package.tmp && mv package.tmp package.json && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && bash test_commands.sh
###ACTION_DELIMITER###
git checkout package.json && jq '.overrides = { "undici": "5.28.4", "enzyme": { "cheerio": "0.22.0" } }' package.json > package.tmp && mv package.tmp package.json && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps && bash test_commands.sh
###ACTION_DELIMITER###
npm install --save-dev web-streams-polyfill && bash test_commands.sh
###ACTION_DELIMITER###
npm install --save-dev web-streams-polyfill --legacy-peer-deps && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/npm test -- --verbose/npm test -- --verbose -u/' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/npm test -- --verbose -u/npm test -- --verbose/' test_commands.sh && bash test_commands.sh"""
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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
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
RUN git clone https://github.com/ant-design/ant-design.git /home/ant-design

WORKDIR /home/ant-design
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ant-design", "ant_design_32143_to_31755")
class ANT_DESIGN_32143_TO_31755(Instance):
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
        # Implement the log parsing logic here
        # Regex patterns for passed, failed, and skipped tests
        passed_pattern = re.compile(r'\s*✓\s+(.*?)\s+\(\d+\s+ms\)')
        failed_pattern = re.compile(r'\s*✕\s+(.*?)\s+\(\d+\s+ms\)')
        skipped_pattern = re.compile(r'\s*○ skipped\s+(.*)')
        # Find all matches
        passed_matches = passed_pattern.findall(log)
        failed_matches = failed_pattern.findall(log)
        skipped_matches = skipped_pattern.findall(log)
        # Update the sets
        passed_tests.update(passed_matches)
        failed_tests.update(failed_matches)
        skipped_tests.update(skipped_matches)
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
