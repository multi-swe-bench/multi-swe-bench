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
        return "node:20"
    
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
sed -i 's|"numeral": "git+https://github.com/LiskHQ/Numeral-js.git"|"numeral": "git+https://github.com/LiskHQ/Numeral-js.git#195af9768f998c4e4acde3ec86388b17c7c0254b"|g' package.json
###ACTION_DELIMITER###
yarn install:all
###ACTION_DELIMITER###
git clone https://github.com/LiskHQ/Numeral-js.git /tmp/numeral-js && cd /tmp/numeral-js && git fetch --all && git checkout 195af9768f998c4e4acde3ec86388b17c7c0254b
###ACTION_DELIMITER###
sed -i 's|"numeral": "git+https://github.com/LiskHQ/Numeral-js.git#195af9768f998c4e4acde3ec86388b17c7c0254b"|"numeral": "2.0.6"|g' /home/lisk-desktop/package.json
###ACTION_DELIMITER###
cd /home/lisk-desktop && yarn install:all
###ACTION_DELIMITER###
yarn install:all --ignore-engines
###ACTION_DELIMITER###
echo -e '#!/bin/bash
 yarn test --verbose
 yarn cypress:run --reporter json' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y xvfb libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 libxtst6 xauth
###ACTION_DELIMITER###
sed -i 's|yarn cypress:run --reporter json|xvfb-run yarn cypress:run --reporter json|g' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
yarn add --dev wait-on
###ACTION_DELIMITER###
yarn add --dev wait-on --ignore-engines
###ACTION_DELIMITER###
sed -i 's|yarn cypress:run --reporter json|yarn dev & SERVER_PID=$!; wait-on http://localhost:8080; xvfb-run yarn cypress:run --reporter json; kill $SERVER_PID|g' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
 yarn test --verbose
 yarn dev &
 SERVER_PID=$!
 npx wait-on http://localhost:8080
 xvfb-run yarn cypress:run --reporter json
 kill $SERVER_PID' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
 set -e
 yarn test --verbose
 yarn dev &
 SERVER_PID=$!
 yarn wait-on --timeout 30000 http://localhost:8080
 xvfb-run yarn cypress:run --reporter json
 kill $SERVER_PID' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
 yarn test --verbose || true
 yarn dev &
 SERVER_PID=$!
 yarn wait-on --timeout 60000 http://localhost:8080
 xvfb-run yarn cypress:run --reporter json || true
 kill $SERVER_PID' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
 yarn test --verbose || true
 yarn dev &
 SERVER_PID=$!
 yarn wait-on --timeout 60000 http://localhost:8080
 xvfb-run yarn cypress:run --reporter json || true
 kill $SERVER_PID

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
 yarn test --verbose || true
 yarn dev &
 SERVER_PID=$!
 yarn wait-on --timeout 60000 http://localhost:8080
 xvfb-run yarn cypress:run --reporter json || true
 kill $SERVER_PID

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
 yarn test --verbose || true
 yarn dev &
 SERVER_PID=$!
 yarn wait-on --timeout 60000 http://localhost:8080
 xvfb-run yarn cypress:run --reporter json || true
 kill $SERVER_PID

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

# Choose an appropriate base image based on the project's requirements - replace node:20 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:20

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


@Instance.register("LiskHQ", "lisk_desktop_5252_to_5176")
class LISK_DESKTOP_5252_TO_5176(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        current_suite = None  # Track the current test suite name
        current_block = None  # Track if we're in a FAIL or PASS block
        for line in log.split('\n'):
            # Update current block based on FAIL/PASS lines
            if line.startswith('FAIL '):
                current_block = 'fail'
            elif line.startswith('PASS '):
                current_block = 'pass'
            # Track test suite names (indented, no status symbol)
            suite_match = re.match(r'^\s{2,}([^\s✕✓]+)\s*$', line)  # 2+ spaces, no ✕/✓
            if suite_match:
                current_suite = suite_match.group(1).strip()
                continue
            # Match individual test lines (4+ spaces, ✕/✓, test name, duration)
            jest_test = re.match(r'^\s{4,}(✕|✓)\s+(.+?)\s+\(\d+\s+ms\)$', line)  # 4+ spaces for tests
            if jest_test and current_suite and current_block:
                status, test_name = jest_test.groups()
                full_test_name = f"{current_suite} {test_name.strip()}"  # Combine suite + test name
                if status == '✕' and current_block == 'fail':
                    failed_tests.add(full_test_name)
                elif status == '✓' and current_block == 'pass':
                    passed_tests.add(full_test_name)
            # Remove feature test logic (optional, if not needed)
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
