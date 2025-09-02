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
                """ls -l /home/pyccel
###ACTION_DELIMITER###
apt-get update && apt-get install -y gcc gfortran libblas-dev liblapack-dev libopenmpi-dev openmpi-bin libomp-dev libomp5
###ACTION_DELIMITER###
pip install -e ".[test]"
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
pip3 install -e ".[test]"
###ACTION_DELIMITER###
python3 -m venv /home/pyccel/venv
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv /home/pyccel/venv
###ACTION_DELIMITER###
source /home/pyccel/venv/bin/activate && pip install -e ".[test]"
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nsource venv/bin/activate\npytest -v --tb=short ./tests' > /home/pyccel/test_commands.sh && chmod +x /home/pyccel/test_commands.sh
###ACTION_DELIMITER###
bash /home/pyccel/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nsource venv/bin/activate\npytest -v -n auto --tb=short ./tests' > /home/pyccel/test_commands.sh && chmod +x /home/pyccel/test_commands.sh
###ACTION_DELIMITER###
bash /home/pyccel/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nsource venv/bin/activate\npytest -v -n 4 --tb=short ./tests' > /home/pyccel/test_commands.sh && chmod +x /home/pyccel/test_commands.sh
###ACTION_DELIMITER###
bash /home/pyccel/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
source venv/bin/activate
pytest -v -n 4 --tb=short ./tests

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
#!/bin/bash
source venv/bin/activate
pytest -v -n 4 --tb=short ./tests

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
#!/bin/bash
source venv/bin/activate
pytest -v -n 4 --tb=short ./tests

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
RUN git clone https://github.com/pyccel/pyccel.git /home/pyccel

WORKDIR /home/pyccel
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pyccel", "pyccel_1797_to_unknown")
class PYCCEL_1797_TO_UNKNOWN(Instance):
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
        passed_tests: set[str] = set() # Tests that passed successfully
        failed_tests: set[str] = set() # Tests that failed
        skipped_tests: set[str] = set() # Tests that were skipped
        import re
        # Track the last test file path from error lines
        last_test_file = None
        # Pattern to match test lines with status (PASSED/SKIPPED/FAILED)
        test_pattern = re.compile(r'^(?:\[\s*\d+\s*\]\s*)?(tests/.+?)\s+(PASSED|SKIPPED|FAILED)(?:\s+\[\s*\d+%?\s*\])?$')
        # Pattern to match error lines and extract test file path
        error_file_pattern = re.compile(r'^(?:\[\s*\d+\s*\]\s*)(tests/.+?)\.py:\d+: .+')
        # Pattern to match failed test separator lines and extract function name
        failed_func_pattern = re.compile(r'^(?:\[\s*\d+\s*\]\s*)?____________________________ (test_.+?) ____________________________')
        for line in log.splitlines():
            # Capture passed/skipped/failed tests from standard lines
            test_match = test_pattern.search(line)
            if test_match:
                test_name = test_match.group(1)
                status = test_match.group(2)
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
            # Capture test file path from error lines
            error_file_match = error_file_pattern.search(line)
            if error_file_match:
                last_test_file = error_file_match.group(1) + '.py'
            # Capture failed test function name from separator lines and combine with file path
            failed_func_match = failed_func_pattern.search(line)
            if failed_func_match and last_test_file:
                test_func = failed_func_match.group(1)
                full_test_name = f'{last_test_file}::{test_func}'
                failed_tests.add(full_test_name)
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
