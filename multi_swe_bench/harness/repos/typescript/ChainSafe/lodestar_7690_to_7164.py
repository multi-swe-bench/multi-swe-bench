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
        return "node:20-bookworm"
    
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
yarn install
###ACTION_DELIMITER###
echo 'yarn test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
yarn build
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-17-jre
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'PORT=0 yarn test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
netstat -tulpn | grep :37421
###ACTION_DELIMITER###
apt-get update && apt-get install -y net-tools
###ACTION_DELIMITER###
netstat -tulpn | grep :37421
###ACTION_DELIMITER###
echo 'pkill node || true; PORT=0 yarn test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
wget https://github.com/ConsenSys/web3signer/releases/download/23.6.0/web3signer-23.6.0.tar.gz && tar -xzf web3signer-23.6.0.tar.gz && mv web3signer-23.6.0 /usr/local/bin/ && ln -s /usr/local/bin/web3signer-23.6.0/bin/web3signer /usr/local/bin/web3signer
###ACTION_DELIMITER###
wget https://github.com/ConsenSys/web3signer/releases/download/23.11.0/web3signer-23.11.0.tar.gz && tar -xzf web3signer-23.11.0.tar.gz && mv web3signer-23.11.0 /usr/local/bin/ && ln -s /usr/local/bin/web3signer-23.11.0/bin/web3signer /usr/local/bin/web3signer
###ACTION_DELIMITER###
wget https://github.com/ConsenSys/web3signer/releases/download/24.6.0/web3signer-24.6.0.tar.gz && tar -xzf web3signer-24.6.0.tar.gz && mv web3signer-24.6.0 /usr/local/bin/ && ln -s /usr/local/bin/web3signer-24.6.0/bin/web3signer /usr/local/bin/web3signer
###ACTION_DELIMITER###
wget https://github.com/ConsenSys/web3signer/releases/download/23.6.0/web3signer-23.6.0-apache.tar.gz && tar -xzf web3signer-23.6.0-apache.tar.gz && mv web3signer-23.6.0 /usr/local/bin/ && ln -s /usr/local/bin/web3signer-23.6.0/bin/web3signer /usr/local/bin/web3signer"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pkill node || true; PORT=0 yarn test -- --verbose

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
pkill node || true; PORT=0 yarn test -- --verbose

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
pkill node || true; PORT=0 yarn test -- --verbose

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

# Choose an appropriate base image based on the project's requirements - replace node:20-bookworm with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:20-bookworm

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
RUN git clone https://github.com/ChainSafe/lodestar.git /home/lodestar

WORKDIR /home/lodestar
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ChainSafe", "lodestar_7690_to_7164")
class LODESTAR_7690_TO_7164(Instance):
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
        # TODO: Implement the parse_log function
        # Regex patterns to match test lines and ANSI codes
        test_pattern = re.compile(r'@lodestar/[^:]+:  (\x1b\[32m✓\x1b\[39m|\x1b\[31m×\x1b\[39m) (.*)')
        ansi_pattern = re.compile(r'\x1b\[[0-9;]*m')
        # Parse each test line
        for match in test_pattern.finditer(log):
            status_part = match.group(1)
            test_name_part = match.group(2)
            # Remove ANSI escape codes from the test name
            clean_test_name = ansi_pattern.sub('', test_name_part).strip()
            # Determine test status and add to the appropriate set
            if '✓' in status_part:
                passed_tests.add(clean_test_name)
            elif '×' in status_part:
                failed_tests.add(clean_test_name)
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
