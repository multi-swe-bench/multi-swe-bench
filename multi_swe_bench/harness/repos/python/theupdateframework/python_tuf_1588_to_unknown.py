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
        return "python:3.9"
    
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
                """ls -la
###ACTION_DELIMITER###
pip install -r requirements.txt -r requirements-test.txt
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd tests
python3 -m coverage run aggregate_tests.py
python3 -m coverage report -m --fail-under 97' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
pip install --editable .
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd tests
python3 -m coverage run -m unittest discover -v
python3 -m coverage report -m --fail-under 97' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
cd tests
python3 -m coverage run -m unittest discover -v
python3 -m coverage report -m --fail-under 97

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
#!/bin/bash
cd tests
python3 -m coverage run -m unittest discover -v
python3 -m coverage report -m --fail-under 97

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
#!/bin/bash
cd tests
python3 -m coverage run -m unittest discover -v
python3 -m coverage report -m --fail-under 97

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.9

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
RUN git clone https://github.com/theupdateframework/python-tuf.git /home/python-tuf

WORKDIR /home/python-tuf
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("theupdateframework", "python_tuf_1588_to_unknown")
class PYTHON_TUF_1588_TO_UNKNOWN(Instance):
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
        import re
        # Extract condensed result string (dots, E, etc.) with optional leading/trailing whitespace
        result_match = re.search(r'^\s*([\.E]+)\s*$', log, re.MULTILINE)
        result_str = result_match.group(1) if result_match else ''
        # Extract test names in order (from any context)
        test_names = re.findall(r'(test_\w+)', log)
        # Extract total tests from 'Ran X tests' line
        ran_match = re.search(r'Ran (\d+) tests', log)
        total_tests = int(ran_match.group(1)) if ran_match else len(result_str)
        # Ensure test_names length matches total_tests (use placeholders if needed)
        if len(test_names) < total_tests:
            test_names += [f'test_{i}' for i in range(len(test_names), total_tests)]
        else:
            test_names = test_names[:total_tests]
        # Map results to test names
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        for test, result in zip(test_names, result_str):
            if result == 'E':
                failed_tests.add(test)
            elif result == '.':
                passed_tests.add(test)
        # Handle cases where only failed tests are named in the log
        if not passed_tests and total_tests > len(failed_tests):
            passed_tests = set(test_names) - failed_tests
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
