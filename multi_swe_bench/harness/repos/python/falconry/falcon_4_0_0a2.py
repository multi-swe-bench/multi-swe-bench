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
        return "python:3.8-slim"
    
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
pip install -r requirements/tests.txt
###ACTION_DELIMITER###
ls -F requirements/
###ACTION_DELIMITER###
pip install -r requirements/tests
###ACTION_DELIMITER###
pytest tests/
###ACTION_DELIMITER###
pip install gunicorn
###ACTION_DELIMITER###
pytest tests/
###ACTION_DELIMITER###
pip install daphne
###ACTION_DELIMITER###
pytest tests/
###ACTION_DELIMITER###
ls -F tests/
###ACTION_DELIMITER###
pytest tests/asgi/
###ACTION_DELIMITER###
pytest tests/test_hello.py
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pytest tests/test_hello.py
###ACTION_DELIMITER###
pytest tests/ --ignore=tests/asgi/
###ACTION_DELIMITER###
echo "pytest tests/ --ignore=tests/asgi/" > test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest tests/ --ignore=tests/asgi/

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
pytest tests/ --ignore=tests/asgi/

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
pytest tests/ --ignore=tests/asgi/

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
FROM python:3.8-slim

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


@Instance.register("falconry", "falcon_4_0_0a2")
class FALCON_4_0_0A2(Instance):
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

        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re
        # Match lines like: tests/test_wsgiref_inputwrapper_with_size.py .           [100%]
        progress_pattern = re.compile(r'^(tests/test_.*\.py)\s+([.sFE]+)')
        # Match lines like: FAILED tests/test_mediatypes.py::test_invalid_media_range[text/plain; q=high]
        failed_summary_pattern = re.compile(r'^FAILED (.*?.py::.+?)(?: -|$)')
        files_with_dots = set()
        files_with_s = set()
        files_with_fe = set() # Files with F or E in progress
        for line in log.splitlines():
            match = progress_pattern.match(line)
            if match:
                test_file, statuses = match.groups()
                if '.' in statuses:
                    files_with_dots.add(test_file)
                if 's' in statuses:
                    files_with_s.add(test_file)
                if 'F' in statuses or 'E' in statuses:
                    files_with_fe.add(test_file)
        for line in log.splitlines():
            match = failed_summary_pattern.search(line)
            if match:
                full_test_name = match.group(1)
                if full_test_name:
                    failed_tests.add(full_test_name.strip())
        failed_files = {name.split('::')[0] for name in failed_tests}
        failed_files.update(files_with_fe)
        passed_tests.update(files_with_dots - failed_files - files_with_s)
        skipped_tests.update(files_with_s - failed_files)
        parsed_results = {
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'skipped_tests': skipped_tests,
        }

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
