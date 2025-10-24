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
                """curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
###ACTION_DELIMITER###
nvm install 16
###ACTION_DELIMITER###
nvm use 16
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential python3 libsass-dev libssl-dev
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
sed -i 's/"rU"/"r"/g' /home/hospitalrun-frontend/node_modules/node-gyp/gyp/pylib/gyp/input.py
###ACTION_DELIMITER###
find /home/hospitalrun-frontend/node_modules -name input.py
###ACTION_DELIMITER###
npm install --legacy-peer-deps --ignore-scripts
###ACTION_DELIMITER###
find /home/hospitalrun-frontend/node_modules -name input.py
###ACTION_DELIMITER###
sed -i 's/"rU"/"r"/g' /home/hospitalrun-frontend/node_modules/node-gyp/gyp/pylib/gyp/input.py
###ACTION_DELIMITER###
npm rebuild
###ACTION_DELIMITER###
mkdir -p node_modules/node-sass/vendor/linux-x64-93 && curl -L https://github.com/sass/node-sass/releases/download/v5.0.0/linux-x64-93_binding.node -o node_modules/node-sass/vendor/linux-x64-93/binding.node
###ACTION_DELIMITER###
nvm install 14 && nvm use 14
###ACTION_DELIMITER###
mkdir -p node_modules/node-sass/vendor/linux-x64-83 && curl -L https://github.com/sass/node-sass/releases/download/v5.0.0/linux-x64-83_binding.node -o node_modules/node-sass/vendor/linux-x64-83/binding.node
###ACTION_DELIMITER###
npm rebuild
###ACTION_DELIMITER###
npm run translation:check && react-scripts test --verbose --testPathIgnorePatterns=src/__tests__/test-utils --env=jest-environment-jsdom-sixteen
###ACTION_DELIMITER###
sed -i 's/"esModuleInterop": true/"esModuleInterop": true, "skipLibCheck": true/' /home/hospitalrun-frontend/scripts/tsconfig.json
###ACTION_DELIMITER###
npm run translation:check
###ACTION_DELIMITER###
npm install typescript@4.1 --legacy-peer-deps
###ACTION_DELIMITER###
react-scripts test --verbose --testPathIgnorePatterns=src/__tests__/test-utils --env=jest-environment-jsdom-sixteen
###ACTION_DELIMITER###
npm install react-scripts@~3.4.0 --legacy-peer-deps
###ACTION_DELIMITER###
./node_modules/.bin/react-scripts test --verbose --testPathIgnorePatterns=src/__tests__/test-utils --env=jest-environment-jsdom-sixteen
###ACTION_DELIMITER###
cross-env CI=true ./node_modules/.bin/react-scripts test --verbose --testPathIgnorePatterns=src/__tests__/test-utils --env=jest-environment-jsdom-sixteen --maxWorkers=2
###ACTION_DELIMITER###
npm install cross-env@~7.0.0 --legacy-peer-deps
###ACTION_DELIMITER###
./node_modules/.bin/cross-env CI=true ./node_modules/.bin/react-scripts test --verbose --testPathIgnorePatterns=src/__tests__/test-utils --env=jest-environment-jsdom-sixteen --maxWorkers=2
###ACTION_DELIMITER###
echo './node_modules/.bin/cross-env CI=true ./node_modules/.bin/react-scripts test --verbose --testPathIgnorePatterns=src/__tests__/test-utils --env=jest-environment-jsdom-sixteen --maxWorkers=2' > /home/hospitalrun-frontend/test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
./node_modules/.bin/cross-env CI=true ./node_modules/.bin/react-scripts test --verbose --testPathIgnorePatterns=src/__tests__/test-utils --env=jest-environment-jsdom-sixteen --maxWorkers=2

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
./node_modules/.bin/cross-env CI=true ./node_modules/.bin/react-scripts test --verbose --testPathIgnorePatterns=src/__tests__/test-utils --env=jest-environment-jsdom-sixteen --maxWorkers=2

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
./node_modules/.bin/cross-env CI=true ./node_modules/.bin/react-scripts test --verbose --testPathIgnorePatterns=src/__tests__/test-utils --env=jest-environment-jsdom-sixteen --maxWorkers=2

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
RUN git clone https://github.com/HospitalRun/hospitalrun-frontend.git /home/hospitalrun-frontend

WORKDIR /home/hospitalrun-frontend
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("HospitalRun", "hospitalrun_frontend_2644_to_2479")
class HOSPITALRUN_FRONTEND_2644_TO_2479(Instance):
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
        import json

        # TODO: Implement the parse_log function
        # Split log into lines
        lines = log.split("\n")
        hierarchy = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            # Calculate leading spaces to determine indentation level (2 spaces per level)
            leading_spaces = len(line) - len(line.lstrip(" "))
            current_level = leading_spaces // 2
            # Check if the line is a test case (passed or failed)
            if stripped.startswith(("✓", "✕", "○")) or "SKIPPED" in stripped:
                # Extract test name (remove status symbol and duration)
                match = re.match(r"^[✓✕○] (.*?) \(\d+ms\)$", stripped) or re.search(
                    r"SKIPPED (.*)", stripped
                )
                if match:
                    test_name_part = match.group(1)
                    full_test_name = " ".join(hierarchy + [test_name_part])
                    if stripped.startswith("✓"):
                        passed_tests.add(full_test_name)
                    elif stripped.startswith("✕"):
                        failed_tests.add(full_test_name)
                    elif stripped.startswith("○") or "SKIPPED" in stripped:
                        skipped_tests.add(full_test_name)
            else:
                # Update hierarchy for group lines
                group_name = stripped.rstrip()  # Remove trailing spaces
                # Adjust hierarchy based on current level
                if current_level < len(hierarchy):
                    # Move up the hierarchy
                    hierarchy = hierarchy[:current_level]
                    hierarchy.append(group_name)
                elif current_level == len(hierarchy):
                    # Replace current level's group name
                    if hierarchy:
                        hierarchy[-1] = group_name
                    else:
                        hierarchy.append(group_name)
                else:
                    # Move down the hierarchy (add new level)
                    # Fill in any missing levels (if indentation skips levels)
                    while len(hierarchy) < current_level:
                        hierarchy.append("")  # Placeholder, though unlikely
                    hierarchy.append(group_name)
        # Implement the log parsing logic here
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
