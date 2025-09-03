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
        return "python:3.11-slim-bullseye"
    
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
ls requirements
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install -r requirements/tests.txt
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
xonsh run-tests.xsh
###ACTION_DELIMITER###
echo -e 'pytest -v -p no:xonsh --ignore tests/test_main.py --ignore tests/test_ptk_highlight.py
pytest -v -p no:xonsh tests/test_main.py
pytest -v -p no:xonsh tests/test_ptk_highlight.py' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libreadline-dev libncurses5-dev
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
make amalgamate
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make amalgamate
###ACTION_DELIMITER###
make xonsh/ply
###ACTION_DELIMITER###
git config --global user.email 'test@example.com' && git config --global user.name 'Test User'
###ACTION_DELIMITER###
make xonsh/ply
###ACTION_DELIMITER###
python -c 'import setup; setup.amalgamate_source()'
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install ply
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
rm -rf xonsh/ply && pip install -e .
###ACTION_DELIMITER###
git checkout 7e1b0997ae19fc5c3c05835b756d60634289a3bb -- xonsh/ply && pip install -e .
###ACTION_DELIMITER###
ls xonsh/ply/ply
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'pytest -v --ignore tests/test_main.py --ignore tests/test_ptk_highlight.py
pytest -v tests/test_main.py
pytest -v tests/test_ptk_highlight.py' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'pytest -v -p no:xonsh --ignore tests/test_main.py --ignore tests/test_ptk_highlight.py
pytest -v -p no:xonsh tests/test_main.py
pytest -v -p no:xonsh tests/test_ptk_highlight.py' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'pytest -v -p no:xonsh --ignore tests/test_main.py --ignore tests/test_ptk_highlight.py --ignore tests/test_integrations.py
pytest -v -p no:xonsh tests/test_main.py
pytest -v -p no:xonsh tests/test_ptk_highlight.py' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v -p no:xonsh --ignore tests/test_main.py --ignore tests/test_ptk_highlight.py --ignore tests/test_integrations.py
pytest -v -p no:xonsh tests/test_main.py
pytest -v -p no:xonsh tests/test_ptk_highlight.py

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
pytest -v -p no:xonsh --ignore tests/test_main.py --ignore tests/test_ptk_highlight.py --ignore tests/test_integrations.py
pytest -v -p no:xonsh tests/test_main.py
pytest -v -p no:xonsh tests/test_ptk_highlight.py

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
pytest -v -p no:xonsh --ignore tests/test_main.py --ignore tests/test_ptk_highlight.py --ignore tests/test_integrations.py
pytest -v -p no:xonsh tests/test_main.py
pytest -v -p no:xonsh tests/test_ptk_highlight.py

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
FROM python:3.11-slim-bullseye

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
RUN git clone https://github.com/xonsh/xonsh.git /home/xonsh

WORKDIR /home/xonsh
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("xonsh", "xonsh_3156_to_3126")
class XONSH_3156_TO_3126(Instance):
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
        # Regex pattern to match test cases with their statuses
        # Pattern: matches "tests/...::test_name STATUS ["
        pattern = r"tests/.*?::(.*?)\s+(PASSED|FAILED|SKIPPED)\s+\[" 
        matches = re.findall(pattern, log)
        for test_name, status in matches:
            if status == "PASSED":
                passed_tests.add(test_name.strip())
            elif status == "FAILED":
                failed_tests.add(test_name.strip())
            elif status == "SKIPPED":
                skipped_tests.add(test_name.strip())
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
