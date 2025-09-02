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
ls tests
###ACTION_DELIMITER###
ls acme
###ACTION_DELIMITER###
cat tox.ini
###ACTION_DELIMITER###
find . -name 'test_*.py'
###ACTION_DELIMITER###
cat pytest.ini
###ACTION_DELIMITER###
echo 'pytest --verbose --no-header -rA --tb=no -p no:cacheprovider .' > /home/certbot/test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y augeas-lenses libaugeas0
###ACTION_DELIMITER###
python tools/pipstrap.py
###ACTION_DELIMITER###
python tools/install_and_test.py acme[test] certbot[test] certbot-dns-cloudflare certbot-dns-cloudxns certbot-dns-digitalocean certbot-dns-dnsimple certbot-dns-dnsmadeeasy certbot-dns-gehirn certbot-dns-google certbot-dns-linode certbot-dns-luadns certbot-dns-nsone certbot-dns-ovh certbot-dns-rfc2136 certbot-dns-route53 certbot-dns-sakuracloud certbot-nginx certbot-apache
###ACTION_DELIMITER###
bash /home/certbot/test_commands.sh
###ACTION_DELIMITER###
echo -e 'pytest --verbose --no-header -rA --tb=no -p no:cacheprovider acme/tests
pytest --verbose --no-header -rA --tb=no -p no:cacheprovider certbot/tests
pytest --verbose --no-header -rA --tb=no -p no:cacheprovider certbot-apache/tests
pytest --verbose --no-header -rA --tb=no -p no:cacheprovider certbot-nginx/tests' > /home/certbot/test_commands.sh
###ACTION_DELIMITER###
echo 'pytest --verbose --no-header -rA --tb=no -p no:cacheprovider -m "not integration" acme/tests certbot/tests certbot-apache/tests certbot-nginx/tests' > /home/certbot/test_commands.sh
###ACTION_DELIMITER###
bash /home/certbot/test_commands.sh
###ACTION_DELIMITER###
pip install -e 'acme[test]' -e 'certbot[test]' -e 'certbot-apache[test]' -e 'certbot-nginx[test]'
###ACTION_DELIMITER###
apt-get update && apt-get install -y apache2 nginx libapache2-mod-ssl && bash /home/certbot/test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y apache2 nginx && a2enmod ssl && bash /home/certbot/test_commands.sh
###ACTION_DELIMITER###
echo 'pytest --collect-only --verbose --no-header -rA --tb=no -p no:cacheprovider -m "not integration" acme/tests certbot/tests certbot-apache/tests certbot-nginx/tests' > /home/certbot/test_commands.sh && bash /home/certbot/test_commands.sh
###ACTION_DELIMITER###
pytest -v certbot/tests/client_test.py
###ACTION_DELIMITER###
echo 'tox' > /home/certbot/test_commands.sh && bash /home/certbot/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
tox

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
tox

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
tox

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


@Instance.register("certbot", "certbot_9359_to_8884")
class CERTBOT_9359_TO_8884(Instance):
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
        import json
        # Extract test names using regex patterns
        skipped_pattern = re.compile(r"SKIPPED:\s*(\S+):")
        failed_pattern = re.compile(r"ERROR:\s*(\S+):")
        passed_pattern = re.compile(r"(\S+):\s*commands succeeded")
        skipped_tests.update(skipped_pattern.findall(log))
        failed_tests.update(failed_pattern.findall(log))
        passed_tests.update(passed_pattern.findall(log))
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
