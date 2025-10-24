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
echo -e '#!/bin/bash
npm run test:unit -- --verbose
npm run test:runner -- --verbose' > test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
npm run test:unit -- --verbose
npm run test:runner -- --verbose

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
npm run test:unit -- --verbose
npm run test:runner -- --verbose

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
npm run test:unit -- --verbose
npm run test:runner -- --verbose

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
RUN git clone https://github.com/codeceptjs/CodeceptJS.git /home/CodeceptJS

WORKDIR /home/CodeceptJS
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("codeceptjs", "CodeceptJS_3393_to_2834")
class CODECEPTJS_3393_TO_2834(Instance):
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

        # Track suite hierarchy and parse test results
        lines = log.split("\n")
        suite_stack = []
        current_indent = 0
        # Regex patterns
        passed_test_pattern = re.compile(r"✓\s+(.*?)\s*(?:\(\d+ms\))?$")
        failed_section_pattern = re.compile(
            r"(\d+ failing)\n(.*?)(?=\n\n|\Z)", re.DOTALL
        )
        # Process lines to track suites and passed tests
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue
            # Determine indent level (number of leading spaces)
            indent = len(line) - len(line.lstrip(" "))
            # Check if line is a suite (no test marker, not an error)
            # Refine suite detection to exclude commands and internal functions
            if (
                "✓" not in line
                and "x" not in line
                and ")" not in line
                and not stripped_line.startswith(("Error:", "at ", ">", "#"))
                and not stripped_line.endswith((":", ";"))
            ):
                # Update suite stack based on indentation
                while len(suite_stack) > 0 and indent <= current_indent:
                    suite_stack.pop()
                suite_stack.append(stripped_line)
                current_indent = indent
                continue
            # Check if line is a passed test
            passed_match = passed_test_pattern.search(line)
            if passed_match:
                test_desc = passed_match.group(1).strip()
                full_test_name = " ".join(suite_stack + [test_desc])
                passed_tests.add(full_test_name)
                continue
        # Process failed tests section
        failed_match = failed_section_pattern.search(log)
        if failed_match:
            failed_content = failed_match.group(2)
            # Split failed tests by numbered entries
            failed_tests_list = re.split(r"\n\s*\d+\)", failed_content)
            for test in failed_tests_list:
                test = test.strip()
                if not test:
                    continue
                # Combine lines and clean up
                test_clean = re.split(r"(Error:|at )", test, maxsplit=1)[0].strip()
                test_lines = [l.strip() for l in test_clean.split("\n") if l.strip()]
                full_test_name = " ".join(test_lines).replace("  ", " ").rstrip(":")
                failed_tests.add(full_test_name)
        # Handle skipped tests (adjust pattern based on log analysis)
        skipped_pattern = re.compile(
            r"^\s*(?:✗|SKIPPED|XFAIL)\s+(.*?)\s*(?:\(\d+ms\))?$", re.MULTILINE
        )
        for match in skipped_pattern.finditer(log):
            test_desc = match.group(1).strip()
            full_test_name = (
                " ".join(suite_stack + [test_desc]) if suite_stack else test_desc
            )
            skipped_tests.add(full_test_name)
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
