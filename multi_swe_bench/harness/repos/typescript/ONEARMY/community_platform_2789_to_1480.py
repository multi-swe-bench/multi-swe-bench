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
        return "node:18.17.1"

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
                """yarn add --dev start-server-and-test
###ACTION_DELIMITER###
yarn build:themes && yarn build:components
###ACTION_DELIMITER###
echo '#!/bin/bash
set -eo pipefail

# Unit tests (verbose, non-interactive)
CI=true yarn test:unit --verbose

# Component tests (verbose, non-interactive)
CI=true yarn test:components --verbose

# E2E tests (headless, with server management)
start-server-and-test "yarn start:platform" http://localhost:3000 "yarn workspace oa-cypress cypress run --headless --browser electron --config video=false"' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
set -eo pipefail

# Unit tests (verbose, non-interactive)
CI=true yarn test:unit --verbose

# Component tests (non-interactive)
CI=true yarn test:components

# E2E tests (headless, with server management)
start-server-and-test "yarn start:platform" http://localhost:3000 "yarn workspace oa-cypress cypress run --headless --browser electron --config video=false"' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
set -eo pipefail

# Unit tests (verbose, non-interactive)
CI=true yarn test:unit --verbose

# Component tests (non-interactive)
CI=true yarn test:components

# E2E tests (headless, with server management)
npx start-server-and-test "yarn start:platform" http://localhost:3000 "yarn workspace oa-cypress cypress run --headless --browser electron --config video=false"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y xvfb
###ACTION_DELIMITER###
echo '#!/bin/bash
set -eo pipefail

# Unit tests (verbose, non-interactive)
CI=true yarn test:unit --verbose

# Component tests (non-interactive)
CI=true yarn test:components

# E2E tests (headless with Xvfb and server management)
npx start-server-and-test "yarn start:platform" http://localhost:3000 "xvfb-run yarn workspace oa-cypress cypress run --headless --browser electron --config video=false"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libnss3 libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 libxss1 libasound2 libxtst6
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls packages/oa-cypress
###ACTION_DELIMITER###
yarn workspaces list
###ACTION_DELIMITER###
ls packages/cypress
###ACTION_DELIMITER###
echo '#!/bin/bash
set -eo pipefail

# Unit tests (verbose, non-interactive)
CI=true yarn test:unit --verbose

# Component tests (non-interactive)
CI=true yarn test:components

# E2E tests (headless, correct workspace and baseUrl)
npx start-server-and-test "yarn start:platform" http://localhost:3000 "xvfb-run yarn workspace cypress cypress run --headless --browser electron --config video=false,baseUrl=http://localhost:3000"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
set -eo pipefail

# Unit tests (verbose, non-interactive)
CI=true yarn test:unit --verbose

# Component tests (non-interactive)
CI=true yarn test:components

# E2E tests (headless, correct workspace and baseUrl)
npx start-server-and-test "yarn start:platform" http://localhost:3000 "xvfb-run yarn workspace oa-cypress cypress run --headless --browser electron --config video=false,baseUrl=http://localhost:3000"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
set -eo pipefail

# Unit tests (verbose, non-interactive)
CI=true yarn test:unit --verbose

# Component tests (non-interactive)
CI=true yarn test:components

# E2E tests (headless, extended timeout, verbose, parseable logs)
npx start-server-and-test --timeout 60000 "yarn start:platform" http://localhost:3000 "xvfb-run yarn workspace oa-cypress cypress run --headless --browser electron --config video=false,baseUrl=http://localhost:3000 --verbose --reporter junit"' > test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -eo pipefail

# Unit tests (verbose, non-interactive)
CI=true yarn test:unit --verbose

# Component tests (non-interactive)
CI=true yarn test:components

# E2E tests (headless, extended timeout, verbose, parseable logs)
npx start-server-and-test --timeout 60000 "yarn start:platform" http://localhost:3000 "xvfb-run yarn workspace oa-cypress cypress run --headless --browser electron --config video=false,baseUrl=http://localhost:3000 --verbose --reporter junit"

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
set -eo pipefail

# Unit tests (verbose, non-interactive)
CI=true yarn test:unit --verbose

# Component tests (non-interactive)
CI=true yarn test:components

# E2E tests (headless, extended timeout, verbose, parseable logs)
npx start-server-and-test --timeout 60000 "yarn start:platform" http://localhost:3000 "xvfb-run yarn workspace oa-cypress cypress run --headless --browser electron --config video=false,baseUrl=http://localhost:3000 --verbose --reporter junit"

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
set -eo pipefail

# Unit tests (verbose, non-interactive)
CI=true yarn test:unit --verbose

# Component tests (non-interactive)
CI=true yarn test:components

# E2E tests (headless, extended timeout, verbose, parseable logs)
npx start-server-and-test --timeout 60000 "yarn start:platform" http://localhost:3000 "xvfb-run yarn workspace oa-cypress cypress run --headless --browser electron --config video=false,baseUrl=http://localhost:3000 --verbose --reporter junit"

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

# Choose an appropriate base image based on the project's requirements - replace node:18.17.1 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:18.17.1

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
RUN git clone https://github.com/ONEARMY/community-platform.git /home/community-platform

WORKDIR /home/community-platform
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ONEARMY", "community_platform_2789_to_1480")
class COMMUNITY_PLATFORM_2789_TO_1480(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re

        # Pattern for passed tests: ✓ followed by test name, then (time ms)
        passed_pattern = re.compile(r"✓\s+(.+?)\s+\(\d+ ms\)")
        passed_matches = passed_pattern.findall(log)
        for match in passed_matches:
            passed_tests.add(match.strip())
        # Pattern for failed tests: Extract test names from failed assertions (e.g., test('name', ...) with errors)
        failed_pattern = re.compile(r"✕\s+(.+?)\s+\(\d+ ms\)")
        failed_matches = failed_pattern.findall(log)
        for match in failed_matches:
            failed_tests.add(match.strip())
        # Pattern for skipped tests: ○ followed by test name (Jest todo)
        skipped_pattern = re.compile(
            r'(?:test\.todo\(\s*[\'"].*?|○\s+)(.+?)(?:[\'"\s*\)]|\s+\(\d+ ms\))'
        )
        skipped_matches = skipped_pattern.findall(log)
        for match in skipped_matches:
            skipped_tests.add(match.strip())
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
