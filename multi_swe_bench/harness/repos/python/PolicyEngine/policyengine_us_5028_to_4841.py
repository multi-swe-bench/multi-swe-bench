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
make install
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.10 python3.10-dev python3.10-pip
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y -t bullseye-backports python3.10 python3.10-dev python3.10-pip
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.11 python3.11-dev python3.11-pip
###ACTION_DELIMITER###
sed -i '/bullseye-backports/d' /etc/apt/sources.list && apt-get update && apt-get install -y python3.11 python3.11-dev python3.11-pip
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.11 python3.11-dev && python3.11 -m ensurepip --upgrade
###ACTION_DELIMITER###
apt-get install -y python3.11-venv && python3.11 -m ensurepip --upgrade
###ACTION_DELIMITER###
apt-get install -y python3-pip
###ACTION_DELIMITER###
pip3.11 install -e .[dev]
###ACTION_DELIMITER###
python3.11 -m venv venv && source venv/bin/activate && pip install -e .[dev]
###ACTION_DELIMITER###
echo -e '#!/bin/bash
source venv/bin/activate
coverage run -a --branch -m policyengine_core.scripts.policyengine_command test policyengine_us/tests/policy/ -c policyengine_us
coverage xml -i
pytest -v policyengine_us/tests/ --maxfail=0' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install coverage
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
source venv/bin/activate
coverage run -a --branch -m policyengine_core.scripts.policyengine_command test policyengine_us/tests/policy/ -c policyengine_us
coverage xml -i
pytest -v policyengine_us/tests/ --maxfail=0

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
source venv/bin/activate
coverage run -a --branch -m policyengine_core.scripts.policyengine_command test policyengine_us/tests/policy/ -c policyengine_us
coverage xml -i
pytest -v policyengine_us/tests/ --maxfail=0

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
source venv/bin/activate
coverage run -a --branch -m policyengine_core.scripts.policyengine_command test policyengine_us/tests/policy/ -c policyengine_us
coverage xml -i
pytest -v policyengine_us/tests/ --maxfail=0

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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.9-slim

## Set noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Install basic requirements
# For example: RUN apt-get update && apt-get install -y git
# For example: RUN yum install -y git
# For example: RUN apk add --no-cache git
RUN apt-get update && apt-get install -y git libhdf5-dev

# Ensure bash is available
RUN if [ ! -f /bin/bash ]; then         if command -v apk >/dev/null 2>&1; then             apk add --no-cache bash;         elif command -v apt-get >/dev/null 2>&1; then             apt-get update && apt-get install -y bash;         elif command -v yum >/dev/null 2>&1; then             yum install -y bash;         else             exit 1;         fi     fi

WORKDIR /home/
COPY fix.patch /home/
COPY test.patch /home/
RUN git clone https://github.com/PolicyEngine/policyengine-us.git /home/policyengine-us

WORKDIR /home/policyengine-us
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("PolicyEngine", "policyengine_us_5028_to_4841")
class POLICYENGINE_US_5028_TO_4841(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re

        # Extract all test names (valid test entries only)
        test_name_pattern = re.compile(
            r"^(policyengine_us/tests/.*?(?:\.py|\.yaml)(?:::[\w\[\]-]+)?)\s+\S+",  # Capture test name followed by any status
            re.MULTILINE,
        )
        all_test_names = set(
            match.group(1) for match in test_name_pattern.finditer(log)
        )
        # Extract failed tests (Python tests with FAILED or summary line)
        failed_pattern = re.compile(
            r"^(policyengine_us/tests/[\w/-]+\.py(?:::[\w\[\]-]+)?)\s+FAILED|"  # Only Python tests
            r"^FAILED\s+(policyengine_us/tests/[\w/-]+(?:\.py|\.yaml)(?:::[\w\[\]-]+)?)",  # Summary line
            re.MULTILINE,
        )
        failed_tests = set()
        for match in failed_pattern.finditer(log):
            test_name = match.group(1) or match.group(2)
            if test_name:  # Ensure only valid test names are added
                failed_tests.add(test_name)
        # Extract skipped tests (Python tests with SKIPPED, YAML files with 's' in status)
        skipped_pattern = re.compile(
            r"^(policyengine_us/tests/.*?(?:\.py|\.yaml)(?:::[\w\[\]-]+)?)\s+SKIPPED|"  # Python tests (inclusive path)
            r"^(policyengine_us/tests/.*?\.yaml)\s+[\.sF]*s[\.sF]*",  # YAML tests with 's' in status sequence
            re.MULTILINE,
        )
        skipped_tests = set()
        for match in skipped_pattern.finditer(log):
            test_name = match.group(1) or match.group(2)
            if test_name:  # Ensure only valid test names are added
                skipped_tests.add(test_name)
        # Passed tests are all test names not in failed or skipped
        passed_tests = all_test_names - failed_tests - skipped_tests
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
