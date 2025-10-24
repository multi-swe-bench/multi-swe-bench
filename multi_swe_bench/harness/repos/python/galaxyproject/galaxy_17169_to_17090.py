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
                """cat README.md
###ACTION_DELIMITER###
ls
###ACTION_DELIMITER###
cat README.rst
###ACTION_DELIMITER###
cat requirements.txt
###ACTION_DELIMITER###
cat run_tests.sh
###ACTION_DELIMITER###
./scripts/common_startup.sh --dev-wheels
###ACTION_DELIMITER###
ln -s /usr/bin/python3.7 /usr/bin/python
###ACTION_DELIMITER###
./scripts/common_startup.sh --dev-wheels
###ACTION_DELIMITER###
ls -l /usr/bin/python && python3.7 --version && python --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository -y ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.7 python3.7-dev python3.7-distutils
###ACTION_DELIMITER###
./scripts/common_startup.sh --dev-wheels
###ACTION_DELIMITER###
apt-get install -y python3.7-venv
###ACTION_DELIMITER###
ln -sf /usr/bin/python3.7 /usr/bin/python3 && ./scripts/common_startup.sh --dev-wheels
###ACTION_DELIMITER###
python3.7 -m venv .venv && ./scripts/common_startup.sh --dev-wheels
###ACTION_DELIMITER###
echo './run_tests.sh -unit' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo './run_tests.sh -unit -m "not docker" --json-report' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo "./run_tests.sh -unit -m 'not docker' --json-report" > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y make && echo "./run_tests.sh -unit -- -m 'not docker' --json-report" > test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y make && echo "./run_tests.sh -unit -- -m 'not docker' --json-report" > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo "./run_tests.sh -unit -- -m 'not docker' --json-report" > test_commands.sh
###ACTION_DELIMITER###
echo 'PYTHONPATH=.:$PYTHONPATH .venv/bin/python3.7 -m pytest test/unit -m "not docker" --json-report -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo './run_tests.sh -unit --ignore=test/unit/tool_util/mulled --json-report -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo "./run_tests.sh -unit test/unit -- -m 'not docker' --json-report -v" > test_commands.sh
###ACTION_DELIMITER###
. .venv/bin/activate && pip install pytest-json-report
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo "./run_tests.sh -unit -- -m 'not docker' --ignore=test/unit/tool_util/mulled --json-report -v" > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'PYTHONPATH=.:$PYTHONPATH .venv/bin/python3.7 -m pytest test/unit -m "not docker" --json-report -v' > test_commands.sh
###ACTION_DELIMITER###
echo 'PYTHONPATH=.:$PYTHONPATH .venv/bin/python3.7 -m pytest test/unit -m "not docker" --json-report -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'PYTHONPATH=.:$PYTHONPATH .venv/bin/python3.7 -m pytest test/unit -m "not docker" --ignore=test/unit/tool_util/mulled --json-report -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'PYTHONPATH=.:$PYTHONPATH .venv/bin/python3.7 -m pytest test/unit -m "not docker" --ignore=test/unit/tool_util/test_cwl.py --ignore=test/unit/tool_util/mulled --json-report -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'PYTHONPATH=.:$PYTHONPATH .venv/bin/python3.7 -m pytest test/unit -m "not docker" --ignore=test/unit/tool_util/test_cwl.py --ignore=test/unit/tool_util/mulled --ignore=test/unit/files/test_ftp.py --ignore=test/unit/tool_util/test_container_resolution.py --ignore=test/unit/tool_util/test_conda_resolution.py --json-report -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
PYTHONPATH=.:$PYTHONPATH .venv/bin/python3.7 -m pytest test/unit -m "not docker" --ignore=test/unit/tool_util/test_cwl.py --ignore=test/unit/tool_util/mulled --ignore=test/unit/files/test_ftp.py --ignore=test/unit/tool_util/test_container_resolution.py --ignore=test/unit/tool_util/test_conda_resolution.py --json-report -v

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
PYTHONPATH=.:$PYTHONPATH .venv/bin/python3.7 -m pytest test/unit -m "not docker" --ignore=test/unit/tool_util/test_cwl.py --ignore=test/unit/tool_util/mulled --ignore=test/unit/files/test_ftp.py --ignore=test/unit/tool_util/test_container_resolution.py --ignore=test/unit/tool_util/test_conda_resolution.py --json-report -v

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
PYTHONPATH=.:$PYTHONPATH .venv/bin/python3.7 -m pytest test/unit -m "not docker" --ignore=test/unit/tool_util/test_cwl.py --ignore=test/unit/tool_util/mulled --ignore=test/unit/files/test_ftp.py --ignore=test/unit/tool_util/test_container_resolution.py --ignore=test/unit/tool_util/test_conda_resolution.py --json-report -v

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
RUN git clone https://github.com/galaxyproject/galaxy.git /home/galaxy

WORKDIR /home/galaxy
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("galaxyproject", "galaxy_17169_to_17090")
class GALAXY_17169_TO_17090(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re
        import json

        # Parse test cases using regular expressions
        pattern = re.compile(
            r"^(test/.*)\s+(PASSED|FAILED|SKIPPED)\s+\[.*?\]$", re.MULTILINE
        )
        matches = pattern.findall(log)
        for test_name, status in matches:
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status == "FAILED":
                failed_tests.add(test_name)
            elif status == "SKIPPED":
                skipped_tests.add(test_name)
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
