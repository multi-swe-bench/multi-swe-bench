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
                """ls -al
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.9 python3.9-venv python3.9-dev
###ACTION_DELIMITER###
pip install git+https://github.com/nose-devs/nose.git
###ACTION_DELIMITER###
pip install .[tests]
###ACTION_DELIMITER###
pyomo download-extensions
###ACTION_DELIMITER###
pyomo build-extensions
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential cmake
###ACTION_DELIMITER###
pyomo build-extensions
###ACTION_DELIMITER###
echo 'python -m pyomo.common.unittest pyomo -v --cat=nightly --xunit' > /home/pyomo/test_commands.sh
###ACTION_DELIMITER###
bash /home/pyomo/test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y nose
###ACTION_DELIMITER###
pip install git+https://github.com/nose-devs/nose.git
###ACTION_DELIMITER###
bash /home/pyomo/test_commands.sh
###ACTION_DELIMITER###
find /usr/local/lib/python3.10/site-packages/nose -name core.py
###ACTION_DELIMITER###
sed -i 's/print "%s version %s" % (os.path.basename(sys.argv[0]), __version__)/print("%s version %s" % (os.path.basename(sys.argv[0]), __version__))/g' /usr/local/lib/python3.10/site-packages/nose/core.py
###ACTION_DELIMITER###
bash /home/pyomo/test_commands.sh
###ACTION_DELIMITER###
sed -i -E "s/print ([^"]*)"/print(\1)/g" /usr/local/lib/python3.10/site-packages/nose/core.py
###ACTION_DELIMITER###
sed -i "153s/print \"%s version %s\" % (os.path.basename(sys.argv[0]), __version__)/print(f'{os.path.basename(sys.argv[0])} version {__version__}')/" /usr/local/lib/python3.10/site-packages/nose/core.py
###ACTION_DELIMITER###
bash /home/pyomo/test_commands.sh
###ACTION_DELIMITER###
2to3 -w /usr/local/lib/python3.10/site-packages/nose/core.py
###ACTION_DELIMITER###
bash /home/pyomo/test_commands.sh
###ACTION_DELIMITER###
2to3 -w /usr/local/lib/python3.10/site-packages/nose
###ACTION_DELIMITER###
bash /home/pyomo/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python -m pyomo.common.unittest pyomo -v --cat=nightly --xunit

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
python -m pyomo.common.unittest pyomo -v --cat=nightly --xunit

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
python -m pyomo.common.unittest pyomo -v --cat=nightly --xunit

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
RUN git clone https://github.com/Pyomo/pyomo.git /home/pyomo

WORKDIR /home/pyomo
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Pyomo", "pyomo_6_1_2")
class PYOMO_6_1_2(Instance):
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
            # Improved regex: only match lines like test_name (module.class) ... STATUS
        result_re = re.compile(r'^(?P<test_name>\w+) \((?P<test_class>[\w\.]+)\) \.\.\. (?P<status>ok|FAIL|SKIP)(:.*)?$')
        # Status precedence: failed > skipped > passed
        status_order = {'failed_tests': 2, 'skipped_tests': 1, 'passed_tests': 0}
        test_status = {}
        for line in log.splitlines():
            m = result_re.match(line)
            if m:
                test_id = f"{m.group('test_class')}.{m.group('test_name')}"
                status = m.group('status')
                if status == 'ok':
                    s = 'passed_tests'
                elif status == 'FAIL':
                    s = 'failed_tests'
                elif status == 'SKIP':
                    s = 'skipped_tests'
                # Only upgrade status if new status is more severe
                if test_id not in test_status or status_order[s] > status_order[test_status[test_id]]:
                    test_status[test_id] = s
        # Assign each test to only one set based on its final status
        failed_tests = set()
        skipped_tests = set()
        passed_tests = set()
        for k, v in test_status.items():
            if v == 'failed_tests':
                failed_tests.add(k)
            elif v == 'skipped_tests':
                skipped_tests.add(k)
            elif v == 'passed_tests':
                passed_tests.add(k)
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
