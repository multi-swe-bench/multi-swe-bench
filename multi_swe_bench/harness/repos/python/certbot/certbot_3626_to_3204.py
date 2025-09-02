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
apt-get update && apt-get install -y augeas-tools libaugeas-dev libssl-dev python3-dev gcc make
###ACTION_DELIMITER###
pip install -e .[dev]
###ACTION_DELIMITER###
pip install -e acme[dns,dev]
###ACTION_DELIMITER###
pip install -e .[dev]
###ACTION_DELIMITER###
pip install -e certbot-apache
###ACTION_DELIMITER###
pip install -e certbot-nginx
###ACTION_DELIMITER###
pip install -e letshelp-certbot
###ACTION_DELIMITER###
nosetests -v acme
###ACTION_DELIMITER###
tox -e cover
###ACTION_DELIMITER###
echo -e 'nosetests -v acme
nosetests -v certbot
nosetests -v certbot_apache
nosetests -v certbot_nginx
nosetests -v letshelp_certbot' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
nosetests -v acme
nosetests -v certbot
nosetests -v certbot_apache
nosetests -v certbot_nginx
nosetests -v letshelp_certbot

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
nosetests -v acme
nosetests -v certbot
nosetests -v certbot_apache
nosetests -v certbot_nginx
nosetests -v letshelp_certbot

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
nosetests -v acme
nosetests -v certbot
nosetests -v certbot_apache
nosetests -v certbot_nginx
nosetests -v letshelp_certbot

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim with actual base image
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
RUN git clone https://github.com/certbot/certbot.git /home/certbot

WORKDIR /home/certbot
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("certbot", "certbot_3626_to_3204")
class CERTBOT_3626_TO_3204(Instance):
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
        # import json  # Not needed for regex parsing
        # Implement the log parsing logic here
        # Regex patterns to match test cases and their statuses
        # Pattern for passed tests (ends with ... ok)
        passed_pattern = re.compile(r'^(?:\s*\[\s*\d+\s*\]\s*)?(test_[a-z_]+)\s*\(([^)]+)\)\s*\.\.\.\s*ok\s*$', re.MULTILINE)
        # Pattern for failed tests (starts with ERROR:)
        failed_pattern = re.compile(r'^(?:\s*\[\s*\d+\s*\]\s*)?ERROR:\s*(test_[a-z_]+)\s*\(([^)]+)\)\s*$', re.MULTILINE)
        # Pattern for skipped tests (ends with ... skipped)
        skipped_pattern = re.compile(r'^\s*\[\s*\d+\s*\]\s*(test_[a-z_]+)\s*\(([\w.]+)\)\s*\.\.\.\s*skipped\s*$', re.MULTILINE)
        # Extract test names and strip any surrounding whitespace
        passed_tests = set(f"{class_module}.{test_method}" for test_method, class_module in passed_pattern.findall(log))
        failed_tests = set(f"{class_module}.{test_method}" for test_method, class_module in failed_pattern.findall(log))
        skipped_tests = set(f"{class_module}.{test_method}" for test_method, class_module in skipped_pattern.findall(log))
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
