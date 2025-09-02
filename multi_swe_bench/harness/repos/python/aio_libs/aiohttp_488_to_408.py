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
cat requirements-dev.txt
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
cat tox.ini
###ACTION_DELIMITER###
cat setup.py
###ACTION_DELIMITER###
pip install .[tests]
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install .[tests]
###ACTION_DELIMITER###
pip install nose gunicorn
###ACTION_DELIMITER###
pip install pytest pytest-nose
###ACTION_DELIMITER###
pip install nose2
###ACTION_DELIMITER###
nose2 -v
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.5 python3.5-venv
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository -y ppa:deadsnakes/ppa
###ACTION_DELIMITER###
sed -i 's/asyncio.async/asyncio.ensure_future/g' aiohttp/client_reqrep.py
###ACTION_DELIMITER###
nose2 -v
###ACTION_DELIMITER###
apt-get install -y python3.7 python3.7-venv
###ACTION_DELIMITER###
python3.7 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install .
###ACTION_DELIMITER###
pip install nose gunicorn coverage
###ACTION_DELIMITER###
nosetests -v
###ACTION_DELIMITER###
sed -i 's/asyncio.async/asyncio.ensure_future/g' aiohttp/server.py
###ACTION_DELIMITER###
nosetests -v
###ACTION_DELIMITER###
echo 'nosetests -v --processes=4' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
nosetests -v --processes=4

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
nosetests -v --processes=4

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
nosetests -v --processes=4

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
RUN git clone https://github.com/aio-libs/aiohttp.git /home/aiohttp

WORKDIR /home/aiohttp
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("aio-libs", "aiohttp_488_to_408")
class AIOHTTP_488_TO_408(Instance):
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
        # Split log into lines and process each line
        lines = log.split('\n')
        for line in lines:
            line = line.strip()
            # Skip setup syntax errors
            if 'Failure: SyntaxError' in line:
                continue
            # Handle SKIP lines
            if line.upper().startswith(('SKIP:', 'SKIPPED:')):
                test_name = line.split(':', 1)[1].strip()
                skipped_tests.add(test_name)
            # Handle test lines with '...'
            if '...' in line:
                test_part, status_part = line.split('...', 1)
                test_name = test_part.split(']')[-1].strip() if ']' in test_part else test_part.strip()
                status = re.sub(r'[^A-Z]', '', status_part.strip().upper())
                if status == 'OK':
                    passed_tests.add(test_name)
                elif status in ('FAIL', 'ERROR'):
                    # Clean test name by removing trailing warnings
                    clean_test_name = test_name.split('/')[0].strip()
                    failed_tests.add(clean_test_name)
                elif status.startswith(('SKIP', 'SKIPPED', 'SK', 'S')):
                    skipped_tests.add(test_name)
            # Handle FAIL/ERROR lines
            elif line.startswith(('FAIL:', 'ERROR:')):
                test_name = line.split(':', 1)[1].strip()
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
