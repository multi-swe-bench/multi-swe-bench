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
apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.10
###ACTION_DELIMITER###
pip install poetry --break-system-packages
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3-pip
###ACTION_DELIMITER###
pip3 install poetry --break-system-packages
###ACTION_DELIMITER###
poetry install -E test
###ACTION_DELIMITER###
echo 'poetry run pytest -v test/' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
poetry install -E test -E tools
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
poetry install -E rag
###ACTION_DELIMITER###
export OPENAI_API_KEY=dummy && bash test_commands.sh
###ACTION_DELIMITER###
poetry install -E key-value-storages -E object-storages"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
poetry run pytest -v test/

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
poetry run pytest -v test/

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
poetry run pytest -v test/

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
RUN git clone https://github.com/camel-ai/camel.git /home/camel

WORKDIR /home/camel
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("camel-ai", "camel_1038_to_unknown")
class CAMEL_1038_TO_UNKNOWN(Instance):
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
        import json
        lines = log.split('\n')
        # Define regex patterns to match test cases and their statuses
        # Combined pattern to match both formats: test_name STATUS or STATUS test_name
        # Pattern 1: [line_num] test/path.py::test_name STATUS [percent]
        # More flexible patterns to capture test names with brackets and special characters
        # Specific patterns to match test names with brackets and correct path structure
        # Simplified patterns to capture test names and statuses
        # Specific patterns with allowed characters for test names
        # More permissive patterns using search() instead of match()
        # Include line number prefix in patterns
        # Adjusted to better match status and percent section
        # Make percentage section optional to match more lines
        # Make bracket content optional and flexible
        # Use non-greedy match to capture test names with special characters like ::
        # Simplified to capture test names without spaces
        # Explicitly include :: in test names and expand character class
        # Include optional bracket content at the end
        # Include brackets and hyphens in test names
        # Simplified and permissive patterns to capture test names and statuses
        # Refined patterns to specifically match test names with ::
        # Simplified patterns with non-greedy matching for test names
        # Refined patterns to match test names with :: and percentage brackets
        # Simplified patterns with non-greedy matching for test names
        # Include '::' in test names to ensure correct capture
        # More specific patterns to match log line structure
        pattern1 = re.compile(r'(test/[^\s]+)\s+(\w+)(?:\s*\[\s*\d+%\s*\])?', re.IGNORECASE)  # Matches [line_num] test/path.py::test_name STATUS [percent]
        pattern2 = re.compile(r'(\w+)\s+(test/[^\s]+)', re.IGNORECASE)  # Matches [line_num] STATUS test/path.py::test_name
        for line in lines:
            line = line.strip()
            # Check for pattern1: test_name followed by status
            # Use search() to find matches anywhere in the line
            match1 = pattern1.search(line)
            if match1:
                test_name = match1.group(1)
                status = match1.group(2)
            else:
                # Check for pattern2: status followed by test_name
                match2 = pattern2.search(line)
                if match2:
                    status = match2.group(1)
                    test_name = match2.group(2)
                else:
                    continue  # Skip lines that don't match
            if not test_name or not status:
                continue
            # Normalize test name and status
            test_name = test_name.strip()
            status = status.strip().upper()
            # Categorize the test based on status
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ['FAILED', 'ERROR']:
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
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
