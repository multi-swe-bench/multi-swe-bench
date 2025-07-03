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
        return "python:3.8-slim"
    
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
                """ls -al
###ACTION_DELIMITER###
pip install 'pyutilib==5.6.5'
###ACTION_DELIMITER###
pip install -U pip setuptools wheel && pip install nose coverage codecov sphinx networkx pandas numpy seaborn
###ACTION_DELIMITER###
python setup.py develop
###ACTION_DELIMITER###
echo 'test.pyomo -v --cat=nightly pyomo ./pyomo-model-libraries' > /home/pyomo/test_commands.sh
###ACTION_DELIMITER###
bash /home/pyomo/test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
git clone https://github.com/Pyomo/pyomo-model-libraries.git /home/pyomo/pyomo-model-libraries
###ACTION_DELIMITER###
bash /home/pyomo/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
test.pyomo -v --cat=nightly pyomo ./pyomo-model-libraries

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
test.pyomo -v --cat=nightly pyomo ./pyomo-model-libraries

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
test.pyomo -v --cat=nightly pyomo ./pyomo-model-libraries

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
FROM python:3.8-slim

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
RUN git clone https://github.com/Pyomo/pyomo.git /home/pyomo

WORKDIR /home/pyomo
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Pyomo", "pyomo_5_6")
class PYOMO_5_6(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re
        import json
        # Improved log parsing logic
        # Strict regex for main test result lines: test_name (module.class) ... status
        main_line_pattern = re.compile(r'^(?P<name>.+? \([^)]+\))\s*\.\.\. (?P<status>ok|SKIP:.*|ERROR|FAIL)$')
        # Summary section regex: ERROR: test_name (module.class)
        summary_pattern = re.compile(r'^(ERROR|FAIL): (?P<name>.+? \([^)]+\))')
        in_summary = False
        for line in log.splitlines():
            # Detect start of summary section
            if line.startswith("==========") or line.startswith("FAILED ("):
                in_summary = True
                continue
            if not in_summary:
                m = main_line_pattern.match(line)
                if m:
                    name = m.group('name').strip()
                    status = m.group('status')
                    if status == 'ok':
                        passed_tests.add(name)
                    elif status.startswith('SKIP'):
                        skipped_tests.add(name)
                    elif status in ('ERROR', 'FAIL'):
                        failed_tests.add(name)
            else:
                m2 = summary_pattern.match(line)
                if m2:
                    name = m2.group('name').strip()
                    failed_tests.add(name)
        # Remove any overlaps (should not happen, but just in case)
        passed_tests -= (failed_tests | skipped_tests)
        skipped_tests -= (failed_tests | passed_tests)
        failed_tests -= (passed_tests | skipped_tests)
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
