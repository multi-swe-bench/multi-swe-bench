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
        return "python:3.10-slim"
    
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
                """apt-get update && apt-get install -y libopenjp2-7 libtiff5 libjpeg62-turbo libpng16-16 libfreetype6 libgfortran5
###ACTION_DELIMITER###
apt-get update && apt-get install -y libopenjp2-7 libtiff6 libjpeg62-turbo libpng16-16 libfreetype6 libgfortran5
###ACTION_DELIMITER###
pip install .[tests,all]
###ACTION_DELIMITER###
apt-get install -y build-essential
###ACTION_DELIMITER###
pip install .[tests,all]
###ACTION_DELIMITER###
echo 'ASTROPY_SKIP_LEAP_SECOND_UPDATE=1 SQLALCHEMY_SILENCE_UBER_WARNING=1 PYTHONWARNINGS="ignore::DeprecationWarning:numpy.core.fromnumeric" pytest -vvv -r a -W ignore::pytest.PytestRemovedIn9Warning -W ignore::astropy.utils.iers.iers.IERSStaleWarning -W ignore::astropy.utils.exceptions.AstropyWarning --pyargs sunpy' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install sqlalchemy==1.4.49 numpy==1.26.4
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'ASTROPY_SKIP_LEAP_SECOND_UPDATE=1 SQLALCHEMY_SILENCE_UBER_WARNING=1 PYTHONWARNINGS="ignore:product is deprecated:numpy.core.fromnumeric" pytest -vvv -r a -W ignore::pytest.PytestRemovedIn9Warning -W ignore::astropy.utils.iers.iers.IERSStaleWarning -W ignore::astropy.utils.exceptions.AstropyWarning --pyargs sunpy' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'ASTROPY_SKIP_LEAP_SECOND_UPDATE=1 SQLALCHEMY_SILENCE_UBER_WARNING=1 PYTHONWARNINGS="ignore:`product` is deprecated:DeprecationWarning:numpy.core.fromnumeric" pytest -vvv -r a -W ignore::pytest.PytestRemovedIn9Warning -W ignore::astropy.utils.iers.iers.IERSStaleWarning -W ignore::astropy.utils.exceptions.AstropyWarning --pyargs sunpy' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'ASTROPY_SKIP_LEAP_SECOND_UPDATE=1 SQLALCHEMY_SILENCE_UBER_WARNING=1 PYTHONWARNINGS="ignore:\`product\` is deprecated:DeprecationWarning:numpy.core.fromnumeric" pytest -vvv -r a -W ignore::pytest.PytestRemovedIn9Warning -W ignore::astropy.utils.iers.iers.IERSStaleWarning -W ignore::astropy.utils.exceptions.AstropyWarning --pyargs sunpy' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'ASTROPY_SKIP_LEAP_SECOND_UPDATE=1 SQLALCHEMY_SILENCE_UBER_WARNING=1 pytest -vvv -r a -W ignore::pytest.PytestRemovedIn9Warning -W ignore::astropy.utils.iers.iers.IERSStaleWarning -W ignore::astropy.utils.exceptions.AstropyWarning -W "ignore:`product` is deprecated as of NumPy 1.25.0:DeprecationWarning:numpy.core.fromnumeric" --pyargs sunpy' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'ASTROPY_SKIP_LEAP_SECOND_UPDATE=1 SQLALCHEMY_SILENCE_UBER_WARNING=1 PYTHONWARNINGS="ignore::DeprecationWarning:numpy.core.fromnumeric" pytest -vvv -r a -W ignore::pytest.PytestRemovedIn9Warning -W ignore::astropy.utils.iers.iers.IERSStaleWarning -W ignore::astropy.utils.exceptions.AstropyWarning --pyargs sunpy' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'ASTROPY_SKIP_LEAP_SECOND_UPDATE=1 SQLALCHEMY_SILENCE_UBER_WARNING=1 pytest -vvv -r a -W ignore::pytest.PytestRemovedIn9Warning -W ignore::astropy.utils.iers.iers.IERSStaleWarning -W ignore::astropy.utils.exceptions.AstropyWarning --override-ini=filterwarnings=ignore::DeprecationWarning:numpy.core.fromnumeric --pyargs sunpy' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
ASTROPY_SKIP_LEAP_SECOND_UPDATE=1 SQLALCHEMY_SILENCE_UBER_WARNING=1 pytest -vvv -r a -W ignore::pytest.PytestRemovedIn9Warning -W ignore::astropy.utils.iers.iers.IERSStaleWarning -W ignore::astropy.utils.exceptions.AstropyWarning --override-ini=filterwarnings=ignore::DeprecationWarning:numpy.core.fromnumeric --pyargs sunpy

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
ASTROPY_SKIP_LEAP_SECOND_UPDATE=1 SQLALCHEMY_SILENCE_UBER_WARNING=1 pytest -vvv -r a -W ignore::pytest.PytestRemovedIn9Warning -W ignore::astropy.utils.iers.iers.IERSStaleWarning -W ignore::astropy.utils.exceptions.AstropyWarning --override-ini=filterwarnings=ignore::DeprecationWarning:numpy.core.fromnumeric --pyargs sunpy

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
ASTROPY_SKIP_LEAP_SECOND_UPDATE=1 SQLALCHEMY_SILENCE_UBER_WARNING=1 pytest -vvv -r a -W ignore::pytest.PytestRemovedIn9Warning -W ignore::astropy.utils.iers.iers.IERSStaleWarning -W ignore::astropy.utils.exceptions.AstropyWarning --override-ini=filterwarnings=ignore::DeprecationWarning:numpy.core.fromnumeric --pyargs sunpy

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

# Choose an appropriate base image based on the project's requirements - replace python:3.10-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.10-slim

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
RUN git clone https://github.com/sunpy/sunpy.git /home/sunpy

WORKDIR /home/sunpy
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("sunpy", "sunpy_6605_to_6189")
class SUNPY_6605_TO_6189(Instance):
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
        import json
        # Regex patterns to match test results
        # Pattern for passed and skipped tests (lines with [  X%])
        status_pattern = re.compile(r'^(sunpy/.*?)\s+(PASSED|SKIPPED)(?:\s+\[\s*\d+%\])?$|^(SKIPPED)\s+(sunpy/.*?)(?:\s+-.*)?$|^(?:skipped:?)\s+(sunpy/.*)$', re.MULTILINE | re.IGNORECASE)
        # Pattern for failed tests (lines starting with FAILED)
        failed_pattern = re.compile(r'^FAILED\s+(sunpy/.*?)\s+-', re.MULTILINE)
        # Extract passed and skipped tests
        for match in status_pattern.finditer(log):
            if match.group(2):  # Matches test_name followed by status
                test_name = match.group(1).strip()
                status = match.group(2)
            elif match.group(3):  # Matches status followed by test_name (SKIPPED)
                test_name = match.group(4).strip()
                status = match.group(3)
            elif match.group(5):  # Matches 'skipped: test_name'
                test_name = match.group(5).strip()
                status = 'SKIPPED'
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
        # Extract failed tests
        for match in failed_pattern.finditer(log):
            test_name = match.group(1).strip()
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
