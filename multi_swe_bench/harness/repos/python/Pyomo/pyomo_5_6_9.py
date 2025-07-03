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
        return "python:3.8"
    
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
pip install -U pip setuptools wheel
###ACTION_DELIMITER###
pip install --quiet git+https://github.com/PyUtilib/pyutilib
###ACTION_DELIMITER###
python setup.py develop
###ACTION_DELIMITER###
pyomo download-extensions
###ACTION_DELIMITER###

###ACTION_DELIMITER###
pip uninstall -y pyutilib
###ACTION_DELIMITER###
pip install pyutilib==5.8.0
###ACTION_DELIMITER###
pip install pyutilib==5.8.1
###ACTION_DELIMITER###
pip install --upgrade --force-reinstall --no-cache-dir git+https://github.com/PyUtilib/pyutilib@5.8
###ACTION_DELIMITER###
git ls-remote https://github.com/PyUtilib/pyutilib.git
###ACTION_DELIMITER###
pip install --upgrade --force-reinstall --no-cache-dir git+https://github.com/PyUtilib/pyutilib@8509a555567f9944d65a4061fdf86841c9ed4250
###ACTION_DELIMITER###
pyomo download-extensions
###ACTION_DELIMITER###
sed -i 's/PyUtilib>=5.8.1.dev0/PyUtilib>=5.8.0/' setup.py
###ACTION_DELIMITER###
python setup.py develop
###ACTION_DELIMITER###
pyomo download-extensions
###ACTION_DELIMITER###
pyomo build-extensions
###ACTION_DELIMITER###
apt-get update && apt-get install -y cmake
###ACTION_DELIMITER###
pyomo build-extensions
###ACTION_DELIMITER###
echo 'test.pyomo -v --cat=nightly pyomo' > /home/pyomo/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
test.pyomo -v --cat=nightly pyomo

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
test.pyomo -v --cat=nightly pyomo

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
test.pyomo -v --cat=nightly pyomo

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
FROM python:3.8

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


@Instance.register("Pyomo", "pyomo_5_6_9")
class PYOMO_5_6_9(Instance):
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
        def status_rank(status):
                if status in ('FAIL', 'ERROR'):
                    return 3
                elif status.startswith('SKIP:'):
                    return 2
                elif status == 'ok':
                    return 1
                return 0
        # Parse the log content and extract test execution results.
        passed_tests = set() # Tests that passed successfully
        failed_tests = set() # Tests that failed
        skipped_tests = set() # Tests that were skipped
        import re
        import json
            # Regular expression to match test result lines
        # Example: test_name (module.path.ClassName) ... ok
        test_line_re = re.compile(r'^(\S+) \([^)]+\) \.\.\. (ok|FAIL|ERROR|SKIP: .*)$')
        # Track the worst status for each test
        test_status = {}
        # Severity order: failed > skipped > passed
        def status_rank(status):
            if status in ('FAIL', 'ERROR'):
                return 3
            elif status.startswith('SKIP:'):
                return 2
            elif status == 'ok':
                return 1
            return 0
        for line in log.splitlines():
            m = test_line_re.match(line)
            if m:
                test_name, status = m.group(1), m.group(2)
                # Only keep the most severe status for each test
                prev = test_status.get(test_name)
                if prev is None or status_rank(status) > status_rank(prev):
                    test_status[test_name] = status
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        for test, status in test_status.items():
            if status in ('FAIL', 'ERROR'):
                failed_tests.add(test)
            elif status.startswith('SKIP:'):
                skipped_tests.add(test)
            elif status == 'ok':
                passed_tests.add(test)
        # End of improved parsing logic
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
