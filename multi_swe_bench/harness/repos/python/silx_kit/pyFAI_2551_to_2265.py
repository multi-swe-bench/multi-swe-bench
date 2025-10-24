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
                """ls -la
###ACTION_DELIMITER###
cat requirements.txt
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y build-essential libgl1-mesa-glx libgfortran5 libhdf5-dev libfreetype6-dev libpng-dev pkg-config
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
python run_tests.py --help
###ACTION_DELIMITER###
echo 'python run_tests.py -vv' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'python run_tests.py -vv -x -g -o -l' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'meson test -C build -v' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
echo 'meson test -C build -v -j 4' > test_commands.sh
###ACTION_DELIMITER###
meson build
###ACTION_DELIMITER###
ninja -C build
###ACTION_DELIMITER###
ls -la .github/workflows
###ACTION_DELIMITER###
cat .github/workflows/python-package.yml
###ACTION_DELIMITER###
echo 'python run_tests.py -v -x -g -o -l' > test_commands.sh
###ACTION_DELIMITER###
echo 'python run_tests.py -v' > test_commands.sh
###ACTION_DELIMITER###
echo 'python run_tests.py -v -x -g -o -l' > test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -n auto' > test_commands.sh
###ACTION_DELIMITER###
echo 'python run_tests.py --installed -v -x -g -o -l' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
meson install -C build
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
meson setup --prefix /usr/local build
###ACTION_DELIMITER###
meson setup --reconfigure --prefix /usr/local build
###ACTION_DELIMITER###
ninja -C build
###ACTION_DELIMITER###
ls /usr/local/lib/python3.10/site-packages | grep pyFAI
###ACTION_DELIMITER###
meson install -C build
###ACTION_DELIMITER###
python -c "import pyFAI; print('pyFAI imported successfully')"
###ACTION_DELIMITER###
echo 'python run_tests.py -v -x -g -o -l' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
python run_tests.py -v -x -g -o -l

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
python run_tests.py -v -x -g -o -l

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
python run_tests.py -v -x -g -o -l

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
RUN git clone https://github.com/silx-kit/pyFAI.git /home/pyFAI

WORKDIR /home/pyFAI
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("silx-kit", "pyFAI_2551_to_2265")
class PYFAI_2551_TO_2265(Instance):
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

        lines = log.split("\n")
        for i, line in enumerate(lines):
            # Pattern 1: test method, class, and status on the same line (e.g., "test_helium (module.Class) ... ERROR")
            same_line_match = re.match(
                r"^\s*(test\w+) \(([\w.]+)\) \.\.\. (\w+)\s*", line
            )
            if same_line_match:
                test_method = same_line_match.group(1)
                module_class = same_line_match.group(2)
                status = same_line_match.group(3).lower()
                full_test_name = f"{module_class}.{test_method}"
                if status == "ok":
                    passed_tests.add(full_test_name)
                elif status in ["error", "failed"]:
                    failed_tests.add(full_test_name)
                elif status == "skipped":
                    skipped_tests.add(full_test_name)
                continue
            # Pattern 2: SKIPPED: test method and class (e.g., "SKIPPED: test_sigma_clip_hor (module.Class)")
            skipped_match = re.match(r"^\s*SKIPPED: (test\w+) \(([\w.]+)\)\s*", line)
            if skipped_match:
                test_method = skipped_match.group(1)
                module_class = skipped_match.group(2)
                full_test_name = f"{module_class}.{test_method}"
                skipped_tests.add(full_test_name)
                continue
            # Pattern 3: test method and class on current line, status on next line (e.g., "test_XYZ (module.Class)" followed by "... ok")
            test_line_match = re.match(r"^\s*(test\w+) \(([\w.]+)\)\s*$", line)
            if test_line_match:
                test_method = test_line_match.group(1)
                module_class = test_line_match.group(2)
                full_test_name = f"{module_class}.{test_method}"
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    status_match = re.search(r"\.\.\. (\w+)\s*$", next_line)
                    if status_match:
                        status = status_match.group(1).lower()
                        if status == "ok":
                            passed_tests.add(full_test_name)
                        elif status in ["error", "failed"]:
                            failed_tests.add(full_test_name)
                        elif status == "skipped":
                            skipped_tests.add(full_test_name)
                continue
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
