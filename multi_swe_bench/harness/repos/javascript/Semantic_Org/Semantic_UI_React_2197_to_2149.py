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
        return "node:20"
    
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
                """ls
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip python-is-python3
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2 python2-dev
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian oldstable main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python2.7 python2.7-dev
###ACTION_DELIMITER###
npm install -g node-gyp@latest && yarn install
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && source ~/.nvm/nvm.sh && nvm install 18 && nvm use 18 && yarn install
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python2.7 python2.7-dev
###ACTION_DELIMITER###
PYTHON=/usr/bin/python2.7 yarn install
###ACTION_DELIMITER###
yarn add node-sass@7.0.0 && yarn install
###ACTION_DELIMITER###
yarn add node-sass@9.0.0 && PYTHON=/usr/bin/python2.7 yarn install
###ACTION_DELIMITER###
yarn test
###ACTION_DELIMITER###
apt-get update && apt-get install -y libx11-xcb1
###ACTION_DELIMITER###
apt-get update && apt-get install -y libnss3 libxss1 libasound2 libatk-bridge2.0-0 libgtk-3-0 libgbm1
###ACTION_DELIMITER###
yarn test
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgconf-2-4
###ACTION_DELIMITER###
yarn test
###ACTION_DELIMITER###
sed -i 's/browsers: \[\'ChromeHeadless\'\]/browsers: \[\'puppeteer\'\]/' karma.conf.babel.js && sed -i '/--stack-trace-limit 50000/a \      "--no-sandbox",' karma.conf.babel.js
###ACTION_DELIMITER###
sed -i "/'--stack-trace-limit 50000'/a \  '--no-sandbox'," karma.conf.babel.js
###ACTION_DELIMITER###
yarn test
###ACTION_DELIMITER###
sed -i "s/browsers: \['ChromeHeadless'\]/browsers: \['puppeteer'\]/" karma.conf.babel.js
###ACTION_DELIMITER###
yarn test
###ACTION_DELIMITER###
echo 'yarn test' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn test

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
yarn test

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
yarn test

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
FROM node:20

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
RUN git clone https://github.com/Semantic-Org/Semantic-UI-React.git /home/Semantic-UI-React

WORKDIR /home/Semantic-UI-React
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Semantic-Org", "Semantic_UI_React_2197_to_2149")
class SEMANTIC_UI_REACT_2197_TO_2149(Instance):
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
        # Extract test names using regex patterns
        passed_pattern = re.compile(r'^\s*✔\s*(.*)$', re.MULTILINE)
        failed_pattern = re.compile(r'^\s*✖\s*(.*)$', re.MULTILINE)
        passed_tests = set(match.strip() for match in passed_pattern.findall(log) if "tests completed" not in match)
        failed_tests = set(match.strip() for match in failed_pattern.findall(log) if "test failed" not in match)
        # Skipped tests not identified in sampled logs
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
