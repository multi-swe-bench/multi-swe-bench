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
        return "ubuntu:latest"

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
go version
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y wget build-essential
###ACTION_DELIMITER###
wget https://dl.google.com/go/go1.13.15.linux-amd64.tar.gz
###ACTION_DELIMITER###
tar -C /usr/local -xzf go1.13.15.linux-amd64.tar.gz
###ACTION_DELIMITER###
export PATH=$PATH:/usr/local/go/bin && go version
###ACTION_DELIMITER###
go mod download
###ACTION_DELIMITER###
echo 'go test -v -count=1 ./...' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
apt-get install -y postgresql
###ACTION_DELIMITER###
pg_ctlcluster 16 main start
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
go test -v -count=1 ./...

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
go test -v -count=1 ./...

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
go test -v -count=1 ./...

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:latest with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:latest

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
RUN git clone https://github.com/artifacthub/hub.git /home/hub

WORKDIR /home/hub
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("artifacthub", "hub_174_to_55")
class HUB_174_TO_55(Instance):
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

        # Pattern to match test status lines (e.g., "--- PASS: TestName (0.00s)")
        status_pattern = r"^\s*--- (\w+): (.*?) \(\d+\.?\d*s\)$"
        status_matches = re.findall(status_pattern, log, re.MULTILINE)
        # Pattern to match test start lines (e.g., "=== RUN   TestName")
        run_pattern = r"^\s*=== RUN\s+(\S+)$"
        all_tests = set(re.findall(run_pattern, log, re.MULTILINE))
        # Pattern to match suite-level FAIL (e.g., "FAIL" at the end of the log)
        suite_fail_pattern = r"^\s*FAIL\s*$"
        suite_failed = re.search(suite_fail_pattern, log, re.MULTILINE) is not None
        # Pattern to match compilation/setup errors (e.g., "h.MethodName undefined (type ...)")
        error_pattern = r"^\s*internal/.*?_test\.go:\d+:\d+: h\.(\w+) undefined.*"
        compilation_errors = re.findall(error_pattern, log, re.MULTILINE)
        for status, test_name in status_matches:
            status = status.upper()
            if status == "PASS":
                passed_tests.add(test_name)
            elif status in ("FAIL", "ERROR"):  # Handle ERROR as failure
                failed_tests.add(test_name)
            elif status in ("SKIP", "SKIPPED"):  # Handle SKIP and SKIPPED
                skipped_tests.add(test_name)
        # Mark tests that started but didn't complete as failed
        completed_tests = passed_tests.union(failed_tests).union(skipped_tests)
        failed_tests.update(all_tests - completed_tests)
        # If suite failed and no failed tests captured, assume compilation errors affected tests
        if suite_failed and not failed_tests and compilation_errors:
            # Extract method names from compilation errors and form test names
            for method_name in compilation_errors:
                test_name = f"Test{method_name}"
                failed_tests.add(test_name)
        # Add other statuses if necessary, like XFAIL, etc.
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
