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
        return "python:3.11-slim"
    
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
                """ls -la
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
echo 'pytest -v --doctest-modules --durations=10 --pyargs networkx' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
pip install -r requirements/optional.txt && pip install -r requirements/extras.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install 'numpy<2.0'
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install 'numpy==1.19.5'
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install 'numpy==1.23.5'
###ACTION_DELIMITER###
pip uninstall -y scipy contourpy pandas matplotlib && pip install 'scipy<=1.9.3' 'pandas<=1.5.3' 'matplotlib<=3.6.3' 'pyyaml>=5.1' 'lxml>=4.2.3'
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install 'numpy==1.21.6' 'scipy==1.7.3' 'pandas==1.3.5' 'matplotlib==3.5.3'
###ACTION_DELIMITER###
pip install 'numpy==1.24.4' 'scipy==1.10.1' 'pandas==1.5.3' 'matplotlib==3.6.3'
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install 'numpy==1.23.5'
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install 'numpy==1.22.4'
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install 'numpy==1.23.5'
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y matplotlib && pip install 'matplotlib==3.2.2'
###ACTION_DELIMITER###
apt-get update && apt-get install -y libfreetype6-dev
###ACTION_DELIMITER###
pip install 'matplotlib==3.2.2'
###ACTION_DELIMITER###
MPLLOCALFREETYPE=1 pip install 'matplotlib==3.2.2'
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v --doctest-modules --durations=10 --pyargs networkx

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
pytest -v --doctest-modules --durations=10 --pyargs networkx

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
pytest -v --doctest-modules --durations=10 --pyargs networkx

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

# Choose an appropriate base image based on the project's requirements - replace python:3.11-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.11-slim

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
RUN git clone https://github.com/networkx/networkx.git /home/networkx

WORKDIR /home/networkx
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("networkx", "networkx_3764_to_3639")
class NETWORKX_3764_TO_3639(Instance):
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
        # Compile regex patterns to match test statuses
        passed_pattern = re.compile(r'^(.*?)\s+PASSED\s+\[\s*\d+%\]$')
        skipped_pattern = re.compile(r'^(.*?)\s+SKIPPED\s+\[\s*\d+%\]$')
        failed_pattern = re.compile(r'^FAILED\s+(.*)$')
        error_pattern = re.compile(r'^ERROR\s+(.*)$')
        # Process each line to extract test names and statuses
        for line in log.split('\n'):
            line = line.strip()
            # Check for passed tests
            match = passed_pattern.match(line)
            if match:
                passed_tests.add(match.group(1).strip())
                continue
            # Check for skipped tests
            match = skipped_pattern.match(line)
            if match:
                skipped_tests.add(match.group(1).strip())
                continue
            # Check for failed tests
            match = failed_pattern.match(line)
            if match:
                failed_tests.add(match.group(1).strip())
                continue
            # Check for error tests (treated as failed)
            match = error_pattern.match(line)
            if match:
                failed_tests.add(match.group(1).strip())
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
