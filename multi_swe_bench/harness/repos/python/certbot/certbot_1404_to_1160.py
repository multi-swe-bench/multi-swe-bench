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
                """ls -la
###ACTION_DELIMITER###
apt-get update && apt-get install -y libssl-dev libffi-dev
###ACTION_DELIMITER###
pip install -e acme[testing]
###ACTION_DELIMITER###
pip install -e .[testing]
###ACTION_DELIMITER###
pip install pythondialog
###ACTION_DELIMITER###
pip install -e .[testing]
###ACTION_DELIMITER###
sed -i 's/python2-pythondialog/pythondialog/' setup.py
###ACTION_DELIMITER###
pip install -e .[testing]
###ACTION_DELIMITER###
pip install -e letsencrypt-apache
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libaugeas0 libaugeas-dev
###ACTION_DELIMITER###
pip install -e letsencrypt-apache
###ACTION_DELIMITER###
pip install -e letsencrypt-nginx
###ACTION_DELIMITER###
nosetests -v acme
###ACTION_DELIMITER###
pip install cryptography==1.9 pyopenssl==16.2.0
###ACTION_DELIMITER###
pip install cryptography==2.8 pyopenssl==19.1.0
###ACTION_DELIMITER###
nosetests -v acme
###ACTION_DELIMITER###
pip install werkzeug==1.0.1
###ACTION_DELIMITER###
echo -e 'nosetests -v acme
nosetests -v letsencrypt
nosetests -v letsencrypt_apache
nosetests -v letsencrypt_nginx
nosetests -v letshelp_letsencrypt' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -e letshelp-letsencrypt
###ACTION_DELIMITER###
pip install zope.interface==4.7.0
###ACTION_DELIMITER###
pip install setuptools==41.6.0
###ACTION_DELIMITER###
pip install zope-event==4.5.0
###ACTION_DELIMITER###
pip install zope.interface==4.7.0
###ACTION_DELIMITER###
pip install zope-component==4.6.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i -e '34i @zope.interface.implementer(interfaces.IPlugin)' -e '36d' letsencrypt/plugins/common.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/import urlparse/from urllib.parse import urlparse/' letsencrypt/configuration.py
###ACTION_DELIMITER###

###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i 's/import urlparse/from urllib.parse import urlparse/' letsencrypt/configuration.py
###ACTION_DELIMITER###

###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i 's/print textwrap.fill(/print(textwrap.fill(/' letshelp-letsencrypt/apache.py
###ACTION_DELIMITER###
sed -i 's/print textwrap.fill(/print(textwrap.fill(/' letshelp-letsencrypt/letshelp_letsencrypt/apache.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from urllib.parse from urllib.parse import urlparse/from urllib.parse import urlparse/' letsencrypt/configuration.py
###ACTION_DELIMITER###
sed -i 's/from urllib.parse from urllib.parse import urlparse/from urllib.parse import urlparse/' letsencrypt/configuration.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i -e '34i @zope.interface.implementer(interfaces.IConfig)' -e '35d' letsencrypt/configuration.py
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
nosetests -v acme
nosetests -v letsencrypt
nosetests -v letsencrypt_apache
nosetests -v letsencrypt_nginx
nosetests -v letshelp_letsencrypt

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
nosetests -v letsencrypt
nosetests -v letsencrypt_apache
nosetests -v letsencrypt_nginx
nosetests -v letshelp_letsencrypt

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
nosetests -v letsencrypt
nosetests -v letsencrypt_apache
nosetests -v letsencrypt_nginx
nosetests -v letshelp_letsencrypt

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


@Instance.register("certbot", "certbot_1404_to_1160")
class CERTBOT_1404_TO_1160(Instance):
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
        import json
        # Parse passed tests: lines ending with "... ok"
        # Adjusted to ignore leading line numbers in brackets
        # Adjusted to match actual log format (no line numbers) and handle leading spaces
        passed_pattern = re.compile(r'^\s*(.+?)\s*\.\.\.\s*ok$', re.MULTILINE)
        passed_tests = set(test.strip() for test in passed_pattern.findall(log))
        # Parse failed tests: lines ending with ... FAILED or starting with ERROR:
        failed_result_pattern = re.compile(r'^(?:\[\s*\d+\s*\]\s*)?(.+?)\s*\.\.\.\s*FAILED$', re.MULTILINE)
        failed_error_pattern = re.compile(r'^(?:\[\s*\d+\s*\]\s*)?ERROR:\s*(.+)$', re.MULTILINE)
        failed_tests = set()
        # Combine results from both patterns
        for test in failed_result_pattern.findall(log) + failed_error_pattern.findall(log):
            cleaned_test = test.strip()
            if cleaned_test:
                failed_tests.add(cleaned_test)
        # TODO: Check for skipped tests if patterns are found in logs
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
