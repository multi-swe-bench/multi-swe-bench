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
ls requirements
###ACTION_DELIMITER###
./build.sh test
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
./build.sh test
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
./build.sh test
###ACTION_DELIMITER###
apt-get update && apt-get install -y zlib1g-dev
###ACTION_DELIMITER###
./build.sh test
###ACTION_DELIMITER###
apt-get update && apt-get install -y libssl-dev libreadline-dev libsqlite3-dev libbz2-dev liblzma-dev
###ACTION_DELIMITER###
sed -i 's/3.6.5/3.6.15/' build.sh && ./build.sh test
###ACTION_DELIMITER###
pip install 'setuptools<58.0.0' && ./build.sh test
###ACTION_DELIMITER###
sed -i 's/pygithub==1.43.7/pygithub==1.43.8/' requirements/tools.txt && ./build.sh test
###ACTION_DELIMITER###
sed -i 's/pygithub==1.43.8/pygithub==1.56/' requirements/tools.txt && ./build.sh test
###ACTION_DELIMITER###
sed -i 's/pyjwt==1.7.1/pyjwt>=2.0/' requirements/tools.txt && ./build.sh test
###ACTION_DELIMITER###
./build.sh --help
###ACTION_DELIMITER###
pip install -e . && pytest -v
###ACTION_DELIMITER###
cd hypothesis-python && pip install -e . && pytest -v
###ACTION_DELIMITER###
pip install pytest && pytest -v
###ACTION_DELIMITER###
/root/.cache/hypothesis-build-runtimes/python-versions//3.6.15/bin/python -m pytest -v
###ACTION_DELIMITER###
/root/.cache/hypothesis-build-runtimes/python-versions//3.6.15/bin/pip install pytest && /root/.cache/hypothesis-build-runtimes/python-versions//3.6.15/bin/python -m pytest -v
###ACTION_DELIMITER###
/root/.cache/hypothesis-build-runtimes/python-versions//3.6.15/bin/pip install -e . && /root/.cache/hypothesis-build-runtimes/python-versions//3.6.15/bin/python -m pytest -v
###ACTION_DELIMITER###
/root/.cache/hypothesis-build-runtimes/python-versions//3.6.15/bin/pip install mock python-dateutil pytz django dpcontracts lark-parser numpy pandas && /root/.cache/hypothesis-build-runtimes/python-versions//3.6.15/bin/python -m pytest -v
###ACTION_DELIMITER###
DJANGO_SETTINGS_MODULE=tests.django.toystore.settings /root/.cache/hypothesis-build-runtimes/python-versions//3.6.15/bin/python -m pytest -v --ignore=tests/py2/
###ACTION_DELIMITER###
/root/.cache/hypothesis-build-runtimes/python-versions//3.6.15/bin/python -m pytest -v --ignore=tests/py2/ --ignore=tests/django/
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd hypothesis-python || exit 1
/root/.cache/hypothesis-build-runtimes/python-versions//3.6.15/bin/python -m pytest -v --ignore=tests/py2/ --ignore=tests/django/' > /home/hypothesis/test_commands.sh && chmod +x /home/hypothesis/test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
cd hypothesis-python || exit 1
/root/.cache/hypothesis-build-runtimes/python-versions//3.6.15/bin/python -m pytest -v --ignore=tests/py2/ --ignore=tests/django/

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
cd hypothesis-python || exit 1
/root/.cache/hypothesis-build-runtimes/python-versions//3.6.15/bin/python -m pytest -v --ignore=tests/py2/ --ignore=tests/django/

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
cd hypothesis-python || exit 1
/root/.cache/hypothesis-build-runtimes/python-versions//3.6.15/bin/python -m pytest -v --ignore=tests/py2/ --ignore=tests/django/

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
RUN git clone https://github.com/HypothesisWorks/hypothesis.git /home/hypothesis

WORKDIR /home/hypothesis
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("HypothesisWorks", "hypothesis_1989_to_1701")
class HYPOTHESIS_1989_TO_1701(Instance):
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

        # Regex patterns for each status
        # PASSED: [line_num] test_name PASSED ...
        pattern_passed = re.compile(r"^\s*([^\s]+)\s+PASSED\b", re.MULTILINE)
        # FAILED: [line_num] FAILED test_name ...
        pattern_failed = re.compile(r"^\s*FAILED\s+([^\s]+)\b", re.MULTILINE)
        # SKIPPED: Check both possible patterns
        pattern_skipped1 = re.compile(r"^\s*([^\s]+)\s+SKIPPED\b", re.MULTILINE)
        pattern_skipped2 = re.compile(r"^\s*SKIPPED\s+([^\s]+)\b", re.MULTILINE)
        # Extract passed tests
        passed_matches = pattern_passed.findall(log)
        passed_tests.update(passed_matches)
        # Extract failed tests
        failed_matches = pattern_failed.findall(log)
        failed_tests.update(failed_matches)
        # Extract skipped tests
        skipped_matches1 = pattern_skipped1.findall(log)
        skipped_matches2 = pattern_skipped2.findall(log)
        skipped_tests.update(skipped_matches1)
        skipped_tests.update(skipped_matches2)
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
