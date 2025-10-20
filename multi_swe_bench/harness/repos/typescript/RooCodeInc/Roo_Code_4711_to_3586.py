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
        return "ubuntu:22.04"
    
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
turbo test --help
###ACTION_DELIMITER###
pnpm exec turbo --help
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
###ACTION_DELIMITER###
apt-get install -y nodejs
###ACTION_DELIMITER###
corepack enable && corepack prepare pnpm@10.8.1 --activate
###ACTION_DELIMITER###
pnpm install
###ACTION_DELIMITER###
pnpm exec turbo test --help
###ACTION_DELIMITER###
echo 'pnpm test -- --output-logs full --verbosity 2' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pnpm test --output-logs full --verbosity 2' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'turbo test --log-order grouped --output-logs full --verbosity 2' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pnpm exec turbo test --log-order grouped --output-logs full --verbosity 2' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pnpm exec turbo test --log-order grouped --output-logs full --verbosity 2

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
pnpm exec turbo test --log-order grouped --output-logs full --verbosity 2

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
pnpm exec turbo test --log-order grouped --output-logs full --verbosity 2

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:22.04 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:22.04

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
RUN git clone https://github.com/RooCodeInc/Roo-Code.git /home/Roo-Code

WORKDIR /home/Roo-Code
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("RooCodeInc", "Roo_Code_4711_to_3586")
class ROO_CODE_4711_TO_3586(Instance):
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
        # Remove ANSI escape codes
        log_clean = re.sub(r'\x1B\[[0-9;]*[mK]', '', log)
        # Extract all test suites (e.g., @roo-code/telemetry:test)
        test_suites_pattern = re.compile(r'(\S+):test:', re.IGNORECASE)
        all_suites = set(test_suites_pattern.findall(log_clean))
        all_suites = {f"{suite}#test" for suite in all_suites}
        # Pattern for failed tests: Capture 'Failed: <test>' or '<test>#test: ... exited (1)'
        failed_pattern = re.compile(r'Failed:\s+(\S+)|(\S+)#test:.*exited \(1\)', re.IGNORECASE)
        failed_matches = failed_pattern.findall(log_clean)
        # Combine results from both capture groups
        failed_tests = set()
        for match in failed_matches:
            test = match[0] or match[1]
            if test:
                # Filter out invalid test names (e.g., 'command')
                if not (test.startswith('@roo-code/') or test.startswith('roo-cline')):
                    continue
                # Ensure consistent format (add #test if missing)
                if '#test' not in test:
                    test += '#test'
                failed_tests.add(test)
        # Passed tests = all suites - failed suites
        passed_tests = all_suites - failed_tests
        # Pattern for skipped tests: Capture 'skipped' in test summaries
        skipped_pattern = re.compile(r'(\S+#test)[^\n]*skipped', re.IGNORECASE)
        skipped_tests.update(skipped_pattern.findall(log_clean))
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
