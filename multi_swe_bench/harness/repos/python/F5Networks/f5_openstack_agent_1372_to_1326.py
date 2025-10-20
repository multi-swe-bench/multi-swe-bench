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
                """ls -la
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python2.7 python-pip libssl-dev libffi-dev
###ACTION_DELIMITER###
apt-get install -y debian-archive-keyring
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye main' > /etc/apt/sources.list.d/bullseye.list
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python2.7
###ACTION_DELIMITER###
apt-get install -y python-pip
###ACTION_DELIMITER###
curl -O https://bootstrap.pypa.io/pip/2.7/get-pip.py && python2.7 get-pip.py
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl -O https://bootstrap.pypa.io/pip/2.7/get-pip.py && python2.7 get-pip.py
###ACTION_DELIMITER###
apt-get install -y libssl-dev libffi-dev
###ACTION_DELIMITER###
pip2.7 install -r requirements.unittest.txt
###ACTION_DELIMITER###
pip2.7 install setuptools==44.1.1
###ACTION_DELIMITER###
sed -i 's/cryptography>=1.2.3/cryptography<=2.8/' requirements.unittest.txt
###ACTION_DELIMITER###
pip2.7 install -r requirements.unittest.txt
###ACTION_DELIMITER###
pip2.7 install --no-build-isolation -r requirements.unittest.txt
###ACTION_DELIMITER###
echo 'pika==1.0.1' >> requirements.unittest.txt
###ACTION_DELIMITER###
pip2.7 install --no-build-isolation -r requirements.unittest.txt
###ACTION_DELIMITER###
apt-get install -y build-essential
###ACTION_DELIMITER###
pip2.7 install --no-build-isolation -r requirements.unittest.txt
###ACTION_DELIMITER###
apt-get install -y python2.7-dev
###ACTION_DELIMITER###
echo 'yappi==1.0.0' >> requirements.unittest.txt && pip2.7 install --no-build-isolation -r requirements.unittest.txt
###ACTION_DELIMITER###
echo 'pytest -v f5_openstack_agent/tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls -la f5_openstack_agent
###ACTION_DELIMITER###
echo 'pytest -v test/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'pytest -v \
    --ignore f5_openstack_agent/tests/functional \
    --ignore f5_openstack_agent/lbaasv2/drivers/bigip/test/test_agent_manager.py \
    --ignore f5_openstack_agent/lbaasv2/drivers/bigip/test/test_agent_manager_LbaasAgentManager.py \
    --ignore f5_openstack_agent/lbaasv2/drivers/bigip/test/test_plugin_rpc.py \
    --ignore f5_openstack_agent/lbaasv2/drivers/bigip/test/test_icontrol_driver.py \
    f5_openstack_agent' > test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v \
    --ignore f5_openstack_agent/tests/functional \
    --ignore f5_openstack_agent/lbaasv2/drivers/bigip/test/test_agent_manager.py \
    --ignore f5_openstack_agent/lbaasv2/drivers/bigip/test/test_agent_manager_LbaasAgentManager.py \
    --ignore f5_openstack_agent/lbaasv2/drivers/bigip/test/test_plugin_rpc.py \
    --ignore f5_openstack_agent/lbaasv2/drivers/bigip/test/test_icontrol_driver.py \
    f5_openstack_agent

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
pytest -v \
    --ignore f5_openstack_agent/tests/functional \
    --ignore f5_openstack_agent/lbaasv2/drivers/bigip/test/test_agent_manager.py \
    --ignore f5_openstack_agent/lbaasv2/drivers/bigip/test/test_agent_manager_LbaasAgentManager.py \
    --ignore f5_openstack_agent/lbaasv2/drivers/bigip/test/test_plugin_rpc.py \
    --ignore f5_openstack_agent/lbaasv2/drivers/bigip/test/test_icontrol_driver.py \
    f5_openstack_agent

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
pytest -v \
    --ignore f5_openstack_agent/tests/functional \
    --ignore f5_openstack_agent/lbaasv2/drivers/bigip/test/test_agent_manager.py \
    --ignore f5_openstack_agent/lbaasv2/drivers/bigip/test/test_agent_manager_LbaasAgentManager.py \
    --ignore f5_openstack_agent/lbaasv2/drivers/bigip/test/test_plugin_rpc.py \
    --ignore f5_openstack_agent/lbaasv2/drivers/bigip/test/test_icontrol_driver.py \
    f5_openstack_agent

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
RUN git clone https://github.com/F5Networks/f5-openstack-agent.git /home/f5-openstack-agent

WORKDIR /home/f5-openstack-agent
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("F5Networks", "f5_openstack_agent_1372_to_1326")
class F5_OPENSTACK_AGENT_1372_TO_1326(Instance):
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
            # Regex pattern to match test lines with status
        pattern = re.compile(r'^(.*?)\s+(PASSED|FAILED|SKIPPED)$', re.MULTILINE)
        matches = pattern.findall(log)
        for test_name, status in matches:
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
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
