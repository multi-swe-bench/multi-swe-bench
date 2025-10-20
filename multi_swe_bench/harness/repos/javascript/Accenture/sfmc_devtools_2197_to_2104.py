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
        return "node:20-bookworm"
    
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
npm install
###ACTION_DELIMITER###
echo 'npm test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npm test -- --verbose

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
npm test -- --verbose

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
npm test -- --verbose

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

# Choose an appropriate base image based on the project's requirements - replace node:20-bookworm with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:20-bookworm

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
RUN git clone https://github.com/Accenture/sfmc-devtools.git /home/sfmc-devtools

WORKDIR /home/sfmc-devtools
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Accenture", "sfmc_devtools_2197_to_2104")
class SFMC_DEVTOOLS_2197_TO_2104(Instance):
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
        passed_tests = set() # Tests that passed successfully
        failed_tests = set() # Tests that failed
        skipped_tests = set() # Tests that were skipped
        import re
        import json
        # Extract test names using hierarchical sections (indentation + === headers)
        test_hierarchy = []
        test_names = set()
        # Regex to match section headers (indentation + ===, e.g., '    Deploy ================')
        section_header = re.compile(r'^(\s+)([^=]+?)\s+={3,}$', re.MULTILINE)  # More permissive text capture
        # Regex to match test cases (indentation without ===, e.g., '  Should create template' or '  test: validate')
        test_case = re.compile(r'^(\s{2,})(.+?)$', re.MULTILINE | re.UNICODE)  # Capture diverse test patterns
        for line in log.split('\n'):
            line = line.rstrip()
            if not line: continue
            # Skip summary lines
            # Skip debug lines
            if 'debug' in line: continue
            # Match section headers (e.g., '    Deploy ================')
            header_match = section_header.match(line)
            if header_match:
                leading_spaces = header_match.group(1)
                text = header_match.group(2).strip()
                current_level = len(leading_spaces)
                # Update hierarchy (pop higher/lower levels)
                while test_hierarchy and test_hierarchy[-1][0] >= current_level:
                    test_hierarchy.pop()
                test_hierarchy.append((current_level, text))
                full_test_name = ' > '.join([t for (l, t) in test_hierarchy])
                test_names.add(full_test_name)
            # Match test cases (leaf nodes, e.g., '  Should create a script template')
            case_match = test_case.match(line)
            if case_match:
                leading_spaces = case_match.group(1)
                text = case_match.group(2).strip()
                if not text or '=' in text or 'debug' in text or 'at Context' in text or 'at process' in text or 'Unexpected number' in text or 'expected - actual' in text or text.startswith(('+', '-', '1)', '10)', '11)', '13)', '16)', '17)', '2)', '20)', '21)')) or 'did not create' in text or 'should not have thrown an error' in text or 'returned metadata' in text or 'returned JSON' in text or 'returned new-JSON' in text or 'returned template JSON' in text or 'was not equal expected' in text or 'does not correspond to' in text or 'failing' in text or 'passing' in text or 'pending' in text : continue  # Skip empty/header/debug lines
                current_level = len(leading_spaces)
                # Update hierarchy for test cases (maintain nested context)
                while test_hierarchy and test_hierarchy[-1][0] > current_level:
                    test_hierarchy.pop()
                # Append as child if same level as last, or new level if deeper
                if test_hierarchy and test_hierarchy[-1][0] == current_level:
                    test_hierarchy.pop()
                test_hierarchy.append((current_level, text))
                full_test_name = ' > '.join([t for (l, t) in test_hierarchy])
                test_names.add(full_test_name)
        # Identify failed tests (numbered entries with error details, e.g., '46) type: triggeredSend')
        failed_tests = set()
        failed_entry = re.compile(r'^\s*(\d+)\)\s*([^\n]+?)(?=\s*:|\n)', re.MULTILINE)
        for match in failed_entry.finditer(log):
            # Extract full test name from failed entry
            failed_hierarchy = []
            for line in match.group(2).split('\n'):
                leading_spaces = len(line) - len(line.lstrip())
                content = line.lstrip().rstrip(':').split(' =')[0]
                if '===' in content: content = content.split('===')[0].strip()
                if not content: continue
                current_level = leading_spaces
                while failed_hierarchy and failed_hierarchy[-1][0] >= current_level:
                    failed_hierarchy.pop()
                failed_hierarchy.append((current_level, line.lstrip()))
            failed_text = ' > '.join([t for (l, t) in failed_hierarchy])
            # Match with extracted test names (case-insensitive)
            matched = False
            for test in test_names:
                if test.lower() in failed_text.lower() or failed_text.lower() in test.lower():
                    failed_tests.add(test)
                    matched = True
                    break
            if not matched:
                failed_tests.add(failed_text)
        # Identify skipped tests (individual 'pending' tests and summary)
        skipped_tests = set()
        # Check for 'pending' in test lines (e.g., '  (pending)')
        pending_test = re.compile(r'^(\s+)([\w\s:,-]+?)\s+\(pending\)$', re.MULTILINE)
        for match in pending_test.finditer(log):
            leading_spaces = match.group(1)
            text = match.group(2).strip()
            current_level = len(leading_spaces)
            # Update hierarchy for pending test
            while test_hierarchy and test_hierarchy[-1][0] >= current_level:
                test_hierarchy.pop()
            test_hierarchy.append((current_level, text))
            full_test_name = ' > '.join([t for (l, t) in test_hierarchy]) + ' (pending)'
            skipped_tests.add(full_test_name)
            test_hierarchy.pop()
        # Check summary for pending count (fallback)
        summary_pending = re.search(r'(\d+)\s*pending', log, re.IGNORECASE)
        if summary_pending and len(skipped_tests) == 0:
            skipped_tests.add(f"{summary_pending.group(1)} pending tests")
        # Calculate passed tests (total tests - failed - skipped)
        passed_tests = test_names - failed_tests - skipped_tests
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
