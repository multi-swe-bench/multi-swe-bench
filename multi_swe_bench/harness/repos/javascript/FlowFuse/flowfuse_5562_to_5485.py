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
                """ls
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
echo -e '#!/bin/bash
npm test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
npm run test:unit:forge -- --verbose
npm run test:unit:frontend -- --verbose
npm run test:system -- --verbose' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
npm run test:unit:forge -- --verbose
npm run test:unit:frontend -- --verbose
npm run test:system -- --verbose

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
npm run test:unit:forge -- --verbose
npm run test:unit:frontend -- --verbose
npm run test:system -- --verbose

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
npm run test:unit:forge -- --verbose
npm run test:unit:frontend -- --verbose
npm run test:system -- --verbose

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
RUN git clone https://github.com/FlowFuse/flowfuse.git /home/flowfuse

WORKDIR /home/flowfuse
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("FlowFuse", "flowfuse_5562_to_5485")
class FLOWFUSE_5562_TO_5485(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        # Parse log lines to extract test suites and results
        current_suite = ""
        # Regex patterns to match test suites and test cases
        suite_pattern = re.compile(r'^\s+(?!\d+\))(\w+.*?)\s*$')  # Matches suites, excluding failed tests
        passed_pattern = re.compile(r'^\s+✔\s+(.*)$')      # Matches passed tests (flexible indentation)
        failed_pattern = re.compile(r'^\s+\d+\)\s*(?!.*at )(?:"([^"]+)" hook (?:for|in) "([^"]+)"|([^:]+))$')  # Excludes stack traces and limits direct test capture
        skipped_pattern = re.compile(r'^\s+(?:✖|SKIPPED)\s+(.*)$')  # Matches skipped tests (flexible indentation)
        for line in log.split('\n'):
            # Remove leading line number and brackets
            cleaned_line = re.sub(r'^\[\s*\d+\]\s*', '', line)
            # Skip stack trace lines
            if 'at ' in cleaned_line:
                continue
            # Update current test suite if cleaned line matches a suite
            suite_match = suite_pattern.match(cleaned_line)
            if suite_match:
                current_suite = suite_match.group(1).strip()
                continue
            # Check for passed tests in cleaned line
            passed_match = passed_pattern.match(cleaned_line)
            if passed_match:
                test_name = f"{current_suite} > {passed_match.group(1).strip()}" if current_suite else passed_match.group(1).strip()
                passed_tests.add(test_name)
                continue
            # Check for failed tests in cleaned line
            failed_match = failed_pattern.match(cleaned_line)
            if failed_match:
                # Handle hook failures (group 2) or direct test failures (group 3)
                hook_test = failed_match.group(2)
                direct_test = failed_match.group(3)
                if hook_test:
                    test_name = f"{current_suite} > {hook_test.strip()}" if current_suite else hook_test.strip()
                elif direct_test:
                    test_name = f"{current_suite} > {direct_test.strip()}" if current_suite else direct_test.strip()
                else:
                    test_name = "Unknown test (fix parser)"
                failed_tests.add(test_name)
                continue
            # Check for skipped tests in cleaned line
            skipped_match = skipped_pattern.match(cleaned_line)
            if skipped_match:
                test_name = f"{current_suite} > {skipped_match.group(1).strip()}" if current_suite else skipped_match.group(1).strip()
                skipped_tests.add(test_name)
                continue
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
