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
                """cat package.json
###ACTION_DELIMITER###
yarn --version
###ACTION_DELIMITER###
yarn install --ignore-engines
###ACTION_DELIMITER###
npx jest --version
###ACTION_DELIMITER###
bash -c 'cat > test_commands.sh <<EOF
#!/bin/bash
# Run unit tests with verbose output
yarn test:unit -- --verbose
# Run type checks with verbose output
yarn typecheck -- --verbose
# Run ESLint with verbose formatting
yarn lint:es -- --format verbose
# Run Stylelint with verbose formatting
yarn lint:style -- --formatter verbose
# Run Prettier check with verbose output
yarn lint:prettier -- --verbose
EOF
chmod +x test_commands.sh'
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
bash -c 'cat > test_commands.sh <<EOF
#!/bin/bash
# Run unit tests with verbose output
yarn --ignore-engines test:unit -- --verbose
# Run type checks with verbose output
yarn --ignore-engines typecheck -- --verbose
# Run ESLint with verbose formatting
yarn --ignore-engines lint:es -- --format verbose
# Run Stylelint with verbose formatting
yarn --ignore-engines lint:style -- --formatter verbose
# Run Prettier check with verbose output
yarn --ignore-engines lint:prettier -- --verbose
EOF
chmod +x test_commands.sh'
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
# Run unit tests with verbose output
yarn --ignore-engines test:unit -- --verbose
# Run type checks with verbose output
yarn --ignore-engines typecheck -- --verbose
# Run ESLint with verbose formatting
yarn --ignore-engines lint:es -- --format verbose
# Run Stylelint with verbose formatting
yarn --ignore-engines lint:style -- --formatter verbose
# Run Prettier check with verbose output
yarn --ignore-engines lint:prettier -- --verbose

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
# Run unit tests with verbose output
yarn --ignore-engines test:unit -- --verbose
# Run type checks with verbose output
yarn --ignore-engines typecheck -- --verbose
# Run ESLint with verbose formatting
yarn --ignore-engines lint:es -- --format verbose
# Run Stylelint with verbose formatting
yarn --ignore-engines lint:style -- --formatter verbose
# Run Prettier check with verbose output
yarn --ignore-engines lint:prettier -- --verbose

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
# Run unit tests with verbose output
yarn --ignore-engines test:unit -- --verbose
# Run type checks with verbose output
yarn --ignore-engines typecheck -- --verbose
# Run ESLint with verbose formatting
yarn --ignore-engines lint:es -- --format verbose
# Run Stylelint with verbose formatting
yarn --ignore-engines lint:style -- --formatter verbose
# Run Prettier check with verbose output
yarn --ignore-engines lint:prettier -- --verbose

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
RUN git clone https://github.com/VKCOM/VKUI.git /home/VKUI

WORKDIR /home/VKUI
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("VKCOM", "VKUI_2692_to_2382")
class VKUI_2692_TO_2382(Instance):
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

        groups = []
        for line in log.split("\n"):
            line = line.rstrip("\r")
            leading_spaces = len(line) - len(line.lstrip())
            level = leading_spaces // 2
            stripped_line = line.strip()
            # Check for passed tests
            pass_match = re.match(r"^✓\s+(.*?)(?:\s+\(\d+ ms\))?$", stripped_line)
            if pass_match:
                test_name = pass_match.group(1)
                full_name = " ".join(groups + [test_name])
                passed_tests.add(full_name)
                continue
            # Check for failed tests
            fail_match = re.match(r"^✕\s+(.*?)(?:\s+\(\d+ ms\))?$", stripped_line)
            if fail_match:
                test_name = fail_match.group(1)
                full_name = " ".join(groups + [test_name])
                failed_tests.add(full_name)
                continue
            # Check for skipped tests
            skip_match = re.match(
                r"^○\s+skipped\s+(.*?)(?:\s+\(\d+ ms\))?$", stripped_line
            )
            if skip_match:
                test_name = skip_match.group(1)
                full_name = " ".join(groups + [test_name])
                skipped_tests.add(full_name)
                continue
            # Update groups for non-test lines (ignore PASS/FAIL/ERROR lines)
            if stripped_line and not stripped_line.startswith(
                ("✓", "✕", "○", "PASS", "FAIL", "ERROR")
            ):
                if level == 0:
                    continue
                if level > len(groups):
                    groups.append(stripped_line)
                else:
                    groups = groups[: level - 1] + [stripped_line]
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
