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
        return "python:3.9-slim"
    
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
make virtualenv
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make virtualenv
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3-virtualenv
###ACTION_DELIMITER###
make virtualenv
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list && apt-get update && apt-get install -y yarn
###ACTION_DELIMITER###
make virtualenv
###ACTION_DELIMITER###
echo -e '#!/bin/bash
. .venvpython3/bin/activate
trial -v buildbot' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
trial --help
###ACTION_DELIMITER###
echo -e '#!/bin/bash
. .venvpython3/bin/activate
.venvpython3/bin/trial --verbose buildbot' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
make trial' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
make trial

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
make trial

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
make trial

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.9-slim

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
RUN git clone https://github.com/buildbot/buildbot.git /home/buildbot

WORKDIR /home/buildbot
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("buildbot", "buildbot_8452_to_6274")
class BUILDBOT_8452_TO_6274(Instance):
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
        processed_tests = set()  # Track tests already classified
        import re
        import json
        lines = log.split('\n')
        hierarchy = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Strip [number] prefix from log lines
            stripped_line = re.sub(r'^\[\d+\]\s*', '', line)
            leading_spaces = re.match(r'^(\s*)', stripped_line).group(1)
            level = len(leading_spaces) // 2
            text = stripped_line.strip()
            # Handle hierarchical test cases with ... [STATUS]
            test_case_match = re.search(r'^(.*?)\s+\.\.\.\s+\[(\w+)\]$', text)
            if test_case_match:
                test_name_part = test_case_match.group(1)
                status = test_case_match.group(2)
                # Update hierarchy to current level
                if level < len(hierarchy):
                    hierarchy = hierarchy[:level]
                else:
                    while len(hierarchy) < level:
                        hierarchy.append('')
                hierarchy.append(test_name_part)
                full_test_name = '.'.join(hierarchy)
                # Categorize by status (avoid duplicates)
                if full_test_name not in processed_tests:
                    if status == 'OK':
                        passed_tests.add(full_test_name)
                    elif status in ['ERROR', 'FAILED']:
                        failed_tests.add(full_test_name)
                    elif status == 'SKIPPED':
                        skipped_tests.add(full_test_name)
                    processed_tests.add(full_test_name)
                hierarchy.pop()  # Remove test part for next iteration
            else:
                # Update hierarchy for suite lines
                if level < len(hierarchy):
                    hierarchy = hierarchy[:level]
                else:
                    while len(hierarchy) < level:
                        hierarchy.append('')
                if level < len(hierarchy):
                    hierarchy[level] = text
                else:
                    hierarchy.append(text)
            i += 1
        # Handle flat test cases (e.g., [ERROR], [SKIPPED] with separators)
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # Check if current line is a separator
            if re.fullmatch(r'^[=-]+$', line):
                # Check if next line is a status line
                if i + 1 < len(lines):
                    status_line = lines[i+1].strip()
                    status_match = re.fullmatch(r'^\[(\w+)\]$', status_line)
                    if status_match:
                        status = status_match.group(1)
                        # Collect all test names before the separator
                        test_names = []
                        j = i - 1
                        while j >= 0:
                            test_line = lines[j].strip()
                            # Check if test_line is a valid test name and not processed
                            if re.match(r'^buildbot\.test\..+\.test_\w+$', test_line) and test_line not in processed_tests:
                                test_names.append(test_line)
                                j -= 1
                            else:
                                break
                        # Add collected test names to the appropriate set
                        for test_name in test_names:
                            if status == 'ERROR':
                                failed_tests.add(test_name)
                            elif status == 'SKIPPED':
                                skipped_tests.add(test_name)
                            elif status == 'OK':
                                passed_tests.add(test_name)
                            processed_tests.add(test_name)
                        # Move i to after the status line
                        i += 2
                        continue
            i += 1
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
