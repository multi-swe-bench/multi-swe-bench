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
        return "node:18.12.0"

    def image_prefix(self) -> str:
        return "envagent"

    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:
        repo_name = self.pr.repo
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
yarn install:all
###ACTION_DELIMITER###
git clone https://github.com/LiskHQ/Numeral-js.git && cd Numeral-js && git log --pretty=format:%H | grep 195af9768f998c4e4acde3ec86388b17c7c0254b
###ACTION_DELIMITER###
git log --pretty=format:%H | grep 195af9768f998c4e4acde3ec86388b17c7c0254b
###ACTION_DELIMITER###
git log --pretty=format:%H -n 10
###ACTION_DELIMITER###
cd ..
###ACTION_DELIMITER###
sed -i 's|"numeral": "git+https://github.com/LiskHQ/Numeral-js.git"|"numeral": "git+https://github.com/LiskHQ/Numeral-js.git#3673d4898e8b58c609b104e5c4e615d4e429f66d"|g' package.json
###ACTION_DELIMITER###
yarn install:all
###ACTION_DELIMITER###
echo -e '#!/bin/bash

yarn test --verbose
 yarn cypress:run --reporter spec
 yarn cucumber:playwright:open --format pretty' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash

yarn test --verbose
 yarn cypress:run --reporter spec
 yarn cucumber:playwright:open --format pretty

""".replace("[[REPO_NAME]]", repo_name),
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

yarn test --verbose
 yarn cypress:run --reporter spec
 yarn cucumber:playwright:open --format pretty

""".replace("[[REPO_NAME]]", repo_name),
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

yarn test --verbose
 yarn cypress:run --reporter spec
 yarn cucumber:playwright:open --format pretty

""".replace("[[REPO_NAME]]", repo_name),
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
FROM node:18.12.0

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


@Instance.register("LiskHQ", "lisk_desktop_5175_to_5135")
class LISK_DESKTOP_5175_TO_5135(Instance):
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

        return "bash /home/run.sh"

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

        lines = log.split("\n")
        current_groups = []
        current_test_file = ""
        for line in lines:
            leading_spaces = len(line) - len(line.lstrip(" "))
            level = leading_spaces // 2
            content = line.lstrip(" ")
            # Check for passed tests (✓)
            if content.startswith("✓ "):
                match = re.match(r"✓ (.*?)\s*\(\d+ ms\)$", content)
                if match:
                    test_desc = match.group(1)
                    test_name = (
                        f"{current_test_file} {' '.join(current_groups + [test_desc])}"
                        if current_test_file
                        else " ".join(current_groups + [test_desc])
                    )
                    passed_tests.add(test_name)
            # Handle test file passes
            elif content.startswith("PASS "):
                match = re.match(r"PASS (.*?)(\s*\(\d+\.\d+ s\))?$", content)
                if match:
                    test_file = match.group(1)
                    current_test_file = test_file
                    current_groups = []
            # Handle test file failures
            elif content.startswith("FAIL "):
                match = re.match(r"FAIL (.*?)(\s*\(\d+\.\d+ s\))?$", content)
                if match:
                    test_file = match.group(1)
                    current_test_file = test_file
                    current_groups = []
            # Check for failed tests (Jest uses ✕ or ● for failures)
            elif content.startswith("✕ "):
                match = re.match(r"✕ (.*?)(\s*\(\d+ ms\)|:|Error:|Failed:|$)", content)
                if match:
                    test_desc = match.group(1)
                    test_name = (
                        f"{current_test_file} {' '.join(current_groups + [test_desc])}"
                        if current_test_file
                        else " ".join(current_groups + [test_desc])
                    )
                    failed_tests.add(test_name)
            elif content.startswith("● "):
                # Extract test name from suite failures
                match = re.match(r"●\s*(.*?)(\s*[:(]|$)", content)
                if match:
                    test_desc = match.group(1).strip()
                    test_name = (
                        f"{current_test_file} {' '.join(current_groups + [test_desc])}"
                        if current_test_file
                        else " ".join(current_groups + [test_desc])
                    )
                    failed_tests.add(test_name)
            # Check for skipped tests (○)
            elif content.startswith("○ "):
                match = re.match(r"○ (.*?)\s*\(\d+ ms\)$", content)
                if match:
                    test_desc = match.group(1)
                    test_name = (
                        f"{current_test_file} {' '.join(current_groups + [test_desc])}"
                        if current_test_file
                        else " ".join(current_groups + [test_desc])
                    )
                    skipped_tests.add(test_name)
            # Update current groups (ignore file-level lines)
            else:
                group_name = content.rstrip(" :\t\n\r")
                if (
                    group_name
                    and not group_name.startswith(
                        (
                            "PASS",
                            "FAIL",
                            "SKIPPED",
                            "error",
                            "info",
                            "Summary",
                            "at ",
                            "warning",
                            "failed",
                        )
                    )
                    and "error" not in group_name.lower()
                    and "failed" not in group_name.lower()
                ):
                    if level < len(current_groups):
                        current_groups = current_groups[:level]
                    elif level == len(current_groups):
                        if current_groups:
                            current_groups[-1] = group_name
                        else:
                            current_groups.append(group_name)
                    else:
                        # Add missing levels
                        while len(current_groups) < level:
                            current_groups.append("")
                        current_groups[level - 1] = group_name
        parsed_results = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
        }

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
