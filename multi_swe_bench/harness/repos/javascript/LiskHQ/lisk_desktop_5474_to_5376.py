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
        return "node:18-bullseye-slim"
    
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
                """yarn install:all
###ACTION_DELIMITER###
sed -i 's/"numeral": "git+https:\/\/github.com\/LiskHQ\/Numeral-js.git"/"numeral": "^2.0.6"/' package.json
###ACTION_DELIMITER###
yarn install:all
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
 yarn test -- --verbose
 yarn cypress:run
 yarn cucumber:playwright:open' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e
 yarn test -- --verbose
 yarn cypress:run
 yarn cucumber:playwright:open

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
 yarn test -- --verbose
 yarn cypress:run
 yarn cucumber:playwright:open

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
 yarn test -- --verbose
 yarn cypress:run
 yarn cucumber:playwright:open

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
FROM node:18-bullseye-slim

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
RUN git clone https://github.com/LiskHQ/lisk-desktop.git /home/lisk-desktop

WORKDIR /home/lisk-desktop
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("LiskHQ", "lisk_desktop_5474_to_5376")
class LISK_DESKTOP_5474_TO_5376(Instance):
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
        passed_tests = set()  # type: set[str]
        failed_tests = set()  # type: set[str]
        skipped_tests = set()  # type: set[str]
        import re
        import json
        lines = log.split('\n')
        current_hierarchy = []
        for line in lines:
            leading_spaces = len(line) - len(line.lstrip(' '))
            indent_level = leading_spaces // 2  # Assume 2 spaces per indent level
            content = line.strip()
            if not content:
                continue
            # Check for test markers
            test_marker = None
            if '✓' in content:
                test_marker = '✓'
            elif '✕' in content:
                test_marker = '✕'
            elif '○' in content:
                test_marker = '○'
            if test_marker:
                # Extract test description
                # Split off the time part (e.g., (5 ms))
                parts = content.split(' (', 1)
                test_desc = parts[0].replace(test_marker, '').strip()
                # Combine with current hierarchy
                full_test_name = ' '.join(current_hierarchy + [test_desc]).strip()
                # Categorize
                if test_marker == '✓':
                    passed_tests.add(full_test_name)
                elif test_marker == '✕':
                    failed_tests.add(full_test_name)
                elif test_marker == '○':
                    skipped_tests.add(full_test_name)
            else:
                # Update describe hierarchy
                # Ensure indent_level is valid (>=1)
                if indent_level == 0:
                    # Top-level describe, though unlikely in Jest verbose output
                    current_hierarchy = [content]
                else:
                    # Adjust hierarchy to current indent level
                    if len(current_hierarchy) >= indent_level:
                        # Replace the current level
                        current_hierarchy[indent_level - 1] = content
                        # Truncate to current level
                        current_hierarchy = current_hierarchy[:indent_level]
                    else:
                        # Add new levels
                        while len(current_hierarchy) < indent_level - 1:
                            current_hierarchy.append('')
                        current_hierarchy.append(content)
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
