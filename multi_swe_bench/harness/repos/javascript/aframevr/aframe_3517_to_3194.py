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
        return "node:18-bullseye"

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
                """ls -la
###ACTION_DELIMITER###
chromium --version || apt-get update && apt-get install -y chromium
###ACTION_DELIMITER###
echo 'CHROME_BIN=/usr/bin/chromium npm test -- --browsers ChromeHeadless --single-run --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
which chromium && apt-get install -y libnss3 libxss1 libasound2 libatk-bridge2.0-0 libgtk-3-0
###ACTION_DELIMITER###
echo 'CHROME_BIN=/usr/bin/chromium npm test -- --browsers ChromeHeadless --single-run --verbose --chromeFlags="--no-sandbox --disable-gpu --headless=new"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ln -s /usr/bin/chromium /usr/bin/chrome && which chrome
###ACTION_DELIMITER###
sed -i '/ChromeTravis: {/a \  ChromeHeadless: {\n    base: "Chrome",\n    flags: ["--no-sandbox", "--disable-gpu", "--headless=new"]\n  },' tests/karma.conf.js
###ACTION_DELIMITER###
echo 'CHROME_BIN=/usr/bin/chromium npm test -- --browsers ChromeHeadless --single-run --verbose --log-level debug' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
/usr/bin/chromium --headless=new --disable-gpu --no-sandbox --remote-debugging-port=9222 about:blank
###ACTION_DELIMITER###
echo 'XDG_RUNTIME_DIR=/tmp CHROME_BIN=/usr/bin/chromium npm test -- --browsers ChromeHeadless --single-run --verbose --chromeFlags="--no-sandbox --disable-gpu --headless=new --disable-software-rasterizer --disable-dev-shm-usage"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'npm test -- --browsers Firefox --single-run --verbose' > test_commands.sh
###ACTION_DELIMITER###
which firefox || apt-get install -y firefox-esr
###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i '/ChromeTravis: {/a \  FirefoxHeadless: {\n    base: "Firefox",\n    flags: ["-headless"]\n  },' tests/karma.conf.js
###ACTION_DELIMITER###
echo 'npm test -- --browsers FirefoxHeadless --single-run --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
firefox-esr --headless about:blank
###ACTION_DELIMITER###
apt-get install -y xvfb && echo 'xvfb-run -a npm test -- --browsers Firefox --single-run --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/mocha: {ui: 'tdd'}/a \      timeout: 60000,' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/browsers: \['Firefox', 'Chrome'\],/a \  browserNoActivityTimeout: 60000,' tests/karma.conf.js
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
xvfb-run -a npm test -- --browsers Firefox --single-run --verbose

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
xvfb-run -a npm test -- --browsers Firefox --single-run --verbose

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
xvfb-run -a npm test -- --browsers Firefox --single-run --verbose

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
FROM node:18-bullseye

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
RUN git clone https://github.com/aframevr/aframe.git /home/aframe

WORKDIR /home/aframe
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("aframevr", "aframe_3517_to_3194")
class AFRAME_3517_TO_3194(Instance):
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

        # Implement the log parsing logic here
        import re
        import re

        # Strip ANSI color codes and line numbers
        ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        log_clean = ansi_escape.sub("", log)
        # Remove line number prefixes (e.g., [  20] )
        log_clean = re.sub(r"^\[\s*\d+\]\s", "", log_clean, flags=re.MULTILINE)
        # Pattern to match test lines (status symbols: ✔, ✖, ℹ)
        test_pattern = re.compile(
            r"^(\s*)(✔|✖|ℹ)\s+(.*)$"
        )  # Matches status with any leading spaces
        # Pattern to match parent categories (no status symbol)
        group_pattern = re.compile(r"^(\s*)([^✔✖ℹ].*)$")
        current_groups = []
        for line in log_clean.split("\n"):
            line = line.rstrip()  # Preserve leading spaces
            if not line.strip():
                continue
            # Skip log lines
            if any(
                keyword in line
                for keyword in [
                    "LOG:",
                    "INFO",
                    "WARNING",
                    "Timeout",
                    "require<",
                    "WARN",
                    "404:",
                ]
            ):
                continue
            # Match test lines (status symbols with leading spaces)
            test_match = test_pattern.match(line)
            if test_match:
                spaces, status, test_part = test_match.groups()
                indent_level = (
                    len(spaces) // 2
                )  # 2 spaces = level 1, 4 spaces = level 2, etc.
                # Update groups based on indentation
                if indent_level == 0:
                    current_groups = [test_part]
                else:
                    current_groups = current_groups[:indent_level] + [test_part]
                full_test = " > ".join(current_groups)
                if status == "✔":
                    passed_tests.add(full_test)
                elif status == "✖":
                    failed_tests.add(full_test)
                elif status == "ℹ":
                    skipped_tests.add(full_test)
            # Match parent categories (non-status lines with leading spaces)
            group_match = group_pattern.match(line)
            if group_match:
                spaces, group_name = group_match.groups()
                group_indent = len(spaces) // 2
                current_groups = current_groups[:group_indent] + [group_name.strip()]
        # Parse summary for skipped tests (fallback)
        summary_match = re.search(r"SUMMARY:.*ℹ (\d+) tests? skipped", log_clean)
        if summary_match and not skipped_tests:
            skipped_tests.add(
                f"Skipped {summary_match.group(1)} tests (summary fallback)"
            )
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
