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
                """cat package.json
###ACTION_DELIMITER###
cat .nvmrc
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && nvm install
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && nvm install
###ACTION_DELIMITER###
node --version
###ACTION_DELIMITER###
nvm --version
###ACTION_DELIMITER###
nvm install v12.18.4
###ACTION_DELIMITER###
npm install --global yarn@3.0.0
###ACTION_DELIMITER###
npm install --global yarn@1.22.19
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
 export CI=true
cp envConfig/local.env .env
yarn test:unit --verbose
yarn test:integration --verbose
yarn test:e2e:local --verbose' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e
 export CI=true
cp envConfig/local.env .env
yarn test:unit --verbose
yarn test:integration --verbose
yarn test:e2e:local --verbose

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
 export CI=true
cp envConfig/local.env .env
yarn test:unit --verbose
yarn test:integration --verbose
yarn test:e2e:local --verbose

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
 export CI=true
cp envConfig/local.env .env
yarn test:unit --verbose
yarn test:integration --verbose
yarn test:e2e:local --verbose

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
RUN git clone https://github.com/bbc/simorgh.git /home/simorgh

WORKDIR /home/simorgh
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("bbc", "simorgh_9567_to_8834")
class SIMORGH_9567_TO_8834(Instance):
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
        # Remove ANSI escape codes from the log
        cleaned_log = re.sub(r'\x1b\[[0-9;]*m', '', log)
        lines = cleaned_log.split('\n')
        current_group = ""
        for line in lines:
            # Reset current group when a new test suite starts (PASS/FAIL)
            if 'PASS' in line or 'FAIL' in line:
                current_group = ""
            # Identify group lines (indented, no test symbols)
            elif '✕' not in line and '✓' not in line and '○' not in line:
                group_match = re.match(r'^\s*(\w[\w\s]*?)\s*$', line)
                if group_match and group_match.group(1):
                    current_group = group_match.group(1)
            # Process test case lines
            else:
                test_case = None
                # Check for failed tests (✕)
                if '✕' in line:
                    match = re.match(r'^\s*✕\s+(.*?)(?:\s*\(\d+ ms\))?\s*$', line)
                    if match:
                        test_case = match.group(1).strip()
                # Check for passed tests (✓)
                elif '✓' in line:
                    match = re.match(r'^\s*✓\s+(.*?)(?:\s*\(\d+ ms\))?\s*$', line)
                    if match:
                        test_case = match.group(1).strip()
                # Check for skipped tests (○)
                elif '○' in line:
                    match = re.match(r'^\s*○\s*(?:skipped\s+)?(.*?)(?:\s*\(\d+ ms\))?\s*$', line)
                    if match:
                        test_case = match.group(1).strip()
                if test_case:
                    full_test_name = f"{current_group} {test_case}" if current_group else test_case
                    if '✕' in line:
                        failed_tests.add(full_test_name)
                    elif '✓' in line:
                        passed_tests.add(full_test_name)
                    elif '○' in line:
                        skipped_tests.add(full_test_name)
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
