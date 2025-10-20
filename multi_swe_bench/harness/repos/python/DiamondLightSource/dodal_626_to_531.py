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
                """ls
###ACTION_DELIMITER###
pip show ophyd-async
###ACTION_DELIMITER###
pip install 'ophyd-async>=0.3.1'
###ACTION_DELIMITER###
python --version
###ACTION_DELIMITER###
cat /etc/os-release
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.11 python3.11-pip
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.11
###ACTION_DELIMITER###
python3.11 -m ensurepip --upgrade
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.11-venv
###ACTION_DELIMITER###
python3.11 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install -e ".[dev]"
###ACTION_DELIMITER###
echo -e '#!/bin/bash
venv/bin/pytest --no-header -rA' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip show ophyd-async && ls -l venv/lib/python3.11/site-packages/ophyd_async/
###ACTION_DELIMITER###
venv/bin/pip uninstall -y ophyd-async && venv/bin/pip install 'ophyd-async==0.3.1'
###ACTION_DELIMITER###
find venv/lib/python3.11/site-packages/ophyd_async/ -name 'panda*'
###ACTION_DELIMITER###
ls -l venv/lib/python3.11/site-packages/ophyd_async/panda
###ACTION_DELIMITER###
cat venv/lib/python3.11/site-packages/ophyd_async/panda/__init__.py
###ACTION_DELIMITER###
venv/bin/python -c "from ophyd_async.panda import HDFPanda; print('Import successful')"
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
venv/bin/pytest --no-header -rA

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
venv/bin/pytest --no-header -rA

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
venv/bin/pytest --no-header -rA

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
RUN git clone https://github.com/DiamondLightSource/dodal.git /home/dodal

WORKDIR /home/dodal
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("DiamondLightSource", "dodal_626_to_531")
class DODAL_626_TO_531(Instance):
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
        # Regex patterns to match test names and their statuses
        passed_pattern = re.compile(r'(tests/[\w/:.[\]()\-]+)\s+PASSED')
        failed_pattern = re.compile(r'FAILED\s+(tests/[\w/:.[\]()\-]+)')
        skipped_pattern = re.compile(r'(tests/[\w/:.[\]()\-]+)\s+SKIPPED|SKIPPED\s+(tests/[\w/:.[\]()\-]+)')
        for line in log.splitlines():
            # Check for passed tests
            passed_match = passed_pattern.search(line)
            if passed_match:
                test_name = passed_match.group(1)
                passed_tests.add(test_name)
            # Check for failed tests
            failed_match = failed_pattern.search(line)
            if failed_match:
                test_name = failed_match.group(1)
                failed_tests.add(test_name)
            # Check for skipped tests
            skipped_match = skipped_pattern.search(line)
            if skipped_match:
                # Determine which group matched
                test_name = skipped_match.group(1) if skipped_match.group(1) else skipped_match.group(2)
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
