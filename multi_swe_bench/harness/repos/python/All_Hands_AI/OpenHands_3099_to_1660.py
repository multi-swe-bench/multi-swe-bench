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
        return "ubuntu:22.04"
    
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
                """poetry add tomli
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y curl python3
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH"
###ACTION_DELIMITER###
poetry install
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y
###ACTION_DELIMITER###
apt-get install -y python3.11 python3.11-venv python3.11-dev
###ACTION_DELIMITER###
poetry env use python3.11
###ACTION_DELIMITER###
poetry install
###ACTION_DELIMITER###
poetry env info
###ACTION_DELIMITER###
poetry run python --version
###ACTION_DELIMITER###
python3.11 --version
###ACTION_DELIMITER###
poetry env remove python3.11
###ACTION_DELIMITER###
poetry env use python3.11
###ACTION_DELIMITER###
/root/.cache/pypoetry/virtualenvs/opendevin-05yZB55T-py3.11/bin/python --version
###ACTION_DELIMITER###
which python3.11
###ACTION_DELIMITER###
poetry env use /usr/bin/python3.11
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 - --uninstall
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3.11 -
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH"
###ACTION_DELIMITER###
poetry env info
###ACTION_DELIMITER###
rm -rf /root/.cache/pypoetry/virtualenvs/opendevin-05yZB55T-py3.11
###ACTION_DELIMITER###
poetry env use /usr/bin/python3.11
###ACTION_DELIMITER###
/root/.cache/pypoetry/virtualenvs/opendevin-05yZB55T-py3.11/bin/python --version
###ACTION_DELIMITER###
python3.11 -m venv .venv && poetry env use .venv/bin/python
###ACTION_DELIMITER###
./.venv/bin/python --version
###ACTION_DELIMITER###
poetry install
###ACTION_DELIMITER###
poetry add tomli
###ACTION_DELIMITER###
cp config.template.toml config.toml
###ACTION_DELIMITER###
sed -i '/\[docker\]/a enabled = true' config.toml
###ACTION_DELIMITER###
echo -e 'export DOCKER_ENABLED=true
export PROJECT_ROOT="/home/OpenHands"
export SCRIPT_DIR="/home/OpenHands"
export WORKSPACE_BASE="/home/OpenHands/workspace"
poetry run pytest --verbose ./tests/' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i '/\[core\]/a runtime = "docker"' config.toml
###ACTION_DELIMITER###
sed -i '/\[docker\]/a socket_path = "/var/run/docker.sock"' config.toml
###ACTION_DELIMITER###
apt-get install -y docker.io && service docker start
###ACTION_DELIMITER###
systemctl start docker
###ACTION_DELIMITER###
dockerd &
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cat config.toml
###ACTION_DELIMITER###
echo -e '[docker]
enabled = true
socket_path = "/var/run/docker.sock"' >> config.toml
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i '1i export OPENDevin_RUNTIME=docker' test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
export OPENDevin_RUNTIME=docker
export DOCKER_ENABLED=true
export PROJECT_ROOT="/home/OpenHands"
export SCRIPT_DIR="/home/OpenHands"
export WORKSPACE_BASE="/home/OpenHands/workspace"
poetry run pytest --verbose ./tests/

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
export OPENDevin_RUNTIME=docker
export DOCKER_ENABLED=true
export PROJECT_ROOT="/home/OpenHands"
export SCRIPT_DIR="/home/OpenHands"
export WORKSPACE_BASE="/home/OpenHands/workspace"
poetry run pytest --verbose ./tests/

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
export OPENDevin_RUNTIME=docker
export DOCKER_ENABLED=true
export PROJECT_ROOT="/home/OpenHands"
export SCRIPT_DIR="/home/OpenHands"
export WORKSPACE_BASE="/home/OpenHands/workspace"
poetry run pytest --verbose ./tests/

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
FROM ubuntu:22.04

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
RUN git clone https://github.com/All-Hands-AI/OpenHands.git /home/OpenHands

WORKDIR /home/OpenHands
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("All-Hands-AI", "OpenHands_3099_to_1660")
class OPENHANDS_3099_TO_1660(Instance):
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
        passed_tests = set() # Tests that passed successfully
        failed_tests = set() # Tests that failed
        skipped_tests = set() # Tests that were skipped
        import re
        import json
        # Use regex to find test cases and their statuses
        pattern = r'(\btests/.*?::.*?) (PASSED|FAILED|SKIPPED|ERROR)\b'
        matches = re.findall(pattern, log)
        for test_name, status in matches:
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ('FAILED', 'ERROR'):
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
