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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
pip3 install tox
###ACTION_DELIMITER###
tox -e dbt021-py38 --devenv .venv
###ACTION_DELIMITER###
apt-get install -y python3-tox
###ACTION_DELIMITER###
pip3 install tox --break-system-packages
###ACTION_DELIMITER###
tox -e dbt021-py38 --devenv .venv
###ACTION_DELIMITER###
tox -e dbt150-py38 --devenv .venv
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.8
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.8
###ACTION_DELIMITER###
tox -e dbt150-py38 --devenv .venv
###ACTION_DELIMITER###
ls constraints/
###ACTION_DELIMITER###
ln -s dbt150.txt constraints/dbt150-py38.txt
###ACTION_DELIMITER###
tox -e dbt150-py38 --devenv .venv
###ACTION_DELIMITER###
apt-get install -y python3.8-distutils
###ACTION_DELIMITER###
tox -e dbt150-py38 --devenv .venv
###ACTION_DELIMITER###
sed -i 's/types-pkg_resources/types-setuptools/' requirements_dev.txt
###ACTION_DELIMITER###
tox -e dbt150-py38 --devenv .venv
###ACTION_DELIMITER###
echo -e '#!/bin/bash
.venv/bin/pytest -vv -rsfE test/' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
.venv/bin/pytest -vv -rsfE test/

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
.venv/bin/pytest -vv -rsfE test/

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
.venv/bin/pytest -vv -rsfE test/

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
RUN git clone https://github.com/sqlfluff/sqlfluff.git /home/sqlfluff

WORKDIR /home/sqlfluff
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("sqlfluff", "sqlfluff_5053_to_4813")
class SQLFLUFF_5053_TO_4813(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re
        # Regex patterns to match test cases and their statuses
        passed_pattern = re.compile(r'.*?(test/[^\s]+)\s+PASSED', re.IGNORECASE)
        failed_pattern = re.compile(r'.*?FAILED\s+(test/[^\s]+)\s+-', re.IGNORECASE)
        skipped_pattern1 = re.compile(r'.*?(test/[^\s]+)\s+SKIPPED', re.IGNORECASE)
        skipped_pattern2 = re.compile(r'^SKIPPED\s+(test/.*?)\s+-', re.IGNORECASE)
        for line in log.splitlines():
            line = line.strip()
            # Check for passed tests
            passed_match = passed_pattern.search(line)
            if passed_match:
                test_name = passed_match.group(1).strip()
                passed_tests.add(test_name)
            # Check for failed tests
            failed_match = failed_pattern.search(line)
            if failed_match:
                test_name = failed_match.group(1).strip()
                failed_tests.add(test_name)
            # Check for skipped tests
            skipped_match = skipped_pattern1.search(line) or skipped_pattern2.search(line)
            if skipped_match:
                test_name = skipped_match.group(1).strip()
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
