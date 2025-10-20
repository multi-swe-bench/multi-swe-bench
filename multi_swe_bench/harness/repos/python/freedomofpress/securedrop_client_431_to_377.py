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
                """apt-get update && apt-get install -y software-properties-common && add-apt-repository -y ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.5 python3.5-venv
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository -y ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.5 python3-virtualenv
###ACTION_DELIMITER###
virtualenv --python=python3.5 .venv && source .venv/bin/activate && pip install --require-hashes -r dev-requirements.txt
###ACTION_DELIMITER###
python3.5 --version
###ACTION_DELIMITER###
apt-cache search python3.5
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.7 python3.7-venv && python3.7 -m venv .venv && source .venv/bin/activate && pip install --require-hashes -r dev-requirements.txt
###ACTION_DELIMITER###
python3.7 -m venv .venv && source .venv/bin/activate && pip install 'setuptools<40.0.0' && pip install --require-hashes -r dev-requirements.txt
###ACTION_DELIMITER###
echo 'source .venv/bin/activate && make test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgl1-mesa-glx
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgl1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y xvfb
###ACTION_DELIMITER###
echo 'source .venv/bin/activate && xvfb-run make test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y xserver-xorg-core xfonts-base xfonts-75dpi
###ACTION_DELIMITER###
Xvfb :99 -screen 0 1024x768x16
###ACTION_DELIMITER###
echo 'source .venv/bin/activate && xvfb-run -a make test' > test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y xorg openbox libxinerama1 libxi6 libxtst6
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
Xvfb :99 -screen 0 1024x768x16 -verbose 5 > xvfb.log 2>&1
###ACTION_DELIMITER###
cat xvfb.log
###ACTION_DELIMITER###

###ACTION_DELIMITER###
Xvfb :99 -screen 0 1024x768x16
###ACTION_DELIMITER###
echo 'source .venv/bin/activate && xvfb-run -a -s "-screen 0 1024x768x24" make test' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'source .venv/bin/activate
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
make test
kill $!' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source .venv/bin/activate
Xvfb :99 -screen 0 1024x768x24 &
sleep 2
export DISPLAY=:99
make test
kill $!' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'source .venv/bin/activate
Xvfb :99 -screen 0 1024x768x24 > xvfb.log 2>&1 &
sleep 5
if ! xdpyinfo -display :99 > /dev/null 2>&1; then echo "Xvfb failed to start"; cat xvfb.log; exit 1; fi
export DISPLAY=:99
make test
kill $!' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic && echo 'source .venv/bin/activate && xvfb-run -a -s "-screen 0 1024x768x24" make test' > test_commands.sh
###ACTION_DELIMITER###
echo 'source .venv/bin/activate && xvfb-run -a -s "-screen 0 1024x768x24" -e xvfb.log make test' > test_commands.sh && bash test_commands.sh && cat xvfb.log
###ACTION_DELIMITER###
Xvfb :99 -screen 0 1024x768x24 -logfile xvfb.log 2>&1 & sleep 2; if ! xdpyinfo -display :99 >/dev/null 2>&1; then echo 'Xvfb failed to start'; cat xvfb.log; else echo 'Xvfb started successfully'; fi
###ACTION_DELIMITER###
echo -e 'source .venv/bin/activate
Xvfb :0 -screen 0 1024x768x24 > xvfb.log 2>&1 &
sleep 5
if xdpyinfo -display :0 >/dev/null 2>&1; then
  export DISPLAY=:0
  make test
else
  echo "Xvfb failed to start. Logs:
" && cat xvfb.log
fi' > test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
source .venv/bin/activate
Xvfb :0 -screen 0 1024x768x24 > xvfb.log 2>&1 &
sleep 5
if xdpyinfo -display :0 >/dev/null 2>&1; then
  export DISPLAY=:0
  make test
else
  echo "Xvfb failed to start. Logs:
" && cat xvfb.log
fi

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
source .venv/bin/activate
Xvfb :0 -screen 0 1024x768x24 > xvfb.log 2>&1 &
sleep 5
if xdpyinfo -display :0 >/dev/null 2>&1; then
  export DISPLAY=:0
  make test
else
  echo "Xvfb failed to start. Logs:
" && cat xvfb.log
fi

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
source .venv/bin/activate
Xvfb :0 -screen 0 1024x768x24 > xvfb.log 2>&1 &
sleep 5
if xdpyinfo -display :0 >/dev/null 2>&1; then
  export DISPLAY=:0
  make test
else
  echo "Xvfb failed to start. Logs:
" && cat xvfb.log
fi

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
RUN git clone https://github.com/freedomofpress/securedrop-client.git /home/securedrop-client

WORKDIR /home/securedrop-client
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("freedomofpress", "securedrop_client_431_to_377")
class SECUREDROP_CLIENT_431_TO_377(Instance):
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
        # Regex pattern to match test lines with status
        pattern = re.compile(r'^(tests/.*?)\s+(PASSED|FAILED|SKIPPED)\s+\[\s*\d+%\]', re.MULTILINE)
        # Extract test cases and statuses
        for match in pattern.finditer(log):
            test_name = match.group(1)
            status = match.group(2)
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status == "FAILED":
                failed_tests.add(test_name)
            elif status == "SKIPPED":
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
