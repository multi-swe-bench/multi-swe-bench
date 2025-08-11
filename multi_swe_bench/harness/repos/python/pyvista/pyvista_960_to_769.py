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
        return "python:3.9-slim"
    
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
pip install numpy imageio appdirs 'scooby>=0.5.1' 'meshio>=4.0.3,<5.0' vtk
###ACTION_DELIMITER###
pip install -r requirements_test.txt
###ACTION_DELIMITER###
echo 'pytest -v -rA --tb=short' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libxrender1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
sed -i '18,20 s/^/#/' setup.py
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y vtk && pip install vtk==9.1.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgl1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgl1-mesa-glx libegl1-mesa libgles2-mesa fonts-freefont-ttf
###ACTION_DELIMITER###
apt-get update && apt-get install -y xvfb && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install numpy==1.26.4
###ACTION_DELIMITER###
xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
echo 'HYPOTHESIS_DEADLINE=500 pytest -v -rA --tb=short' > test_commands.sh
###ACTION_DELIMITER###
xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
echo 'HYPOTHESIS_DEADLINE=None pytest -v -rA --tb=short' > test_commands.sh && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
echo 'HYPOTHESIS_DEADLINE=None pytest -v -rA --tb=short --hypothesis-max-examples=50' > test_commands.sh && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
echo 'HYPOTHESIS_DEADLINE=None HYPOTHESIS_MAX_EXAMPLES=50 pytest -v -rA --tb=short' > test_commands.sh && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
echo 'HYPOTHESIS_DEADLINE=None HYPOTHESIS_MAX_EXAMPLES=50 HYPOTHESIS_HEALTH_CHECKS=deadline pytest -v -rA --tb=short' > test_commands.sh && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
echo 'HYPOTHESIS_DEADLINE=None HYPOTHESIS_MAX_EXAMPLES=50 HYPOTHESIS_HEALTH_CHECKS=none pytest -v -rA --tb=short' > test_commands.sh && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
echo -e '[hypothesis]\ndeadline = none\nmax_examples = 10\nhealth_checks = none' >> pytest.ini && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
echo 'HYPOTHESIS_DEADLINE=None HYPOTHESIS_MAX_EXAMPLES=10 HYPOTHESIS_HEALTH_CHECKS= xvfb-run -a pytest -v -rA --tb=short' > test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
HYPOTHESIS_DEADLINE=None HYPOTHESIS_MAX_EXAMPLES=10 HYPOTHESIS_HEALTH_CHECKS= xvfb-run -a pytest -v -rA --tb=short

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
HYPOTHESIS_DEADLINE=None HYPOTHESIS_MAX_EXAMPLES=10 HYPOTHESIS_HEALTH_CHECKS= xvfb-run -a pytest -v -rA --tb=short

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
HYPOTHESIS_DEADLINE=None HYPOTHESIS_MAX_EXAMPLES=10 HYPOTHESIS_HEALTH_CHECKS= xvfb-run -a pytest -v -rA --tb=short

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.9-slim

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
RUN git clone https://github.com/pyvista/pyvista.git /home/pyvista

WORKDIR /home/pyvista
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pyvista", "pyvista_960_to_769")
class PYVISTA_960_TO_769(Instance):
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
        # Regex patterns to match test names and their statuses
        patterns = [
            # Test name followed by PASSED
            (re.compile(r'(tests/.*?::test_.*?|pyvista::tests::.*?::test_.*?)\s+PASSED\b'), 'passed'),
            # PASSED followed by test name
            (re.compile(r'PASSED\s+(tests/.*?::test_.*?|pyvista::tests::.*?::test_.*?)\b'), 'passed'),
            # Test name followed by FAILED
            (re.compile(r'(tests/.*?::test_.*?|pyvista::tests::.*?::test_.*?)\s+FAILED\b'), 'failed'),
            # FAILED followed by test name
            (re.compile(r'FAILED\s+(tests/.*?::test_.*?|pyvista::tests::.*?::test_.*?)\b'), 'failed'),
            # SKIPPED with test name (assuming test name is after SKIPPED)
            (re.compile(r'.*SKIPPED\s+\[\d+\]\s+(tests/.*?:\d+)'), 'skipped'),
        ]
        for line in log.split('\n'):
            line = line.strip()
            for pattern, status in patterns:
                match = pattern.search(line)
                if match:
                    test_name = match.group(1)
                    if status == 'passed':
                        passed_tests.add(test_name)
                    elif status == 'failed':
                        failed_tests.add(test_name)
                    elif status == 'skipped':
                        skipped_tests.add(test_name)
                    break  # Stop checking other patterns for this line
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
