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
apt-get update && apt-get install -y gcc libssl-dev libbrotli-dev libzstd-dev
###ACTION_DELIMITER###
pip install -r tests/requirements.txt && pip install -e .
###ACTION_DELIMITER###
echo 'pytest -v --cov=scrapy --cov-report=xml --cov-report= --durations=10 docs scrapy tests --doctest-modules' > /home/scrapy/test_commands.sh
###ACTION_DELIMITER###
cat /home/scrapy/test_commands.sh
###ACTION_DELIMITER###
bash /home/scrapy/test_commands.sh
###ACTION_DELIMITER###
pip install cryptography==36.0.0 cssselect==0.9.1 h2==3.0 itemadapter==0.1.0 parsel==1.5.0 Protego==0.1.15 pyOpenSSL==21.0.0 queuelib==1.4.2 service_identity==18.1.0 'Twisted[http2]==18.9.0' w3lib==1.17.0 zope.interface==5.1.0 lxml==4.4.1
###ACTION_DELIMITER###
apt-get install -y libxml2-dev libxslt1-dev
###ACTION_DELIMITER###
pip install cryptography==36.0.0 cssselect==0.9.1 h2==3.0 itemadapter==0.1.0 parsel==1.5.0 Protego==0.1.15 pyOpenSSL==21.0.0 queuelib==1.4.2 service_identity==18.1.0 'Twisted[http2]==18.9.0' w3lib==1.17.0 zope.interface==5.1.0 lxml==4.4.1
###ACTION_DELIMITER###
apt-get install -y zlib1g-dev
###ACTION_DELIMITER###
pip install cryptography==36.0.0 cssselect==0.9.1 h2==3.0 itemadapter==0.1.0 parsel==1.5.0 Protego==0.1.15 pyOpenSSL==21.0.0 queuelib==1.4.2 service_identity==18.1.0 'Twisted[http2]==18.9.0' w3lib==1.17.0 zope.interface==5.1.0 lxml==4.4.1
###ACTION_DELIMITER###
bash /home/scrapy/test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --cov=scrapy --cov-report=xml --cov-report= --durations=10 docs scrapy tests --doctest-modules -k "not Windows"' > /home/scrapy/test_commands.sh
###ACTION_DELIMITER###
cat /home/scrapy/test_commands.sh
###ACTION_DELIMITER###
bash /home/scrapy/test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --cov=scrapy --cov-report=xml --cov-report= --durations=10 docs scrapy tests --doctest-modules -k "not Windows" --deselect docs/intro/tutorial.rst::line:254,column:1 --deselect docs/intro/tutorial.rst::line:350,column:1 --deselect docs/intro/tutorial.rst::line:412,column:1' > /home/scrapy/test_commands.sh
###ACTION_DELIMITER###
cat /home/scrapy/test_commands.sh
###ACTION_DELIMITER###
bash /home/scrapy/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v --cov=scrapy --cov-report=xml --cov-report= --durations=10 docs scrapy tests --doctest-modules -k "not Windows" --deselect docs/intro/tutorial.rst::line:254,column:1 --deselect docs/intro/tutorial.rst::line:350,column:1 --deselect docs/intro/tutorial.rst::line:412,column:1

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
pytest -v --cov=scrapy --cov-report=xml --cov-report= --durations=10 docs scrapy tests --doctest-modules -k "not Windows" --deselect docs/intro/tutorial.rst::line:254,column:1 --deselect docs/intro/tutorial.rst::line:350,column:1 --deselect docs/intro/tutorial.rst::line:412,column:1

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
pytest -v --cov=scrapy --cov-report=xml --cov-report= --durations=10 docs scrapy tests --doctest-modules -k "not Windows" --deselect docs/intro/tutorial.rst::line:254,column:1 --deselect docs/intro/tutorial.rst::line:350,column:1 --deselect docs/intro/tutorial.rst::line:412,column:1

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
RUN git clone https://github.com/scrapy/scrapy.git /home/scrapy

WORKDIR /home/scrapy
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("scrapy", "scrapy_6013_to_5691")
class SCRAPY_6013_TO_5691(Instance):
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
        # Split log into lines
        lines = log.split('\n')
        for line in lines:
            # Remove leading [number] and whitespace
            processed_line = re.sub(r'^\[\s*\d+\]\s*', '', line)
            # Check for PASSED
            passed_match = re.match(r'^(.*?)\s+PASSED\s+\[\s*\d+%\]', processed_line)
            if passed_match:
                test_name = passed_match.group(1).strip()
                passed_tests.add(test_name)
            # Check for SKIPPED
            skipped_match = re.match(r'^(.*?)\s+SKIPPED\s+\[\s*\d+%\]', processed_line)
            if skipped_match:
                test_name = skipped_match.group(1).strip()
                skipped_tests.add(test_name)
            # Check for FAILED
            failed_match = re.match(r'^FAILED\s+(.*?)\s+-', processed_line)
            if failed_match:
                test_name = failed_match.group(1).strip()
                failed_tests.add(test_name)
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
