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
        return "node:20-bullseye-slim"

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
npm install
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
git config --global url."https://github.com/".insteadOf "git@github.com:"
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
git config --global url."https://github.com/".insteadOf "git://github.com/"
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
git config --global url."https://github.com/".insteadOf "ssh://git@github.com/"
###ACTION_DELIMITER###
git config --global --list
###ACTION_DELIMITER###
cat /root/.gitconfig
###ACTION_DELIMITER###
git config --global url."https://github.com/".insteadOf "git@github.com:"
###ACTION_DELIMITER###
cat /root/.gitconfig
###ACTION_DELIMITER###
git config --global url."https://github.com/".insteadOf "ssh://git@github.com/"
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
git clone https://github.com/gilt/gonzales-pe.git
###ACTION_DELIMITER###
apt-get update && apt-get install -y ca-certificates
###ACTION_DELIMITER###
npm cache clean --force
###ACTION_DELIMITER###

###ACTION_DELIMITER###
npm install --legacy-peer-deps --verbose
###ACTION_DELIMITER###
npm install --legacy-peer-deps --verbose
###ACTION_DELIMITER###
sed -i '/"jest": {/,/}/a\  "overrides": {\n    "gonzales-pe": "git+https://github.com/gilt/gonzales-pe.git"\n  },' package.json
###ACTION_DELIMITER###
sed -i '/"overrides": {/d' package.json
###ACTION_DELIMITER###
sed -i '$i\  "overrides": {\n    "gonzales-pe": "git+https://github.com/gilt/gonzales-pe.git"\n  }' package.json
###ACTION_DELIMITER###
sed -i '$i\  "overrides": {\n    "gonzales-pe": "git+https://github.com/gilt/gonzales-pe.git"\n  }' package.json
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
sed -i 's/  "overrides": {/,
  "overrides": {/' package.json
###ACTION_DELIMITER###
apt-get update && apt-get install -y jq
###ACTION_DELIMITER###
jq '. + { "overrides": { "gonzales-pe": "git+https://github.com/gilt/gonzales-pe.git" } }' package.json > temp.json && mv temp.json package.json
###ACTION_DELIMITER###
sed -i '148d' package.json
###ACTION_DELIMITER###
jq . package.json
###ACTION_DELIMITER###
git checkout package.json
###ACTION_DELIMITER###
jq '. + { "overrides": { "gonzales-pe": "git+https://github.com/gilt/gonzales-pe.git" } }' package.json > temp.json && mv temp.json package.json
###ACTION_DELIMITER###
jq . package.json
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
jq '.overrides."gonzales-pe" = "git+https://github.com/tonyganch/gonzales-pe.git"' package.json > temp.json && mv temp.json package.json
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
jq '.scripts.prepublish = "echo skipping prepublish"' package.json > temp.json && mv temp.json package.json
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
echo 'npm test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo 'npm run jest -- --verbose' > test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npm run jest -- --verbose

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
npm run jest -- --verbose

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
npm run jest -- --verbose

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
FROM node:20-bullseye-slim

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
RUN git clone https://github.com/ant-design/ant-design.git /home/ant-design

WORKDIR /home/ant-design
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ant-design", "ant_design_1936_to_1623")
class ANT_DESIGN_1936_TO_1623(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        import json  # Included as per skeleton

        # Clean log by removing leading [  n] line numbers
        log_clean = re.sub(r"^\[\s*\d+\]\s*", "", log, flags=re.MULTILINE)
        lines = log_clean.split("\n")
        current_suite = None
        current_file_status = None
        for i, line in enumerate(lines):
            # Match test file lines to get status and suite name
            file_match = re.match(
                r"^(PASS|FAIL)\s+tests/[\w-]+\.test\.js\s+\(\d+\.\d+s\)$", line.strip()
            )
            if file_match:
                current_file_status = file_match.group(1)
                # Find first non-blank line for suite name
                j = i + 1
                while j < len(lines) and lines[j].strip() == "":
                    j += 1
                if j < len(lines):
                    current_suite = lines[j].strip()
                continue
            # Match test cases with ✓ (pass) or ✕ (fail) using 2-space indent
            test_match = re.match(
                r"^  (✓|✕) (.*)$", line
            )  # 2 spaces before, 1 space after symbol
            if test_match and current_suite and current_file_status:
                status_symbol, test_desc = test_match.groups()
                test_name = f"{current_suite} {test_desc}"
                if status_symbol == "✓" and current_file_status == "PASS":
                    passed_tests.add(test_name)
                elif status_symbol == "✕" and current_file_status == "FAIL":
                    failed_tests.add(test_name)
                continue
            # Match failed tests: error line (-) linked to previous test case line
            if current_suite and current_file_status == "FAIL":
                error_match = re.match(r"^  - (.*)$", line)  # 2 spaces before error
                if error_match and i > 0:
                    prev_line = lines[i - 1].strip()
                    prev_test_match = re.match(rf"^{current_suite} › (.*)$", prev_line)
                    if prev_test_match:
                        test_name = f"{current_suite} {prev_test_match.group(1)}"
                        failed_tests.add(test_name)
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
