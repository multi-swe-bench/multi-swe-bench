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
        return "python:3.6"

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
cat makefile
###ACTION_DELIMITER###
cat pywbem_os_setup.sh
###ACTION_DELIMITER###
sed -i 's/sudo //g' pywbem_os_setup.sh
###ACTION_DELIMITER###
make develop
###ACTION_DELIMITER###
pip install packaging
###ACTION_DELIMITER###
make develop
###ACTION_DELIMITER###
echo 'pytest -v -rA --cov pywbem --cov pywbem_mock --cov-config coveragerc --ignore=attic --ignore=releases -s ./testsuite' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -rA -W ignore::pytest.PytestDeprecationWarning --cov pywbem --cov pywbem_mock --cov-config coveragerc --ignore=attic --ignore=releases -s ./testsuite' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls testsuite
###ACTION_DELIMITER###
pip install pytest==6.2.5
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'PYTHONWARNINGS="ignore::pytest.PytestDeprecationWarning" pytest -v -rA --cov pywbem --cov pywbem_mock --cov-config coveragerc --ignore=attic --ignore=releases -s ./testsuite' > test_commands.sh
###ACTION_DELIMITER###
echo 'PYTHONWARNINGS="ignore::DeprecationWarning" pytest -v -rA --cov pywbem --cov pywbem_mock --cov-config coveragerc --ignore=attic --ignore=releases -s ./testsuite' > test_commands.sh
###ACTION_DELIMITER###
cat setup.cfg
###ACTION_DELIMITER###
sed -i 's/warnerrors = true/warnerrors = false/' setup.cfg
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cat testsuite/pytest_extensions.py
###ACTION_DELIMITER###
echo 'pytest -v -rA -W ignore::DeprecationWarning --cov pywbem --cov pywbem_mock --cov-config coveragerc --ignore=attic --ignore=releases -s ./testsuite' > test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -rA -W ignore::pytest.PytestDeprecationWarning:conftest --cov pywbem --cov pywbem_mock --cov-config coveragerc --ignore=attic --ignore=releases -s ./testsuite' > test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -rA -W ignore::DeprecationWarning:pytest --cov pywbem --cov pywbem_mock --cov-config coveragerc --ignore=attic --ignore=releases -s ./testsuite' > test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -rA -W ignore::DeprecationWarning -W ignore::pytest.PytestDeprecationWarning --cov pywbem --cov pywbem_mock --cov-config coveragerc --ignore=attic --ignore=releases -s ./testsuite' > test_commands.sh
###ACTION_DELIMITER###
pip install pytest==6.0.0
###ACTION_DELIMITER###
pip install pytest==5.4.3
###ACTION_DELIMITER###
find . -name conftest.py
###ACTION_DELIMITER###
sed -i '211s/return YamlFile(path, parent)/return YamlFile.from_parent(parent, path=path)/' testsuite/testclient/conftest.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i '211s/path=path/fspath=path/' testsuite/testclient/conftest.py
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v -rA -W ignore::DeprecationWarning -W ignore::pytest.PytestDeprecationWarning --cov pywbem --cov pywbem_mock --cov-config coveragerc --ignore=attic --ignore=releases -s ./testsuite

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
pytest -v -rA -W ignore::DeprecationWarning -W ignore::pytest.PytestDeprecationWarning --cov pywbem --cov pywbem_mock --cov-config coveragerc --ignore=attic --ignore=releases -s ./testsuite

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
pytest -v -rA -W ignore::DeprecationWarning -W ignore::pytest.PytestDeprecationWarning --cov pywbem --cov pywbem_mock --cov-config coveragerc --ignore=attic --ignore=releases -s ./testsuite

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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.6

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
RUN git clone https://github.com/pywbem/pywbem.git /home/pywbem

WORKDIR /home/pywbem
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pywbem", "pywbem_1274_to_1264")
class PYWBEM_1274_TO_1264(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re

        # import json  # Not used
        # Regex patterns to match FULL test names (e.g., testsuite/file.py::class::function[params])
        test_pattern = re.compile(
            r"(testsuite/[^:]+::[^:]+(?:::[^:]+)?(?:\[[^\]]*\])?)\s+(PASSED|FAILED|SKIPPED)"
        )
        status_before_pattern = re.compile(
            r"(PASSED|FAILED|SKIPPED)\s+(testsuite/[^:]+::[^:]+(?:::[^:]+)?(?:\[[^\]]*\])?)"
        )
        # Split log into lines and process each line
        for line in log.split("\n"):
            line = line.strip()
            match_after = test_pattern.search(line)
            match_before = status_before_pattern.search(line)
            test_name = None
            status = None
            if match_after:
                test_name = match_after.group(1)
                status = match_after.group(2)
            elif match_before:
                status = match_before.group(1)
                test_name = match_before.group(2)
            else:
                continue  # Skip invalid lines
            # Normalize test name (remove leading path if present)
            test_name = re.sub(r"^.*/(testsuite/)", r"\1", test_name)
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
