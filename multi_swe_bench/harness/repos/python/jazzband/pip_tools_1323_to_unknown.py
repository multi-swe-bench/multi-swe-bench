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
        return "python:3.9-slim"
    
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
                """pip --version
###ACTION_DELIMITER###
pip install -v -e ".[testing]"
###ACTION_DELIMITER###
python -c "import piptools.repositories; print('Import successful')"
###ACTION_DELIMITER###
cat /usr/local/lib/python3.9/site-packages/pip/_internal/cli/progress_bars.py | grep 'BAR_TYPES'
###ACTION_DELIMITER###
pip install --upgrade pip==22.3.1
###ACTION_DELIMITER###
python -c "import piptools.repositories; print('Import successful')"
###ACTION_DELIMITER###
cat /usr/local/lib/python3.9/site-packages/pip/_internal/cli/progress_bars.py | grep 'BAR_TYPES'
###ACTION_DELIMITER###
pip install --upgrade pip==20.1.0
###ACTION_DELIMITER###
python -c "import piptools.repositories; print('Import successful')"
###ACTION_DELIMITER###
echo 'pytest -v --strict --doctest-modules' > /home/pip-tools/test_commands.sh
###ACTION_DELIMITER###
cat /home/pip-tools/test_commands.sh
###ACTION_DELIMITER###
bash /home/pip-tools/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v --strict --doctest-modules

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
pytest -v --strict --doctest-modules

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
pytest -v --strict --doctest-modules

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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.9-slim

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
RUN git clone https://github.com/jazzband/pip-tools.git /home/pip-tools

WORKDIR /home/pip-tools
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("jazzband", "pip_tools_1323_to_unknown")
class PIP_TOOLS_1323_TO_UNKNOWN(Instance):
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
        test_status = {}  # Track latest status of each test
        import re
        # Regex pattern to match both "test (status)" and "(status) test" formats
        pattern = re.compile(r"(PASSED|FAILED|SKIPPED)\s+(tests/[^ ]+|piptools/[^ ]+)|(tests/[^ ]+|piptools/[^ ]+)\s+(PASSED|FAILED|SKIPPED)")
        for line in log.split('\n'):
            match = pattern.search(line)
            if match:
                if match.group(1) and match.group(2):
                    status = match.group(1).strip()
                    test_name = match.group(2).strip()
                else:
                    test_name = match.group(3).strip()
                    status = match.group(4).strip()
                test_status[test_name] = status  # Overwrite with latest status
        # Populate sets from the tracked statuses
        parsed_results = {
            "passed_tests": {t for t, s in test_status.items() if s == "PASSED"},
            "failed_tests": {t for t, s in test_status.items() if s == "FAILED"},
            "skipped_tests": {t for t, s in test_status.items() if s == "SKIPPED"}
        }
        

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
