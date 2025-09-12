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
apt-get update
###ACTION_DELIMITER###
apt-get install -y libjpeg62-turbo-dev zlib1g-dev libpng-dev libfreetype6-dev gettext
###ACTION_DELIMITER###
pip install -e ".[testing]"
###ACTION_DELIMITER###
echo 'python runtests.py --verbosity=2' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install "Django~=5.0.0"
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libavif-dev
###ACTION_DELIMITER###
pip install --force-reinstall Pillow
###ACTION_DELIMITER###
pip install "Pillow<11.0.0" --force-reinstall
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install --force-reinstall Pillow==10.4.0
###ACTION_DELIMITER###
python -c "from PIL import Image; print('AVIF' in Image.SAVE)"
###ACTION_DELIMITER###
apt-get install -y gcc python3-dev libavif-dev && pip install --force-reinstall --no-binary Pillow Pillow==10.4.0
###ACTION_DELIMITER###
python -c "from PIL import Image; print('AVIF' in Image.SAVE)"
###ACTION_DELIMITER###
apt-get install -y libaom-dev && pip install --force-reinstall --no-binary Pillow Pillow==10.4.0
###ACTION_DELIMITER###
apt-get install -y pkg-config && pip install --force-reinstall --no-binary Pillow --verbose Pillow==10.4.0
###ACTION_DELIMITER###
CFLAGS=$(pkg-config --cflags libavif) LDFLAGS=$(pkg-config --libs libavif) pip install --force-reinstall --no-binary Pillow Pillow==10.4.0
###ACTION_DELIMITER###
pip install --force-reinstall --no-binary Pillow --verbose Pillow==10.4.0 | grep -i 'avif'
###ACTION_DELIMITER###
pip install --force-reinstall --no-binary Pillow -vvv Pillow==10.4.0 2>&1 | grep -i 'avif'
###ACTION_DELIMITER###
pkg-config --cflags --libs libavif"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python runtests.py --verbosity=2

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
python runtests.py --verbosity=2

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
python runtests.py --verbosity=2

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
RUN git clone https://github.com/wagtail/wagtail.git /home/wagtail

WORKDIR /home/wagtail
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("wagtail", "wagtail_12006_to_11736")
class WAGTAIL_12006_TO_11736(Instance):
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
        # Pattern for failed tests: matches (fully.qualified.test.name) after FAIL: or ERROR:
        failed_pattern = re.compile(r'(FAIL|ERROR): \w+ \(([^)]+)\)')
        failed_matches = failed_pattern.findall(log)
        for match in failed_matches:
            failed_tests.add(match[1].strip())
        # Pattern for skipped tests: handles multi-line (test name on line N, skipped on line N+1)
        skipped_pattern = re.compile(r'\(([^)]+)\).*?\.\.\. skipped', re.DOTALL)
        skipped_matches = skipped_pattern.findall(log)
        for match in skipped_matches:
            skipped_tests.add(match.strip())
        # Pattern for passed tests: handles multi-line (test name on line N, ok on line N+1)
        passed_pattern = re.compile(r'\(([^)]+)\).*?\.\.\. ok', re.DOTALL)
        passed_matches = passed_pattern.findall(log)
        for match in passed_matches:
            test_name = match.strip()
            if test_name not in failed_tests and test_name not in skipped_tests:
                passed_tests.add(test_name)
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
