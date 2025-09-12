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
        return "ubuntu:latest"
    
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
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y
###ACTION_DELIMITER###
apt-get install -y python3.6 python3.6-dev python3.6-venv
###ACTION_DELIMITER###
apt-get install -y python3.7 python3.7-dev python3.7-venv
###ACTION_DELIMITER###
python3.7 -m venv venv
###ACTION_DELIMITER###
venv/bin/pip install -e ".[dev]"
###ACTION_DELIMITER###
sed -i 's/"black"/"black==21.12b0"/' setup.py
###ACTION_DELIMITER###
venv/bin/pip install -e ".[dev]"
###ACTION_DELIMITER###
sed -i 's/mypy >= 0.600, < 0.700/mypy >= 0.900/' requirements.txt
###ACTION_DELIMITER###
venv/bin/pip install -e ".[dev]"
###ACTION_DELIMITER###
echo 'venv/bin/pytest -v -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'venv/bin/pytest -vv -rA -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install -e ".[dev,templates]"
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls src/prefect/tasks/templates/
###ACTION_DELIMITER###
venv/bin/pip install 'jinja2>=2.0,<3.0'
###ACTION_DELIMITER###
echo 'from prefect.tasks.templates import JinjaTemplateTask; print("Success")' > test_import.py && venv/bin/python test_import.py
###ACTION_DELIMITER###
sed -i 's/try:/# try:/' src/prefect/tasks/templates/__init__.py && sed -i 's/from prefect.tasks.templates.jinja2 import JinjaTemplateTask/# from prefect.tasks.templates.jinja2 import JinjaTemplateTask/' src/prefect/tasks/templates/__init__.py && sed -i 's/except ImportError:/# except ImportError:/' src/prefect/tasks/templates/__init__.py && sed -i 's/pass/# pass/' src/prefect/tasks/templates/__init__.py && echo 'from prefect.tasks.templates.jinja2 import JinjaTemplateTask' >> src/prefect/tasks/templates/__init__.py
###ACTION_DELIMITER###
venv/bin/python test_import.py
###ACTION_DELIMITER###
venv/bin/pip install markupsafe==1.1.1
###ACTION_DELIMITER###
venv/bin/python test_import.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'venv/bin/pytest -v -rA --tb=no -p no:cacheprovider -n auto tests/' > test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
venv/bin/pytest -v -rA --tb=no -p no:cacheprovider -n auto tests/

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
venv/bin/pytest -v -rA --tb=no -p no:cacheprovider -n auto tests/

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
venv/bin/pytest -v -rA --tb=no -p no:cacheprovider -n auto tests/

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:latest with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:latest

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
RUN git clone https://github.com/PrefectHQ/prefect.git /home/prefect

WORKDIR /home/prefect
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("PrefectHQ", "prefect_557_to_532")
class PREFECT_557_TO_532(Instance):
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
        # Regex pattern to match test status lines
        pattern = r'\[gw\d+\] \[\s*\d+%\] (\w+) (tests/.*)'
        matches = re.findall(pattern, log)
        for status, test_name in matches:
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
