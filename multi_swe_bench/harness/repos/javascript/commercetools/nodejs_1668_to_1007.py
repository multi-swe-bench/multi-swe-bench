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
yarn install
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn test -- --verbose
yarn test:integration -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
yarn test -- --verbose
yarn test:integration -- --verbose

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
yarn test -- --verbose
yarn test:integration -- --verbose

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
yarn test -- --verbose
yarn test:integration -- --verbose

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

# Choose an appropriate base image based on the project's requirements - replace node:18 with actual base image
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
RUN git clone https://github.com/commercetools/nodejs.git /home/nodejs

WORKDIR /home/nodejs
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("commercetools", "nodejs_1668_to_1007")
class NODEJS_1668_TO_1007(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re
        test_file_pattern = re.compile(r'^(PASS|FAIL)\s+(test .*?\.spec\.js)')  # Capture test file path
        test_case_pattern = re.compile(r'[✓✕]\s+([^\(]+?)(?:\s*\(\d+ ms\))?$')  # Handle optional execution time
        group_stack = []
        current_test_file = None
        for line in log.split('\n'):
            content = re.sub(r'^\[\s*\d+\]\s*', '', line).rstrip()
            if not content:
                continue
            # Detect new test file and reset hierarchy
            file_match = test_file_pattern.match(content)
            if file_match:
                current_test_file = file_match.group(2)
                group_stack = [current_test_file]  # Start stack with test file
                continue
            # Process test cases (✓/✕)
            if '✓' in content or '✕' in content:
                if not current_test_file:
                    continue  # Skip if no test file context
                leading_spaces = len(content) - len(content.lstrip())
                status = '✓' if '✓' in content else '✕'
                # Extract test name (with optional execution time)
                case_match = test_case_pattern.search(content)
                if not case_match:
                    continue
                test_name = case_match.group(1).strip()
                # Calculate depth (test file is level 0, groups start at level 1)
                depth = (leading_spaces // 2)  # 2 spaces per level
                while len(group_stack) > depth:
                    group_stack.pop()
                # Build full unique test name
                full_test_name = ' > '.join(group_stack + [test_name])
                if status == '✓':
                    passed_tests.add(full_test_name)
                else:
                    failed_tests.add(full_test_name)
            # Process nested groups (e.g., describe blocks)
            else:
                if not current_test_file:
                    continue  # Skip if no test file context
                # Skip error lines (e.g., Jest failure messages)
                if '●' in content:
                    continue
                leading_spaces = len(content) - len(content.lstrip())
                group_name = content.strip()
                depth = (leading_spaces // 2)  # 2 spaces per level
                # Adjust stack to current depth (test file is level 0)
                while len(group_stack) > depth:
                    group_stack.pop()
                if len(group_stack) == depth:
                    group_stack.append(group_name)
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
