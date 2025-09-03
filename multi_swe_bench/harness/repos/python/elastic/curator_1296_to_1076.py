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
        repo_name= self.pr.repo
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
pip install -r requirements.txt
###ACTION_DELIMITER###
python setup.py test
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y openjdk-11-jre
###ACTION_DELIMITER###
apt-cache search openjdk
###ACTION_DELIMITER###
apt-get install -y openjdk-17-jre
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
###ACTION_DELIMITER###
apt-get install -y gnupg
###ACTION_DELIMITER###
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
###ACTION_DELIMITER###
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee /etc/apt/sources.list.d/elastic.list
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y elasticsearch
###ACTION_DELIMITER###
/usr/share/elasticsearch/bin/elasticsearch -d
###ACTION_DELIMITER###
su - elasticsearch -c "/usr/share/elasticsearch/bin/elasticsearch -d"
###ACTION_DELIMITER###
su elasticsearch -c "/usr/share/elasticsearch/bin/elasticsearch -d"
###ACTION_DELIMITER###
ps aux | grep elasticsearch
###ACTION_DELIMITER###
getent passwd elasticsearch
###ACTION_DELIMITER###
cat /var/log/elasticsearch/elasticsearch.log
###ACTION_DELIMITER###
mkdir -p /home/elasticsearch && chown elasticsearch:elasticsearch /home/elasticsearch && usermod -d /home/elasticsearch elasticsearch
###ACTION_DELIMITER###
su - elasticsearch -c "/usr/share/elasticsearch/bin/elasticsearch -d"
###ACTION_DELIMITER###
ps aux | grep elasticsearch
###ACTION_DELIMITER###
cat /var/log/elasticsearch/elasticsearch.log
###ACTION_DELIMITER###
chsh -s /bin/bash elasticsearch
###ACTION_DELIMITER###
su - elasticsearch -c "/usr/share/elasticsearch/bin/elasticsearch -d"
###ACTION_DELIMITER###
chown -R elasticsearch:elasticsearch /var/log/elasticsearch
###ACTION_DELIMITER###
su - elasticsearch -c "/usr/share/elasticsearch/bin/elasticsearch -d"
###ACTION_DELIMITER###
chown -R elasticsearch:elasticsearch /var/lib/elasticsearch
###ACTION_DELIMITER###
ps aux | grep elasticsearch
###ACTION_DELIMITER###
python setup.py test
###ACTION_DELIMITER###
echo 'python setup.py test -v' > /home/curator/test_commands.sh
###ACTION_DELIMITER###
cat /home/curator/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
python setup.py test -v

""".replace("[[REPO_NAME]]", repo_name)
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
if ! git -C /home/[[REPO_NAME]] apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
python setup.py test -v

""".replace("[[REPO_NAME]]", repo_name)
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
if ! git -C /home/[[REPO_NAME]] apply --whitespace=nowarn  /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
python setup.py test -v

""".replace("[[REPO_NAME]]", repo_name)
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
RUN git clone https://github.com/elastic/curator.git /home/curator

WORKDIR /home/curator
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("elastic", "curator_1296_to_1076")
class CURATOR_1296_TO_1076(Instance):
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
        # Extract all test names using regex
        all_tests_pattern = r'test_\w+ \(test\.[\w.]+\.\w+\)'
        all_tests = set(re.findall(all_tests_pattern, log))
        # Extract failed tests (FAIL and ERROR)
        failed_pattern = r'^(FAIL|ERROR): (test_\w+ \(test\.[\w.]+\.\w+\))'
        failed_matches = re.findall(failed_pattern, log, re.MULTILINE)
        failed_tests = set(match[1] for match in failed_matches)
        # Extract skipped tests
        skipped_pattern = r'(test_\w+ \(test\.[\w.]+\.\w+\)) \.\.\. SKIP:'
        skipped_tests = set(re.findall(skipped_pattern, log))
        # Calculate passed tests as all tests minus failed and skipped
        passed_tests = all_tests - failed_tests - skipped_tests
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
