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
                """ls -la
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
yarn --version
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python-is-python3
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2 && export PYTHON=python2
###ACTION_DELIMITER###
npm install -g node-gyp@latest
###ACTION_DELIMITER###
PYTHON=python3 yarn install
###ACTION_DELIMITER###
npm install node-gyp@latest
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
yarn test --verbose
###ACTION_DELIMITER###
echo 'yarn test --verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn test --verbose

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
yarn test --verbose

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
yarn test --verbose

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
RUN git clone https://github.com/carbon-design-system/ibm-security.git /home/ibm-security

WORKDIR /home/ibm-security
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("carbon-design-system", "ibm_security_196_to_6")
class IBM_SECURITY_196_TO_6(Instance):
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
        # Track test context (describe blocks) and indentation
        context = []
        passed_pattern = re.compile(r'^(\s+)✓\s+(.*?)(?:\s+\(\d+ms\))?$', re.MULTILINE)
        failed_pattern = re.compile(r'^(\s+)✕\s+(.*?)(?:\s+\(\d+ms\))?$', re.MULTILINE)
        for line in log.split('\n'):
            # Update context based on describe blocks (lines with no ✓/✕ but indentation)
            describe_match = re.match(r'^(\s+)(\w+.*)$', line)
            if describe_match and '✓' not in line and '✕' not in line:
                indent = len(describe_match.group(1))
                # Remove context entries with greater or equal indentation
                while context and context[-1][0] >= indent:
                    context.pop()
                context.append((indent, describe_match.group(2)))
            # Check for passed tests
            passed_match = passed_pattern.match(line)
            if passed_match:
                indent = len(passed_match.group(1))
                test_name = passed_match.group(2).strip()
                # Build full test name from context
                full_name = ' '.join([ctx[1] for ctx in context]) + ' ' + test_name
                passed_tests.add(full_name.strip())
            # Check for failed tests
            failed_match = failed_pattern.match(line)
            if failed_match:
                indent = len(failed_match.group(1))
                test_name = failed_match.group(2).strip()
                full_name = ' '.join([ctx[1] for ctx in context]) + ' ' + test_name
                failed_tests.add(full_name.strip())
        # Skipped tests (assuming similar structure)
        skipped_pattern = re.compile(r'^(\s+)○\s+(.*?)(?:\s+\(\d+ms\))?$', re.MULTILINE)
        for line in log.split('\n'):
            skipped_match = skipped_pattern.match(line)
            if skipped_match:
                indent = len(skipped_match.group(1))
                test_name = skipped_match.group(2).strip()
                full_name = ' '.join([ctx[1] for ctx in context]) + ' ' + test_name
                skipped_tests.add(full_name.strip())
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
