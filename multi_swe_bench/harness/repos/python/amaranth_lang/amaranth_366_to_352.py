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
        return "python:3.11-slim"
    
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
pip install .
###ACTION_DELIMITER###
find . -name "test_*.py"
###ACTION_DELIMITER###
echo 'pytest --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
echo 'pytest nmigen/test/ --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest nmigen/test/ -v --no-header -rA -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install markupsafe==1.1.1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y symbiyosys iverilog
###ACTION_DELIMITER###
sed -i 's/main/main contrib non-free/' /etc/apt/sources.list && apt-get update && apt-get install -y symbiyosys iverilog
###ACTION_DELIMITER###
ls /etc/apt/
###ACTION_DELIMITER###
ls /etc/apt/sources.list.d/
###ACTION_DELIMITER###
sed -i 's/Components: main/Components: main contrib/' /etc/apt/sources.list.d/debian.sources && apt-get update && apt-get install -y symbiyosys iverilog
###ACTION_DELIMITER###
sed -i 's/Components: main contrib/Components: main contrib non-free/' /etc/apt/sources.list.d/debian.sources && apt-get update && apt search symbiyosys && apt-get install -y iverilog
###ACTION_DELIMITER###
wget http://deb.debian.org/debian/pool/contrib/s/symbiyosys/symbiyosys_1.0.0-2_all.deb && dpkg -i symbiyosys_1.0.0-2_all.deb
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget http://deb.debian.org/debian/pool/contrib/s/symbiyosys/symbiyosys_1.0.0-2_all.deb && dpkg -i symbiyosys_1.0.0-2_all.deb
###ACTION_DELIMITER###
apt-get install -y yosys
###ACTION_DELIMITER###
git clone https://github.com/YosysHQ/SymbiYosys.git && cd SymbiYosys && make install
###ACTION_DELIMITER###
apt-get install -y make
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
bash /home/amaranth/test_commands.sh
###ACTION_DELIMITER###
cd /home/amaranth/ && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y z3 && sby --version && yosys --version && bash test_commands.sh -v
###ACTION_DELIMITER###
pip install click
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sby --version && yosys --version && z3 --version && iverilog -v && pip install cocotb && sed -i 's/--tb=no/-v/' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pytest/pytest -v/' test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v nmigen/test/ -v --no-header -rA -p no:cacheprovider

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
pytest -v nmigen/test/ -v --no-header -rA -p no:cacheprovider

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
pytest -v nmigen/test/ -v --no-header -rA -p no:cacheprovider

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

# Choose an appropriate base image based on the project's requirements - replace python:3.11-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.11-slim

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
RUN git clone https://github.com/amaranth-lang/amaranth.git /home/amaranth

WORKDIR /home/amaranth
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("amaranth-lang", "amaranth_366_to_352")
class AMARANTH_366_TO_352(Instance):
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
        # Regex pattern to match test names (e.g., nmigen/test/compat/test_coding.py::EncCase::test_run_sequence)
        test_name_pattern = re.compile(r'[\w\/]+\.py::\w+::\w+')
        # Split log into lines
        for line in log.split('\n'):
            # Find all test names in the line
            test_names = test_name_pattern.findall(line)
            if not test_names:
                continue
            # Assume the first test name in the line is the one we want
            test_name = test_names[0]
            # Check for status
            if 'PASSED' in line:
                passed_tests.add(test_name)
            elif 'FAILED' in line:
                failed_tests.add(test_name)
            elif 'SKIPPED' in line:
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
