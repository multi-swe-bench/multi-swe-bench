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
        return "python:3.7-slim"
    
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
ls -F requirements/
###ACTION_DELIMITER###
pip install -r requirements/tests
###ACTION_DELIMITER###
apt-get update && apt-get install -y gcc
###ACTION_DELIMITER###
pip install -r requirements/tests
###ACTION_DELIMITER###
apt-get install -y g++
###ACTION_DELIMITER###
pip install -r requirements/tests
###ACTION_DELIMITER###

###ACTION_DELIMITER###
echo 'pytest --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install gunicorn
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest tests --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
echo 'pytest --ignore=examples --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest --ignore=examples --ignore=falcon/bench --ignore=tests/test_deps.py --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest --ignore=examples --ignore=falcon/bench --ignore=tests/test_deps.py --ignore=tests/asgi' > test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'export FALCON_ASGI_WRAP_NON_COROUTINES=Y; export FALCON_TESTING_SESSION=Y; pytest --ignore=examples --ignore=falcon/bench --ignore=tests/test_deps.py --ignore=tests/asgi --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
export FALCON_ASGI_WRAP_NON_COROUTINES=Y; export FALCON_TESTING_SESSION=Y; pytest --ignore=examples --ignore=falcon/bench --ignore=tests/test_deps.py --ignore=tests/asgi --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
echo 'export FALCON_ASGI_WRAP_NON_COROUTINES=Y; export FALCON_TESTING_SESSION=Y; pytest --ignore=examples --ignore=falcon/bench --ignore=tests/test_deps.py --ignore=tests/asgi --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
export FALCON_ASGI_WRAP_NON_COROUTINES=Y; export FALCON_TESTING_SESSION=Y; pytest --ignore=examples --ignore=falcon/bench --ignore=tests/test_deps.py --ignore=tests/asgi --no-header -rA --tb=no -p no:cacheprovider

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
export FALCON_ASGI_WRAP_NON_COROUTINES=Y; export FALCON_TESTING_SESSION=Y; pytest --ignore=examples --ignore=falcon/bench --ignore=tests/test_deps.py --ignore=tests/asgi --no-header -rA --tb=no -p no:cacheprovider

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
export FALCON_ASGI_WRAP_NON_COROUTINES=Y; export FALCON_TESTING_SESSION=Y; pytest --ignore=examples --ignore=falcon/bench --ignore=tests/test_deps.py --ignore=tests/asgi --no-header -rA --tb=no -p no:cacheprovider

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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.7-slim

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
RUN git clone https://github.com/falconry/falcon.git /home/falcon

WORKDIR /home/falcon
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("falconry", "falcon_3_0_0a2")
class FALCON_3_0_0A2(Instance):
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
        import json
        test_pattern = re.compile(r'^(tests\/test_.*?\.py)(?:::[^\s]+)?\s+([\.sF]+)')
        error_pattern = re.compile(r'^ERROR (.*)')
        for line in log.splitlines():
            match = test_pattern.match(line)
            if match:
                test_file = match.group(1)
                statuses = match.group(2)
                # This is a simplification, assuming one status character per test
                # A more robust solution would handle multiple tests on one line from the file name.
                # However, the logs only show one test file per line.
                test_name = test_file
                if 'F' in statuses:
                    failed_tests.add(test_name)
                elif 's' in statuses:
                    skipped_tests.add(test_name)
                elif '.' in statuses:
                    passed_tests.add(test_name)
            match = error_pattern.match(line)
            if match:
                failed_tests.add(match.group(1))
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
