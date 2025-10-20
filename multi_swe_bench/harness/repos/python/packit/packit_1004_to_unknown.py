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
                """ls -la /home/packit
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y gnupg rpm rpm2cpio
###ACTION_DELIMITER###
pip install -e .[testing]
###ACTION_DELIMITER###
apt-get install -y libkrb5-dev
###ACTION_DELIMITER###
pip install -e .[testing]
###ACTION_DELIMITER###
apt-get install -y build-essential
###ACTION_DELIMITER###
pip install -e .[testing]
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider' > /home/packit/test_commands.sh
###ACTION_DELIMITER###
cat /home/packit/test_commands.sh
###ACTION_DELIMITER###
bash /home/packit/test_commands.sh
###ACTION_DELIMITER###
pip install flexmock
###ACTION_DELIMITER###
bash /home/packit/test_commands.sh
###ACTION_DELIMITER###
pip install --force-reinstall rebasehelper
###ACTION_DELIMITER###
ls /usr/local/lib/python3.9/site-packages/rebasehelper/helpers/
###ACTION_DELIMITER###
pip install rebasehelper==0.28.0
###ACTION_DELIMITER###
pip install rebasehelper==0.26.0
###ACTION_DELIMITER###
pip install rebasehelper==0.25.0
###ACTION_DELIMITER###
pip install rebasehelper==0.24.0
###ACTION_DELIMITER###
git clone https://github.com/rebase-helper/rebase-helper.git && cd rebase-helper && git checkout 0.23.0 && pip install .
###ACTION_DELIMITER###
pip install rebasehelper==0.21.0
###ACTION_DELIMITER###
pip install rebasehelper==0.19.0
###ACTION_DELIMITER###
ls rebasehelper/helpers/
###ACTION_DELIMITER###
pip install .
###ACTION_DELIMITER###
python -c "from rebasehelper.helpers import macro_helper; print('Success')"
###ACTION_DELIMITER###
apt-get install -y python3-rpm
###ACTION_DELIMITER###
python -c "import rpm; print('Success')"
###ACTION_DELIMITER###
python -c "from rebasehelper.helpers import macro_helper; print('Success')"
###ACTION_DELIMITER###
cd /home/packit && bash test_commands.sh
###ACTION_DELIMITER###
pip install 'setuptools<81' 'click<8.1' && rm -rf rebase-helper && pytest --collect-only -v
###ACTION_DELIMITER###
pip install requre marshmallow>=3.0.0 && pytest --collect-only -v
###ACTION_DELIMITER###
pip install requre==0.9.0 && pip install --force-reinstall marshmallow==3.19.0 && pytest --collect-only -v
###ACTION_DELIMITER###
pip install --force-reinstall flexmock==0.12.2 requre==0.11.0 && pytest --collect-only -v
###ACTION_DELIMITER###
pip install --force-reinstall flexmock==0.12.2 requre==0.9.1 && pytest --collect-only -v
###ACTION_DELIMITER###
pip install --force-reinstall flexmock==0.11.0 requre==0.8.6 && pytest --collect-only -v
###ACTION_DELIMITER###
pip install --force-reinstall flexmock==0.12.2 requre==0.9.0 && pytest --collect-only -v
###ACTION_DELIMITER###
pip install --force-reinstall pytest==7.0.0 pytest-flexmock flexmock==0.12.2 requre==0.8.6 && pytest --collect-only -v
###ACTION_DELIMITER###
pip install --force-reinstall pytest==7.0.0 flexmock==0.11.0 requre==0.8.6 && pytest --collect-only -v
###ACTION_DELIMITER###
pip install --force-reinstall flexmock==0.12.2 requre==0.8.0 pytest==7.0.0 && pytest --collect-only -v
###ACTION_DELIMITER###
pip install --force-reinstall flexmock==0.10.4 pytest==7.0.0 requre==0.8.0 && pytest --collect-only -v
###ACTION_DELIMITER###
bash /home/packit/test_commands.sh
###ACTION_DELIMITER###
apt-get install -y --reinstall rpm gnupg && chmod -R 777 /tmp && bash /home/packit/test_commands.sh -v"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v --no-header -rA --tb=no -p no:cacheprovider

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider

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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
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
RUN git clone https://github.com/packit/packit.git /home/packit

WORKDIR /home/packit
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("packit", "packit_1004_to_unknown")
class PACKIT_1004_TO_UNKNOWN(Instance):
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
        # import json  # Unused, commented out
        # Regex patterns to match test lines
        # Pattern 1: Test name followed by status and [percentage]
        pattern1 = re.compile(r'^(tests/.*?)\s+(PASSED|FAILED|SKIPPED)\s+\[\s*\d+%\s*\]$', re.MULTILINE)
        # Pattern 2: Status followed by test name
        pattern2 = re.compile(r'^\[\s*\d+\]\s+(PASSED|FAILED|SKIPPED)\s+(tests/.*)', re.MULTILINE)
        # Process pattern1 matches
        for match in pattern1.finditer(log):
            test_name = match.group(1)
            status = match.group(2)
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
        # Process pattern2 matches
        for match in pattern2.finditer(log):
            status = match.group(1)
            test_name = match.group(2)
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
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
