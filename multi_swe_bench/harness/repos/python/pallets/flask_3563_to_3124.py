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
pip install pytest greenlet blinker python-dotenv Werkzeug==0.15.5 Jinja2==2.10 itsdangerous==0.24 Click==5.1
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
echo "pytest --no-header -rA --tb=no -p no:cacheprovider" > /home/flask/test_commands.sh
###ACTION_DELIMITER###
bash /home/flask/test_commands.sh
###ACTION_DELIMITER###
pip install Jinja2==2.10.1
###ACTION_DELIMITER###
bash /home/flask/test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y Jinja2 && pip install Jinja2==3.0.0
###ACTION_DELIMITER###
bash /home/flask/test_commands.sh
###ACTION_DELIMITER###
pip install Werkzeug==0.15.5 MarkupSafe==2.0.1
###ACTION_DELIMITER###
pip install --force-reinstall Werkzeug==0.15.5 Jinja2==2.11.3 itsdangerous==0.24 Click==5.1 pytest greenlet blinker python-dotenv MarkupSafe==2.0.1
###ACTION_DELIMITER###
bash /home/flask/test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y pytest && pip install pytest==6.2.5
###ACTION_DELIMITER###
bash /home/flask/test_commands.sh
###ACTION_DELIMITER###
pip install pluggy==0.13.1
###ACTION_DELIMITER###
bash /home/flask/test_commands.sh
###ACTION_DELIMITER###
pip install --force-reinstall Werkzeug==0.15.5 Jinja2==2.11.3 itsdangerous==0.24 Click==5.1 pytest==6.2.5 greenlet blinker python-dotenv MarkupSafe==2.0.1 pluggy==0.13.1
###ACTION_DELIMITER###

###ACTION_DELIMITER###
bash /home/flask/test_commands.sh --forked"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest --no-header -rA --tb=no -p no:cacheprovider

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
pytest --no-header -rA --tb=no -p no:cacheprovider

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
pytest --no-header -rA --tb=no -p no:cacheprovider

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
RUN git clone https://github.com/pallets/flask.git /home/flask

WORKDIR /home/flask
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pallets", "flask_3563_to_3124")
class FLASK_3563_TO_3124(Instance):
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
        for line in log.splitlines():
            if line.startswith("PASSED"):
                match = re.search(r"PASSED\s+(.*?)$", line)
                if match:
                    passed_tests.add(match.group(1).strip())
            elif line.startswith("FAILED"):
                match = re.search(r"FAILED\s+(.*?)\s+-", line)
                if match:
                    failed_tests.add(match.group(1).strip())
            elif line.startswith("XPASS"):
                match = re.search(r"XPASS\s+(.*?)\s+weird", line)
                if match:
                    skipped_tests.add(match.group(1).strip())
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
