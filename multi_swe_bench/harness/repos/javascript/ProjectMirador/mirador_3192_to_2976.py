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
        return "node:14-alpine"

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
                """npm install
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
echo 'npm test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
npm run lint -- --fix
###ACTION_DELIMITER###
npm install eslint@5.x babel-eslint@9.x eslint-plugin-flowtype@2.x eslint-plugin-react-hooks@4.x --legacy-peer-deps
###ACTION_DELIMITER###
eslint ./ --fix
###ACTION_DELIMITER###
npm run lint -- --fix
###ACTION_DELIMITER###
npm install eslint-plugin-react eslint-plugin-import eslint-plugin-jsx-a11y --legacy-peer-deps
###ACTION_DELIMITER###
npm install eslint@6.8.0 --legacy-peer-deps
###ACTION_DELIMITER###
npm install eslint@5.x --legacy-peer-deps
###ACTION_DELIMITER###
npm install eslint-plugin-react@7.24.0 eslint-plugin-import@2.22.1 eslint-plugin-jsx-a11y@6.4.1 --legacy-peer-deps
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && npm install --legacy-peer-deps
###ACTION_DELIMITER###
echo 'npm run build && npm run size && jest -c jest.json --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'npm run build && jest -c jest.json --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'npm run build && ./node_modules/.bin/jest -c jest.json --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apk add --no-cache chromium nss freetype harfbuzz ca-certificates && export PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
###ACTION_DELIMITER###
echo 'npm run build && export PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser && ./node_modules/.bin/jest -c jest.json --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'npm run build && export PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser && export PUPPETEER_ARGS="--no-sandbox" && ./node_modules/.bin/jest -c jest.json --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/sh
/usr/bin/chromium-browser --no-sandbox "$@"' > /usr/local/bin/chromium-browser && chmod +x /usr/local/bin/chromium-browser && echo 'npm run build && export PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chromium-browser && ./node_modules/.bin/jest -c jest.json --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'npm run build && export PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chromium-browser && ./node_modules/.bin/jest -c jest.json --verbose --forceExit --runInBand' > test_commands.sh
###ACTION_DELIMITER###
echo 'npm run build:dev && export PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chromium-browser && ./node_modules/.bin/jest -c jest.json --verbose --forceExit --runInBand' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apk add --no-cache libstdc++ && npm install cheerio@1.0.0-rc.12 --legacy-peer-deps && echo 'npm run build:dev && export PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chromium-browser && ./node_modules/.bin/jest -c jest.json --verbose --forceExit --runInBand' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'npm run build:dev && export PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chromium-browser && ./node_modules/.bin/jest -c jest.json --verbose --forceExit --runInBand --testTimeout=10000 --json --outputFile=test-results.json' > test_commands.sh && bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npm run build:dev && export PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chromium-browser && ./node_modules/.bin/jest -c jest.json --verbose --forceExit --runInBand --testTimeout=10000 --json --outputFile=test-results.json

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
npm run build:dev && export PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chromium-browser && ./node_modules/.bin/jest -c jest.json --verbose --forceExit --runInBand --testTimeout=10000 --json --outputFile=test-results.json

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
npm run build:dev && export PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chromium-browser && ./node_modules/.bin/jest -c jest.json --verbose --forceExit --runInBand --testTimeout=10000 --json --outputFile=test-results.json

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
FROM node:14-alpine

## Set noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Install basic requirements
# For example: RUN apt-get update && apt-get install -y git
# For example: RUN yum install -y git
# For example: RUN apk add --no-cache git
RUN apk add --no-cache git

# Ensure bash is available
RUN if [ ! -f /bin/bash ]; then         if command -v apk >/dev/null 2>&1; then             apk add --no-cache bash;         elif command -v apt-get >/dev/null 2>&1; then             apt-get update && apt-get install -y bash;         elif command -v yum >/dev/null 2>&1; then             yum install -y bash;         else             exit 1;         fi     fi

WORKDIR /home/
COPY fix.patch /home/
COPY test.patch /home/
RUN git clone https://github.com/ProjectMirador/mirador.git /home/mirador

WORKDIR /home/mirador
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ProjectMirador", "mirador_3192_to_2976")
class MIRADOR_3192_TO_2976(Instance):
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
        import itertools

        # Track nested test context (describe blocks) using indentation
        context_stack = []
        test_status = {}
        current_test = None
        # Split log into lines and process line-by-line
        for line in log.split("\n"):
            line = line.rstrip()
            # Detect describe blocks (indentation level 0 or 1)
            describe_match = re.match(r"^(\s*)(describe|context)\s+(.+?):$", line)
            if describe_match:
                indent, block_name = describe_match.groups()
                indent_level = len(indent)
                # Update context stack based on indentation
                while (
                    len(context_stack) > 0
                    and indent_level <= context_stack[-1]["indent"]
                ):
                    context_stack.pop()
                context_stack.append({"name": block_name, "indent": indent_level})
                continue
            # Detect test cases (passed/failed/skipped)
            test_match = re.match(
                r"^(\s*)(✓|✕|×|●|○)\s+(.*?)(\s+\(\d+ ms\)|\s+\(skipped\))?$", line
            )
            if test_match:
                indent, status, test_name, _ = test_match.groups()
                # Build full test name from context stack + test name
                full_test_name = " › ".join(
                    [ctx["name"] for ctx in context_stack] + [test_name]
                )
                # Update status (last occurrence takes precedence)
                if status == "✓":
                    test_status[full_test_name] = "passed"
                elif status == "✕":
                    test_status[full_test_name] = "failed"
                elif status == "○":
                    test_status[full_test_name] = "skipped"
                continue
        # Populate sets from test_status
        passed_tests = set(
            name for name, status in test_status.items() if status == "passed"
        )
        failed_tests = set(
            name for name, status in test_status.items() if status == "failed"
        )
        skipped_tests = set(
            name for name, status in test_status.items() if status == "skipped"
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
