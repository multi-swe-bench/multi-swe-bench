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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.11 python3-pip python-is-python3
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository --yes ppa:deadsnakes/ppa
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.11 python3.11-pip python-is-python3
###ACTION_DELIMITER###
apt-get install -y python3.11 python3.11-distutils python-is-python3
###ACTION_DELIMITER###
python3.11 -m ensurepip
###ACTION_DELIMITER###
apt-get install -y python3.11-venv
###ACTION_DELIMITER###
python3.11 -m ensurepip
###ACTION_DELIMITER###
pip3.11 install -e .[dev]
###ACTION_DELIMITER###
echo 'tox -e tests' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
python --version
###ACTION_DELIMITER###
echo 'python3.11 -m pytest -v' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'python3.11 -m pytest -v --asyncio-mode=auto' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'python3.11 -m pytest -v tests/ src/ docs/ --asyncio-mode=auto' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'python3.11 -m pytest -v --no-header -rA --tb=no -p no:cacheprovider --asyncio-mode=auto --junitxml=test_results.xml tests/ src/ docs/' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
python3.11 -m pytest -v --no-header -rA --tb=no -p no:cacheprovider --asyncio-mode=auto --junitxml=test_results.xml tests/ src/ docs/

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
python3.11 -m pytest -v --no-header -rA --tb=no -p no:cacheprovider --asyncio-mode=auto --junitxml=test_results.xml tests/ src/ docs/

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
python3.11 -m pytest -v --no-header -rA --tb=no -p no:cacheprovider --asyncio-mode=auto --junitxml=test_results.xml tests/ src/ docs/

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
RUN git clone https://github.com/DiamondLightSource/dodal.git /home/dodal

WORKDIR /home/dodal
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("DiamondLightSource", "dodal_868_to_unknown")
class DODAL_868_TO_UNKNOWN(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        # Regex pattern to extract test names (tests/...::...)
        test_pattern = re.compile(r'tests/[^:]+::[^ ]+')
        # Regex pattern to extract statuses (PASSED, FAILED, SKIPPED, ERROR)
        status_pattern = re.compile(r'(PASSED|FAILED|SKIPPED|ERROR)')
        for line in log.split('\n'):
            test_match = test_pattern.search(line)
            if not test_match:
                continue  # Skip lines without test names
            test_name = test_match.group(0)
            status_match = status_pattern.search(line)
            if not status_match:
                continue  # Skip lines without a recognized status
            status = status_match.group(1)
            # Categorize the test based on status
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ('FAILED', 'ERROR'):
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
