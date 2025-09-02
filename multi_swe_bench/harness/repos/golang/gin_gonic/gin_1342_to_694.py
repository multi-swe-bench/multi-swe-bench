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
                """ls -F
###ACTION_DELIMITER###
make deps
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y make
###ACTION_DELIMITER###

###ACTION_DELIMITER###
make deps
###ACTION_DELIMITER###
apt-get install -y golang
###ACTION_DELIMITER###
make deps
###ACTION_DELIMITER###
go mod init github.com/gin-gonic/gin
###ACTION_DELIMITER###
make deps
###ACTION_DELIMITER###
apt-get remove -y golang
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget https://go.dev/dl/go1.18.1.linux-amd64.tar.gz
###ACTION_DELIMITER###
tar -C /usr/local -xzf go1.18.1.linux-amd64.tar.gz
###ACTION_DELIMITER###
export PATH=$PATH:/usr/local/go/bin
###ACTION_DELIMITER###
make deps
###ACTION_DELIMITER###
/usr/local/go/bin/go get -u github.com/kardianos/govendor
###ACTION_DELIMITER###
echo "module github.com/gin-gonic/gin

go 1.18" > go.mod
###ACTION_DELIMITER###
PATH=$PATH:/usr/local/go/bin make deps
###ACTION_DELIMITER###
PATH=$PATH:/usr/local/go/bin go test -v -count=1 ./...
###ACTION_DELIMITER###
PATH=$PATH:/usr/local/go/bin go mod vendor
###ACTION_DELIMITER###
PATH=$PATH:/usr/local/go/bin go mod tidy
###ACTION_DELIMITER###

###ACTION_DELIMITER###
PATH=$PATH:/usr/local/go/bin go test -v -count=1 ./...
###ACTION_DELIMITER###
PATH=$PATH:/usr/local/go/bin go mod vendor
###ACTION_DELIMITER###
PATH=$PATH:/usr/local/go/bin go test -v -count=1 ./...
###ACTION_DELIMITER###

###ACTION_DELIMITER###
echo 'go test -v -count=1 ./...' > test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
go test -v -count=1 ./...

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
go test -v -count=1 ./...

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn  /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
go test -v -count=1 ./...

""".format(
                    pr=self.pr
                ),
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
RUN git clone https://github.com/gin-gonic/gin.git /home/gin

WORKDIR /home/gin
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("gin-gonic", "gin_1342_to_694")
class GIN_1342_TO_694(Instance):
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
        passed_tests = set() 
        failed_tests = set() 
        skipped_tests = set() 
        import re
        #τζ What's causing the problem?
        # The current implementation of the `parse_log` function is incomplete and does not extract test results from the log content.
        # The function initializes empty sets for `passed_tests`, `failed_tests`, and `skipped_tests` but does not populate them with actual data from the logs.
        # As a result, the script will always return empty results, regardless of the log file's content.
        # To fix this, I will add regular expressions to identify and extract the names of passed, failed, and skipped tests from the log file.
        #
        # How does this fix it?
        # I will introduce three regular expressions to find passed, failed, and skipped tests in the log data.
        # - `passed_pattern`: This pattern searches for lines starting with "--- PASS:" and extracts the test name that follows.
        # - `failed_pattern`: This pattern finds lines beginning with "--- FAIL:" and captures the associated test name.
        # - `skipped_pattern`: This pattern looks for lines with "--- SKIP:" and extracts the skipped test's name.
        # By using `re.findall()`, the code will gather all test names matching these patterns and populate the corresponding sets.
        # This ensures that the function correctly parses the log and returns accurate test results, which resolves the issue of the function returning empty sets.
        # The updated implementation will not break existing functionality, as it only adds the necessary logic to the empty function without altering its intended behavior.
        passed_pattern = re.compile(r"--- PASS: (\w+)")
        failed_pattern = re.compile(r"--- FAIL: (\w+)")
        skipped_pattern = re.compile(r"--- SKIP: (\w+)")
        passed_tests.update(passed_pattern.findall(log))
        failed_tests.update(failed_pattern.findall(log))
        skipped_tests.update(skipped_pattern.findall(log))
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
