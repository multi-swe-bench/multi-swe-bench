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
        return "python:3.7-slim"

    def image_prefix(self) -> str:
        return "envagent"

    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:
        repo_name = self.pr.repo
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
apt-get update && apt-get install -y build-essential libopenblas-dev liblapack-dev
###ACTION_DELIMITER###
pip install numpy==1.19.5
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install -r test_requirements.txt
###ACTION_DELIMITER###
echo -e '#!/bin/bash
python3 -m pytest -v --durations=5 --cov=libertem --cov-report=term --cov-report=html --cov-report=xml tests/
python3 -m pytest -v --doctest-modules --ignore=src/libertem/win_tweaks.py src/libertem/' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest-asyncio==0.16.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install hdbscan && pip install numba==0.54.1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install scipy==1.8.0 && pip install numba==0.53.1
###ACTION_DELIMITER###
pip install hdbscan==0.8.27 numba==0.52.0
###ACTION_DELIMITER###
pip install Cython==0.29.36 && pip install hdbscan==0.8.27 && pip install numba==0.52.0
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgomp1 && pip install hdbscan==0.8.27 numba==0.52.0
###ACTION_DELIMITER###
pip install --upgrade setuptools wheel && pip install Cython==0.29.24 && pip install hdbscan==0.8.27 numba==0.52.0
###ACTION_DELIMITER###
pip install Cython==0.29.30 hdbscan==0.8.28 numba==0.52.0
###ACTION_DELIMITER###
pip install Cython==0.29.21 hdbscan==0.8.26 numba==0.52.0
###ACTION_DELIMITER###
pip install hdbscan==0.8.26 --no-build-isolation && pip install numba==0.52.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install joblib==1.1.0 numba==0.51.0
###ACTION_DELIMITER###
pip install joblib==0.13.2 numba==0.45.0 llvmlite==0.30.0
###ACTION_DELIMITER###
sed -i 's/python3.8/python3/g' test_commands.sh && pip install numba==0.49.0 llvmlite==0.32.0 && bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
python3 -m pytest -v --durations=5 --cov=libertem --cov-report=term --cov-report=html --cov-report=xml tests/
python3 -m pytest -v --doctest-modules --ignore=src/libertem/win_tweaks.py src/libertem/

""".replace("[[REPO_NAME]]", repo_name),
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
#!/bin/bash
python3 -m pytest -v --durations=5 --cov=libertem --cov-report=term --cov-report=html --cov-report=xml tests/
python3 -m pytest -v --doctest-modules --ignore=src/libertem/win_tweaks.py src/libertem/

""".replace("[[REPO_NAME]]", repo_name),
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
#!/bin/bash
python3 -m pytest -v --durations=5 --cov=libertem --cov-report=term --cov-report=html --cov-report=xml tests/
python3 -m pytest -v --doctest-modules --ignore=src/libertem/win_tweaks.py src/libertem/

""".replace("[[REPO_NAME]]", repo_name),
            ),
        ]

    def dockerfile(self) -> str:
        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        dockerfile_content = """
# This is a template for creating a Dockerfile to test patches
# LLM should fill in the appropriate values based on the context

# Choose an appropriate base image based on the project's requirements - replace python:3.7-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.7-slim

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


@Instance.register("LiberTEM", "LiberTEM_548_to_336")
class LIBERTEM_548_TO_336(Instance):
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

        return "bash /home/run.sh"

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
        pattern = r"^(tests/.*?::.*?)\s+(PASSED|XFAIL|SKIPPED|FAILED)\s+\[\s*\d+%\s*\]$"
        # Find all matches in the log content
        matches = re.findall(pattern, log, re.MULTILINE)
        for test_name, status in matches:
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status == "SKIPPED":
                skipped_tests.add(test_name)
            elif status in ("FAILED", "XFAIL"):
                failed_tests.add(test_name)
        parsed_results = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
        }

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
