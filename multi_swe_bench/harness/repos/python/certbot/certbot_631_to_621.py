import re

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
        return "python:3.11-slim"
    
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
sed -i 's/python2-pythondialog/pythondialog/' setup.py
###ACTION_DELIMITER###
pip install -r requirements.txt -e acme -e .[testing] -e letsencrypt-apache -e letsencrypt-nginx
###ACTION_DELIMITER###
apt-get update && apt-get install -y gcc libaugeas-dev
###ACTION_DELIMITER###
pip install -r requirements.txt -e acme -e .[testing] -e letsencrypt-apache -e letsencrypt-nginx
###ACTION_DELIMITER###
python setup.py test -v
###ACTION_DELIMITER###
nosetests -v
###ACTION_DELIMITER###
python -m unittest discover -v
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2.7 python2.7-dev
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian buster main' > /etc/apt/sources.list.d/buster.list && echo 'deb http://deb.debian.org/debian-security buster/updates main' >> /etc/apt/sources.list.d/buster.list && apt-get update && apt-get install -y python2.7 python2.7-dev
###ACTION_DELIMITER###
sed -i 's/collections.Mapping/collections.abc.Mapping/g' acme/acme/jose/util.py && sed -i 's/collections.Hashable/collections.abc.Hashable/g' acme/acme/jose/util.py
###ACTION_DELIMITER###
python -m unittest discover -v
###ACTION_DELIMITER###
sed -i 's/collections.Hashable/collections.abc.Hashable/g' acme/acme/jose/jwa.py
###ACTION_DELIMITER###
python -m unittest discover -v
###ACTION_DELIMITER###
ls tests
###ACTION_DELIMITER###
ls tests/integration
###ACTION_DELIMITER###
ls letsencrypt/tests
###ACTION_DELIMITER###
python -m unittest discover -s letsencrypt/tests -p '*_test.py' -v
###ACTION_DELIMITER###
pip install zope.interface==4.7.1
###ACTION_DELIMITER###
sed -i 's/import zope.interface/import zope.interface\nfrom zope.interface import implementer/' letsencrypt/display/util.py && sed -i 's/    zope.interface.implements(interfaces.IDisplay)/@implementer(interfaces.IDisplay)/' letsencrypt/display/util.py
###ACTION_DELIMITER###
python -m unittest discover -s letsencrypt/tests -p '*_test.py' -v
###ACTION_DELIMITER###
sed -i '/zope.interface.implements(interfaces.IDisplay)/d' letsencrypt/display/util.py && sed -i '/class NcursesDisplay(object):/i @implementer(interfaces.IDisplay)' letsencrypt/display/util.py
###ACTION_DELIMITER###
python -m unittest discover -s letsencrypt/tests -p '*_test.py' -v
###ACTION_DELIMITER###
sed -i '/zope\.interface\.implements(interfaces\.IDisplay)/d' letsencrypt/display/util.py && sed -i 's/^class NcursesDisplay(object):/@implementer(interfaces.IDisplay)\nclass NcursesDisplay(object):/' letsencrypt/display/util.py
###ACTION_DELIMITER###
sed -i '/^class NcursesDisplay(object):/i @implementer(interfaces.IDisplay)' letsencrypt/display/util.py
###ACTION_DELIMITER###
sed -i 's/^class NcursesDisplay(object):/@implementer(interfaces.IDisplay)\nclass NcursesDisplay(object):/' letsencrypt/display/util.py
###ACTION_DELIMITER###
python -m unittest discover -s letsencrypt/tests -p '*_test.py' -v
###ACTION_DELIMITER###
sed -i '/^class NcursesDisplay(object):/i @implementer(interfaces.IDisplay)' letsencrypt/display/util.py
###ACTION_DELIMITER###
sed -i '/zope\.interface\.implements(interfaces\.IDisplay)/d' letsencrypt/display/util.py && sed -i '/import zope\.interface/a from zope.interface import implementer' letsencrypt/display/util.py && sed -i 's/^class NcursesDisplay(object):/@implementer(interfaces.IDisplay)\nclass NcursesDisplay(object):/' letsencrypt/display/util.py
###ACTION_DELIMITER###
sed -i '/^class NcursesDisplay(object):/i @implementer(interfaces.IDisplay)' letsencrypt/display/util.py && sed -i 's/^    zope.interface.implements(interfaces.IDisplay)//' letsencrypt/display/util.py
###ACTION_DELIMITER###
sed -i '/@implementer(interfaces.IDisplay)/d' letsencrypt/display/util.py && sed -i 's/^class NcursesDisplay(object):/@implementer(interfaces.IDisplay)\nclass NcursesDisplay(object):/' letsencrypt/display/util.py && sed -i 's/^    def __init__/    def __init__/' letsencrypt/display/util.py
###ACTION_DELIMITER###
sed -i '/^@implementer(interfaces.IDisplay)/d' letsencrypt/display/util.py && sed -i 's/^class NcursesDisplay(object):/@implementer(interfaces.IDisplay)\nclass NcursesDisplay(object):/' letsencrypt/display/util.py && sed -i 's/^  def __init__/    def __init__/' letsencrypt/display/util.py
###ACTION_DELIMITER###
sed -i '/^@implementer/d' letsencrypt/display/util.py && sed -i 's/^class NcursesDisplay(object):/@implementer(interfaces.IDisplay)\nclass NcursesDisplay(object):/' letsencrypt/display/util.py && sed -i 's/^  def __init__/    def __init__/' letsencrypt/display/util.py
###ACTION_DELIMITER###
sed -i '/@implementer/d' letsencrypt/display/util.py && sed -i 's/^class NcursesDisplay(object):/@implementer(interfaces.IDisplay)\nclass NcursesDisplay(object):/' letsencrypt/display/util.py && sed -i 's/^  def __init__/    def __init__/' letsencrypt/display/util.py
###ACTION_DELIMITER###
sed -i '/@implementer/d' letsencrypt/display/util.py && sed -i 's/^class NcursesDisplay(object):/@implementer(interfaces.IDisplay)\nclass NcursesDisplay(object):/' letsencrypt/display/util.py && sed -i 's/^  def __init__/    def __init__/' letsencrypt/display/util.py
###ACTION_DELIMITER###
python -m unittest discover -s letsencrypt/tests -p '*_test.py' -v
###ACTION_DELIMITER###
sed -i 's/collections.Hashable/collections.abc.Hashable/g' acme/acme/messages.py
###ACTION_DELIMITER###
python -m unittest discover -s letsencrypt/tests -p '*_test.py' -v
###ACTION_DELIMITER###
sed -i 's/"0400"/"0o400"/' letsencrypt/tests/account_test.py
###ACTION_DELIMITER###
sed -i 's/self.assertEqual(\[\], self.storage.find_all())/self.assertEqual([], list(self.storage.find_all()))/' letsencrypt/tests/account_test.py
###ACTION_DELIMITER###
sed -i 's/plugins.values()/list(plugins.values())/' letsencrypt/tests/display/ops_test.py
###ACTION_DELIMITER###
echo -e '#!/bin/bash
python -m unittest discover -s letsencrypt/tests -p '*_test.py' -v' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
python -m unittest discover -s letsencrypt/tests -p *_test.py -v

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
python -m unittest discover -s letsencrypt/tests -p *_test.py -v

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
python -m unittest discover -s letsencrypt/tests -p *_test.py -v

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

# Choose an appropriate base image based on the project's requirements - replace python:3.11-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.11-slim

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


@Instance.register("certbot", "certbot_631_to_621")
class CERTBOT_631_TO_621(Instance):
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
        # Parse test results using regex
        test_pattern = re.compile(r'\((.*?)\) \.\.\. (ok|ERROR|FAIL|SKIPPED)')
        for match in test_pattern.findall(log):
            test_name, status = match
            if status == 'ok':
                passed_tests.add(test_name)
            elif status in ('ERROR', 'FAIL'):
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
