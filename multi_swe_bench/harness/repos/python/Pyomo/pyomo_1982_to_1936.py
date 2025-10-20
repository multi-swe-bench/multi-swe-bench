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
                """ls .github/workflows
###ACTION_DELIMITER###
apt-get update && apt-get install -y libopenblas-dev gfortran liblapack-dev glpk-utils
###ACTION_DELIMITER###
pip install -e . numpy scipy parameterized sphinx pytest pytest-sphinx sphinx-testing pymysql pyodbc
###ACTION_DELIMITER###
pip install git+https://github.com/PyUtilib/pyutilib.git
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install parameterized pytest-sphinx sphinx-testing
###ACTION_DELIMITER###
pip install scipy numpy
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest-nose
###ACTION_DELIMITER###
echo -e '#!/bin/bash
python setup.py test -v' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pytest -v --no-header -rA --tb=no -p no:cacheprovider --ignore=pyomo/common/tests/dep_mod_except.py' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pytest -v --no-header -rA --tb=no -p no:cacheprovider --ignore=pyomo/common/tests/dep_mod_except.py --ignore=doc/OnlineDocs/tests/test_examples.py' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.26.4
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libasl-dev && echo -e '#!/bin/bash
pytest -v --no-header -rA --tb=no -p no:cacheprovider --ignore=pyomo/common/tests/dep_mod_except.py --ignore=doc/OnlineDocs/tests/test_examples.py' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
pip install appsi && echo -e '#!/bin/bash
pytest -v --no-header -rA --tb=no -p no:cacheprovider --ignore=pyomo/common/tests/dep_mod_except.py --ignore=doc/OnlineDocs/tests/test_examples.py' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pytest -v --no-header -rA --tb=no -p no:cacheprovider --ignore=pyomo/common/tests/dep_mod_except.py --ignore=doc/OnlineDocs/tests/test_examples.py --ignore=pyomo/contrib/appsi' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
pytest -v --no-header -rA --tb=no -p no:cacheprovider --ignore=pyomo/common/tests/dep_mod_except.py --ignore=doc/OnlineDocs/tests/test_examples.py --ignore=pyomo/contrib/appsi

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
#!/bin/bash
pytest -v --no-header -rA --tb=no -p no:cacheprovider --ignore=pyomo/common/tests/dep_mod_except.py --ignore=doc/OnlineDocs/tests/test_examples.py --ignore=pyomo/contrib/appsi

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
#!/bin/bash
pytest -v --no-header -rA --tb=no -p no:cacheprovider --ignore=pyomo/common/tests/dep_mod_except.py --ignore=doc/OnlineDocs/tests/test_examples.py --ignore=pyomo/contrib/appsi

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim with actual base image
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
RUN git clone https://github.com/Pyomo/pyomo.git /home/pyomo

WORKDIR /home/pyomo
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Pyomo", "pyomo_1982_to_1936")
class PYOMO_1982_TO_1936(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re
        import json
        # TODO: Implement the parse_log function
        # Implement the log parsing logic here
        # Regex pattern to match test lines with status
        pattern = r'^(?:\[.*?\]\s*)?(?:(PASSED|FAILED|SKIPPED|XFAIL)\s+(.*?)|(.*?)\s+(PASSED|FAILED|SKIPPED|XFAIL))(?:\s+\[.*?\]|\s+-.*?)?$'
        for line in log.split('\n'):
            line = line.strip()
            if not line:
                continue
            match = re.match(pattern, line)
            if match:
                status1, test1, test2, status2 = match.groups()
                if status1:
                    status = status1.upper()
                    test_name = test1.strip()
                else:
                    status = status2.upper()
                    test_name = test2.strip()
                # Add to the appropriate set
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
                elif status == 'XFAIL':
                    # Assuming XFAIL is a type of failure
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
