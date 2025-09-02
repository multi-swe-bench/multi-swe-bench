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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y netcat
###ACTION_DELIMITER###
apt-get install -y python3.11
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
###ACTION_DELIMITER###
apt-get install -y nodejs
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH"
###ACTION_DELIMITER###
apt-get install -y make
###ACTION_DELIMITER###
make build
###ACTION_DELIMITER###
apt-get install -y apt-transport-https ca-certificates curl software-properties-common
###ACTION_DELIMITER###
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
###ACTION_DELIMITER###
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
###ACTION_DELIMITER###
service docker start
###ACTION_DELIMITER###
service docker status
###ACTION_DELIMITER###
journalctl -u docker
###ACTION_DELIMITER###
service docker start
###ACTION_DELIMITER###
sed -n '62p' /etc/init.d/docker
###ACTION_DELIMITER###
ulimit -Hn
###ACTION_DELIMITER###
dockerd
###ACTION_DELIMITER###
update-alternatives --set iptables /usr/sbin/iptables-legacy && update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy
###ACTION_DELIMITER###
service docker start
###ACTION_DELIMITER###
sed -i '62s/^/#/' /etc/init.d/docker
###ACTION_DELIMITER###
service docker start
###ACTION_DELIMITER###
make build
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH" && poetry --version
###ACTION_DELIMITER###
PATH="/root/.local/bin:$PATH" make build
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 - --version 1.8.0
###ACTION_DELIMITER###
PATH="/root/.local/bin:$PATH" make build
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
poetry run pytest --verbose --no-header -rA --tb=no -p no:cacheprovider ./tests/unit/
poetry run pytest --verbose --no-header -rA --tb=no -p no:cacheprovider ./tests/integration/' > /home/OpenHands/test_commands.sh
###ACTION_DELIMITER###
chmod +x /home/OpenHands/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
set -e
poetry run pytest --verbose --no-header -rA --tb=no -p no:cacheprovider ./tests/unit/
poetry run pytest --verbose --no-header -rA --tb=no -p no:cacheprovider ./tests/integration/

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
set -e
poetry run pytest --verbose --no-header -rA --tb=no -p no:cacheprovider ./tests/unit/
poetry run pytest --verbose --no-header -rA --tb=no -p no:cacheprovider ./tests/integration/

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
set -e
poetry run pytest --verbose --no-header -rA --tb=no -p no:cacheprovider ./tests/unit/
poetry run pytest --verbose --no-header -rA --tb=no -p no:cacheprovider ./tests/integration/

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:22.04 with actual base image
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


@Instance.register("All-Hands-AI", "OpenHands_3665_to_3448")
class OPENHANDS_3665_TO_3448(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        import json
        lines = log.split('\n')
        for line in lines:
            line = line.strip()
            # Process PASSED tests
            if 'PASSED' in line:
                # Case 1: Test name followed by PASSED
                if 'tests/' in line:
                    parts = line.split('PASSED')
                    test_part_before = parts[0].strip()
                    if test_part_before.startswith('tests/'):
                        passed_tests.add(test_part_before)
                    if len(parts) > 1:
                        test_part_after = parts[1].strip()
                        if test_part_after.startswith('tests/'):
                            test_name = test_part_after.split()[0]
                            passed_tests.add(test_name)
            # Process FAILED tests
            elif 'FAILED' in line:
                if 'tests/' in line:
                    parts = line.split('FAILED')
                    if len(parts) > 1:
                        test_part = parts[1].strip()
                        test_name = test_part.split(' - ')[0] if ' - ' in test_part else test_part
                        if test_name.startswith('tests/'):
                            failed_tests.add(test_name)
            # Process SKIPPED tests
            elif 'SKIPPED' in line:
                if 'tests/' in line:
                    parts = line.split('SKIPPED')
                    if len(parts) > 1:
                        test_part = parts[1].strip()
                        if 'tests/' in test_part:
                            test_part = 'tests/' + test_part.split('tests/')[1]
                            colon_parts = test_part.split(':')
                            test_name = f"{colon_parts[0]}:{colon_parts[1]}" if len(colon_parts)>=2 else colon_parts[0]
                            if test_name.startswith('tests/'):
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
