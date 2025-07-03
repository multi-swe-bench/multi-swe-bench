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
ls -al scripts
###ACTION_DELIMITER###
ls -al pyomo
###ACTION_DELIMITER###
find pyomo -maxdepth 2 -type d -name 'test*'
###ACTION_DELIMITER###
ls -al pyomo/core/tests
###ACTION_DELIMITER###
ls -al pyomo/core/tests/unit
###ACTION_DELIMITER###
apt-get update && apt-get install -y gfortran
###ACTION_DELIMITER###
pip install -e . coverage codecov xlrd openpyxl sphinx_rtd_theme git+https://github.com/PyUtilib/pyutilib
###ACTION_DELIMITER###
echo 'test.pyomo -v pyomo' > /home/pyomo/test_commands.sh
###ACTION_DELIMITER###
bash /home/pyomo/test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y PyUtilib && pip install 'PyUtilib<6.0'
###ACTION_DELIMITER###
bash /home/pyomo/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
test.pyomo -v pyomo

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
test.pyomo -v pyomo

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
test.pyomo -v pyomo

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
RUN git clone https://github.com/Pyomo/pyomo.git /home/pyomo

WORKDIR /home/pyomo
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Pyomo", "pyomo_5_3")
class PYOMO_5_3(Instance):
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

        # Improved parser: Only the last status for each test counts, and use full identifier for uniqueness.
        from collections import OrderedDict
        import re
        # Regex to match test result lines
        # Example: test_name (module.path.ClassName) ... ok
        test_line_re = re.compile(r'^(.*?) \((.*?)\) \.\.\. (ok|SKIP:.*|ERROR|FAIL)', re.MULTILINE)
        test_status = OrderedDict()  # key: full test id, value: status
        for match in test_line_re.finditer(log):
            test_func = match.group(1).strip()
            test_class = match.group(2).strip()
            status = match.group(3)
            # Use full identifier for uniqueness
            test_id = f"{test_func} ({test_class})"
            if status == 'ok':
                test_status[test_id] = 'passed'
            elif status.startswith('SKIP'):
                test_status[test_id] = 'skipped'
            elif status in ('ERROR', 'FAIL'):
                test_status[test_id] = 'failed'
        # Now split into sets
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        for test_id, status in test_status.items():
            if status == 'passed':
                passed_tests.add(test_id)
            elif status == 'failed':
                failed_tests.add(test_id)
            elif status == 'skipped':
                skipped_tests.add(test_id)
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
