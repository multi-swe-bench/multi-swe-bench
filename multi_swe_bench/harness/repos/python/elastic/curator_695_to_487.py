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
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
pip3 install -r requirements.txt
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
echo 'python setup.py test -- -v' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install setuptools
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
echo 'pytest -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install mock
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y openjdk-8-jdk
###ACTION_DELIMITER###
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
###ACTION_DELIMITER###
echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/7.x/apt stable main" | tee /etc/apt/sources.list.d/elasticsearch.list
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y elasticsearch
###ACTION_DELIMITER###
/usr/share/elasticsearch/bin/elasticsearch -d
###ACTION_DELIMITER###
su elasticsearch -c '/usr/share/elasticsearch/bin/elasticsearch -d'
###ACTION_DELIMITER###
ps aux | grep elasticsearch
###ACTION_DELIMITER###
cat /var/log/elasticsearch/elasticsearch.log
###ACTION_DELIMITER###
id elasticsearch
###ACTION_DELIMITER###
su -s /bin/bash elasticsearch -c '/usr/share/elasticsearch/bin/elasticsearch -d'
###ACTION_DELIMITER###
chown -R elasticsearch:elasticsearch /var/log/elasticsearch/ && chown -R elasticsearch:elasticsearch /var/lib/elasticsearch/
###ACTION_DELIMITER###
su -s /bin/bash elasticsearch -c '/usr/share/elasticsearch/bin/elasticsearch -d'
###ACTION_DELIMITER###
ps aux | grep elasticsearch
###ACTION_DELIMITER###
kill 5154
###ACTION_DELIMITER###
su -s /bin/bash elasticsearch -c '/usr/share/elasticsearch/bin/elasticsearch -d'
###ACTION_DELIMITER###
curl http://localhost:9200
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl http://localhost:9200
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pyyaml==5.4.1
###ACTION_DELIMITER###
pip install cython
###ACTION_DELIMITER###
pip install pyyaml==5.4.1
###ACTION_DELIMITER###
pip install cython==0.29.36
###ACTION_DELIMITER###
pip install pyyaml==5.4.1
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v

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
pytest -v

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
pytest -v

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
RUN git clone https://github.com/elastic/curator.git /home/curator

WORKDIR /home/curator
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("elastic", "curator_695_to_487")
class CURATOR_695_TO_487(Instance):
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
        # import json  # Not used in this implementation
        # Regex pattern to match test lines with status (PASSED, FAILED, SKIPPED)
        pattern = re.compile(r'(test/.*?) (PASSED|FAILED|SKIPPED)\s+\[')
        matches = pattern.findall(log)
        for test_name, status in matches:
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
        # Check if there are skipped tests mentioned in the summary but not captured
        summary_skipped_match = re.search(r'(\d+) skipped', log)
        if summary_skipped_match:
            expected_skipped = int(summary_skipped_match.group(1))
            if len(skipped_tests) < expected_skipped:
                # Look for additional skipped test patterns, e.g., "SKIPPED test/..."
                skipped_pattern = re.compile(r'SKIPPED (test/.*?)(?: \[|$)')
                additional_skipped = skipped_pattern.findall(log)
                for test in additional_skipped:
                    skipped_tests.add(test)
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
