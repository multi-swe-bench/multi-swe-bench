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

###ACTION_DELIMITER###
apt-get update && apt-get install -y python3-setuptools
###ACTION_DELIMITER###
echo -e 'pytest -v --durations=10 --cov=libertem --cov-report=term --cov-report=html --cov-report=xml --cov-config=setup.cfg --junitxml=junit.xml tests/
pytest -v --doctest-modules --ignore=src/libertem/common/win_tweaks.py src/libertem/' > test_commands.sh
###ACTION_DELIMITER###
pip install -e . && pip install -r test_requirements.txt && pip install nbval nbqa libertem-blobfinder hyperspy pyxem scikit-image 'pint<0.20'
###ACTION_DELIMITER###
apt-get install -y python3-pip
###ACTION_DELIMITER###
pip3 install -e . && pip3 install -r test_requirements.txt && pip3 install nbval nbqa libertem-blobfinder hyperspy pyxem scikit-image 'pint<0.20'
###ACTION_DELIMITER###
python3 -m venv libertem-venv && source libertem-venv/bin/activate && pip install -e . && pip install -r test_requirements.txt && pip install nbval nbqa libertem-blobfinder hyperspy pyxem scikit-image 'pint<0.20'
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv libertem-venv && source libertem-venv/bin/activate && pip install -e . && pip install -r test_requirements.txt && pip install nbval nbqa libertem-blobfinder hyperspy pyxem scikit-image 'pint<0.20'
###ACTION_DELIMITER###
echo -e 'pytest -v --durations=10 --cov=libertem --cov-report=term --cov-report=html --cov-report=xml --cov-config=setup.cfg --junitxml=junit.xml tests/
pytest -v --doctest-modules --ignore=src/libertem/common/win_tweaks.py src/libertem/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source libertem-venv/bin/activate && pip install setuptools
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source libertem-venv/bin/activate
pytest -v --durations=10 --cov=libertem --cov-report=term --cov-report=html --cov-report=xml --cov-config=setup.cfg --junitxml=junit.xml tests/
pytest -v --doctest-modules --ignore=src/libertem/common/win_tweaks.py src/libertem/' > test_commands.sh
###ACTION_DELIMITER###
source libertem-venv/bin/activate && pip install hdbscan numpy
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source libertem-venv/bin/activate && pip install numpy==1.26.4 && pip install --force-reinstall 'pint<0.20'
###ACTION_DELIMITER###
source libertem-venv/bin/activate && pip install numpy==1.26.4 ncempy==1.12.0 'pint<0.20'
###ACTION_DELIMITER###
source libertem-venv/bin/activate && pip install numpy>=2 ncempy 'pint<0.20'
###ACTION_DELIMITER###
source libertem-venv/bin/activate && pip install 'numpy>=2.0,<2.3' 'numba>=0.64' ncempy 'pint<0.20'
###ACTION_DELIMITER###
source libertem-venv/bin/activate && pip install numpy==2.2.6 ncempy 'pint<0.20'
###ACTION_DELIMITER###
source libertem-venv/bin/activate && pip install numpy==1.26.4 ncempy==1.11.0 'pint<0.20'
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
source libertem-venv/bin/activate
pytest -v --durations=10 --cov=libertem --cov-report=term --cov-report=html --cov-report=xml --cov-config=setup.cfg --junitxml=junit.xml tests/
pytest -v --doctest-modules --ignore=src/libertem/common/win_tweaks.py src/libertem/

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
source libertem-venv/bin/activate
pytest -v --durations=10 --cov=libertem --cov-report=term --cov-report=html --cov-report=xml --cov-config=setup.cfg --junitxml=junit.xml tests/
pytest -v --doctest-modules --ignore=src/libertem/common/win_tweaks.py src/libertem/

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
source libertem-venv/bin/activate
pytest -v --durations=10 --cov=libertem --cov-report=term --cov-report=html --cov-report=xml --cov-config=setup.cfg --junitxml=junit.xml tests/
pytest -v --doctest-modules --ignore=src/libertem/common/win_tweaks.py src/libertem/

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
RUN git clone https://github.com/LiberTEM/LiberTEM.git /home/LiberTEM

WORKDIR /home/LiberTEM
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("LiberTEM", "LiberTEM_1535_to_1285")
class LIBERTEM_1535_TO_1285(Instance):
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
        # Regex pattern to match test lines with status
        pattern = re.compile(r'(tests/.+?)\s+(PASSED|SKIPPED|FAILED)', re.MULTILINE)
        matches = pattern.findall(log)
        for test_id, status in matches:
            if status == 'PASSED':
                passed_tests.add(test_id)
            elif status == 'SKIPPED':
                skipped_tests.add(test_id)
            elif status == 'FAILED':
                failed_tests.add(test_id)
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
