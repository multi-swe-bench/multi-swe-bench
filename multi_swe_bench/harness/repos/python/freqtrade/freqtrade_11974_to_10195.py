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
        return "python:3.10-slim-bullseye"
    
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
                """python3 --version; python3.11 --version
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python3.11 python3.11-venv python3.11-dev -t bullseye-backports
###ACTION_DELIMITER###
sed -i '/bullseye-backports/d' /etc/apt/sources.list && echo 'deb [trusted=yes] http://archive.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python3.11 python3.11-venv python3.11-dev -t bullseye-backports
###ACTION_DELIMITER###
sed -i '/bullseye-backports/d' /etc/apt/sources.list && echo 'deb [trusted=yes] http://archive.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python3.11 -t bullseye-backports
###ACTION_DELIMITER###
python3.11 --version || echo 'Python 3.11 not found'
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl
###ACTION_DELIMITER###
git clone https://github.com/pyenv/pyenv.git ~/.pyenv && export PYENV_ROOT="$HOME/.pyenv" && export PATH="$PYENV_ROOT/bin:$PATH" && eval "$(pyenv init -)"
###ACTION_DELIMITER###
export PYENV_ROOT="$HOME/.pyenv" && export PATH="$PYENV_ROOT/bin:$PATH" && eval "$(pyenv init -)" && pyenv install 3.11.0 && pyenv local 3.11.0
###ACTION_DELIMITER###
yes | ./setup.sh --install
###ACTION_DELIMITER###
. .venv/bin/activate && python --version && deactivate
###ACTION_DELIMITER###
echo -e '#!/bin/bash
.venv/bin/pytest -v tests/' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
.venv/bin/pytest -v tests/

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
.venv/bin/pytest -v tests/

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
.venv/bin/pytest -v tests/

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
FROM python:3.10-slim-bullseye

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
RUN git clone https://github.com/freqtrade/freqtrade.git /home/freqtrade

WORKDIR /home/freqtrade
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("freqtrade", "freqtrade_11974_to_10195")
class FREQTRADE_11974_TO_10195(Instance):
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
        # Pattern for detailed test lines (handles line numbers, test name, and status)
        detailed_pattern = re.compile(r'^(?:\[\s*\d+\]\s+)?(tests/[^\s]+)\s+(PASSED|FAILED|SKIPPED)\s+.*', re.MULTILINE | re.IGNORECASE)
        matches = detailed_pattern.findall(log)
        for test_name, status in matches:
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
        # Pattern for summary failed tests (handles optional trailing content)
        summary_failed_pattern = re.compile(r'^(?:\[\s*\d+\]\s+)?FAILED\s+(tests/[^ ]+)(?: - .*)?$', re.MULTILINE)
        failed_matches = summary_failed_pattern.findall(log)
        for test_name in failed_matches:
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
