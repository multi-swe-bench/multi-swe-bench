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
        return "node:lts-alpine"
    
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
echo 'npm test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'npm test -- --verbose --modulePaths=./' > test_commands.sh
###ACTION_DELIMITER###
echo 'npm test -- --verbose --testPathIgnorePatterns=node_modules' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|src/api/**/jest.config.js|src/api/*/jest.config.js|g' jest.config.js
###ACTION_DELIMITER###
sed -i '/module.exports = {/a \  modulePathIgnorePatterns: ["node_modules"],' jest.config.js
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|src/api/**/jest.config.js|src/api/*/jest.config.js|g' jest.config.js
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|<rootDir>/src/api/**/jest.config.js|<rootDir>/src/api/*/jest.config.js|g' jest.config.js
###ACTION_DELIMITER###
sed -i 's|<rootDir>/src/api/*/jest.config.js|<rootDir>/src/api/**/jest.config.js|g' jest.config.js && sed -i '/<rootDir>\/src\/api\/\*\*\/jest\.config\.js/a \    \'!<rootDir>/src/api/**/node_modules/**\',' jest.config.js
###ACTION_DELIMITER###
sed -i 's|\*\*/jest.config.js|*/jest.config.js|g' jest.config.js
###ACTION_DELIMITER###
echo 'npm test -- --verbose --testPathIgnorePatterns=node_modules/@senecacdot/satellite' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
npm install @babel/core@^7.22.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'npm test -- --verbose --testPathIgnorePatterns=node_modules/@senecacdot/satellite --updateSnapshot --runInBand' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'npm test -- --verbose --testPathIgnorePatterns=node_modules/@senecacdot/satellite --updateSnapshot --runInBand --testTimeout=30000' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npm test -- --verbose --testPathIgnorePatterns=node_modules/@senecacdot/satellite --updateSnapshot --runInBand --testTimeout=30000

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
npm test -- --verbose --testPathIgnorePatterns=node_modules/@senecacdot/satellite --updateSnapshot --runInBand --testTimeout=30000

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
npm test -- --verbose --testPathIgnorePatterns=node_modules/@senecacdot/satellite --updateSnapshot --runInBand --testTimeout=30000

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

# Choose an appropriate base image based on the project's requirements - replace node:lts-alpine with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:lts-alpine

## Set noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Install basic requirements
# For example: RUN apt-get update && apt-get install -y git
# For example: RUN yum install -y git
# For example: RUN apk add --no-cache git
RUN apk add --no-cache git

# Ensure bash is available
RUN if [ ! -f /bin/bash ]; then         if command -v apk >/dev/null 2>&1; then             apk add --no-cache bash;         elif command -v apt-get >/dev/null 2>&1; then             apt-get update && apt-get install -y bash;         elif command -v yum >/dev/null 2>&1; then             yum install -y bash;         else             exit 1;         fi     fi

WORKDIR /home/
COPY fix.patch /home/
COPY test.patch /home/
RUN git clone https://github.com/Seneca-CDOT/telescope.git /home/telescope

WORKDIR /home/telescope
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Seneca-CDOT", "telescope_2200_to_2173")
class TELESCOPE_2200_TO_2173(Instance):
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
        passed_tests = set[str]()
        failed_tests = set[str]()
        skipped_tests = set[str]()
        import re
        import json
        # Regex patterns to match test results with duration
        # Regex patterns to match test results with duration (adjusted for indentation and line boundaries)
        passed_pattern = re.compile(r'^\s*✓\s+(.+?)\s*(\(\d+ ms\))?\s*$')
        failed_pattern = re.compile(r'^\s*(✕|●)\s+(?!Test suite failed)(.+?)\s*(\(\d+ ms\))?\s*$')
        skipped_pattern = re.compile(r'^\s*○\s+(.+?)\s*(\(\d+ ms\))?\s*$')
        # Track test statuses, keeping the last occurrence
        test_status = {}
        for line in log.split('\n'):
            # Check for passed tests
            passed_match = passed_pattern.match(line)
            if passed_match:
                test_name = passed_match.group(1).strip()
                test_status[test_name] = 'passed'
            # Check for failed tests
            failed_match = failed_pattern.match(line)
            if failed_match:
                test_name = failed_match.group(2).strip()
                test_status[test_name] = 'failed'
            # Check for skipped tests
            skipped_match = skipped_pattern.match(line)
            if skipped_match:
                test_name = skipped_match.group(1).strip()
                test_status[test_name] = 'skipped'
        # Populate the sets based on the final status
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
