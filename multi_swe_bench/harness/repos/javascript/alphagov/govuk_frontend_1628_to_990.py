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
apt-get update
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
###ACTION_DELIMITER###
nvm install 10.15.1
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
echo 'npm test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
npm install chokidar@^3.3.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
git checkout package-lock.json && rm -rf node_modules && npm install
###ACTION_DELIMITER###
npm ci
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'standard && gulp test && gulp copy-assets && jest --testPathIgnorePatterns="after-*" --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'npx standard && gulp test && gulp copy-assets && jest --testPathIgnorePatterns="after-*" --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'npx standard && npx gulp test && npx gulp copy-assets && npx jest --testPathIgnorePatterns="after-*" --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libnss3 libcups2 libxss1 libxrandr2 libgconf-2-4 libasound2 libpangocairo-1.0-0 libatk1.0-0 libatk-bridge2.0-0 libgtk-3-0
###ACTION_DELIMITER###
apt-get update && apt-get install -y libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libnss3 libcups2t64 libxss1 libxrandr2 libasound2t64 libpangocairo-1.0-0 libatk1.0-0t64 libatk-bridge2.0-0t64 libgtk-3-0t64
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npx standard && npx gulp test && npx gulp copy-assets && npx jest --testPathIgnorePatterns="after-*" --verbose

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
npx standard && npx gulp test && npx gulp copy-assets && npx jest --testPathIgnorePatterns="after-*" --verbose

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
npx standard && npx gulp test && npx gulp copy-assets && npx jest --testPathIgnorePatterns="after-*" --verbose

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
RUN git clone https://github.com/alphagov/govuk-frontend.git /home/govuk-frontend

WORKDIR /home/govuk-frontend
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("alphagov", "govuk_frontend_1628_to_990")
class GOVUK_FRONTEND_1628_TO_990(Instance):
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
        # Pattern for passed tests: matches lines with ✓ followed by test name and duration
        passed_pattern = re.compile(r'^\s+✓\s+(.*?)\s*\(\d+ms\)$', re.MULTILINE)
        passed_tests = set(passed_pattern.findall(log))
        # Extract all test names (passed/failed) by matching lines with mandatory ✓/✕ and duration
        all_tests_pattern = re.compile(r'^\s+[✓✕]\s+(.*?)\s*\(\d+ms\)$', re.MULTILINE)
        all_tests = set(all_tests_pattern.findall(log))
        # Failed tests are test names in all_tests but not in passed_tests
        failed_tests = all_tests - passed_tests
        # Pattern for skipped tests: assuming '-' as marker (adjust if needed)
        skipped_pattern = re.compile(r'^\s+-\s+(.*?)\s*\(\d+ms\)$', re.MULTILINE)
        skipped_matches = skipped_pattern.findall(log)
        for match in skipped_matches:
            skipped_tests.add(match.strip())
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
