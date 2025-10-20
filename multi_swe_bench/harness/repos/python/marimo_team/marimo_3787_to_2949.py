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
        return "python:3.13-slim"
    
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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y --no-install-recommends libnss3 libatk-bridge2.0-0 libcups2 libxkbcommon0 libatspi2.0-0 libx11-6 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
###ACTION_DELIMITER###
apt-get install nodejs -y
###ACTION_DELIMITER###
pip install hatch
###ACTION_DELIMITER###
npm install -g pnpm
###ACTION_DELIMITER###
cd frontend && pnpm install
###ACTION_DELIMITER###
make fe
###ACTION_DELIMITER###
apt-get install -y make
###ACTION_DELIMITER###
cd .. && make fe
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
hatch run test:test -v
hatch run test-optional:test -v
make e2e VERBOSE=1' > /home/marimo/test_commands.sh && chmod +x /home/marimo/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e
hatch run test:test -v
hatch run test-optional:test -v
make e2e VERBOSE=1

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
set -e
hatch run test:test -v
hatch run test-optional:test -v
make e2e VERBOSE=1

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
set -e
hatch run test:test -v
hatch run test-optional:test -v
make e2e VERBOSE=1

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

# Choose an appropriate base image based on the project's requirements - replace python:3.13-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.13-slim

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
RUN git clone https://github.com/marimo-team/marimo.git /home/marimo

WORKDIR /home/marimo
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("marimo-team", "marimo_3787_to_2949")
class MARIMO_3787_TO_2949(Instance):
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
        # Regex patterns to match test names and statuses
        passed_pattern = re.compile(r"tests/[\w/.-]+\.py::[\w:[\]]+ PASSED")
        skipped_pattern = re.compile(r"tests/[\w/.-]+\.py::[\w:[\]]+ SKIPPED")
        failed_pattern = re.compile(r"FAILED tests/[\w/.-]+\.py::[\w:[\]]+")
        for line in log.splitlines():
            # Check for passed tests
            passed_match = passed_pattern.search(line)
            if passed_match:
                test_name = passed_match.group().rsplit(" PASSED", 1)[0]
                passed_tests.add(test_name)
            # Check for skipped tests
            skipped_match = skipped_pattern.search(line)
            if skipped_match:
                test_name = skipped_match.group().rsplit(" SKIPPED", 1)[0]
                skipped_tests.add(test_name)
            # Check for failed tests
            failed_match = failed_pattern.search(line)
            if failed_match:
                test_name = failed_match.group().split("FAILED ", 1)[1]
                failed_tests.add(test_name)
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
