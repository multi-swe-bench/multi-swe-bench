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
python3 --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip python3-dev
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH"
###ACTION_DELIMITER###
poetry install
###ACTION_DELIMITER###
apt-get install -y libffi-dev
###ACTION_DELIMITER###
poetry install
###ACTION_DELIMITER###
poetry run pip install cython
###ACTION_DELIMITER###
sed -i 's/pyyaml = "^5"/pyyaml = "^6.0.1"/' pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
sed -i 's/troposphere = "^2.4"/troposphere = ">=3.0.0"/' pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
echo 'poetry run pytest -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pytest = "^6.2"/pytest = "^7.4"/' pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/\[tool.poetry.dev-dependencies\]/a py = "^1.11.0"' pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
sed -i '/\[tool.poetry.dev-dependencies\]/a apipkg = "^3.0.0"' pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
sed -i 's/py = "^1.11.0"/py = "^1.12.0"/' pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
rm -rf .venv && poetry install
###ACTION_DELIMITER###
poetry lock && poetry install
###ACTION_DELIMITER###
sed -i 's/py = "^1.12.0"/py = "^1.11.0"/' pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
sed -i '/apipkg = "^3.0.0"/d' pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
sed -i 's/\[tool.poetry.dev-dependencies\]/\[tool.poetry.group.dev.dependencies\]/' pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
sed -i 's/py = "^1.11.0"/py = "^1.12.0"/' pyproject.toml && rm -f poetry.lock && poetry lock && poetry install
###ACTION_DELIMITER###
sed -i 's/py = "^1.12.0"/py = "^1.11.0"/' pyproject.toml && rm -f poetry.lock && poetry lock && poetry install
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/jinja2 = "^2.7"/jinja2 = "^3.0"/' pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/\[tool.poetry.group.dev.dependencies\]/a testfixtures = "^6.18.0"' pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
sed -i 's/testfixtures = ".*"/testfixtures = "^6.18.0"/' pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
sed -i -e '/\[tool.poetry.group.dev.dependencies\]/,/^\[.*\]/ s/^testfixtures = .*//' -e '/\[tool.poetry.group.dev.dependencies\]/a testfixtures = "^6.18.0"' pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/moto = { version = "^2.0"/moto = { version = "^4.0"/' pyproject.toml && poetry lock && poetry install
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
poetry run pytest -v

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
poetry run pytest -v

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
poetry run pytest -v

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
RUN git clone https://github.com/onicagroup/runway.git /home/runway

WORKDIR /home/runway
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("onicagroup", "runway_831_to_unknown")
class RUNWAY_831_TO_UNKNOWN(Instance):
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
        # Permissive regex with positive lookahead
        passed_pattern = re.compile(r'(tests/.+?)(?=\s+PASSED)', re.MULTILINE)
        failed_pattern = re.compile(r'(tests/.+?)(?=\s+FAILED)', re.MULTILINE)
        error_pattern = re.compile(r'ERROR\s+(tests/.+?)(?=\s+-)', re.MULTILINE)
        skipped_pattern = re.compile(r'(tests/.+?)(?=\s+SKIPPED)', re.MULTILINE)
        # Extract test names for each status
        passed_tests = set(passed_pattern.findall(log))
        failed_tests = set(failed_pattern.findall(log))
        error_tests = set(error_pattern.findall(log))
        skipped_tests = set(skipped_pattern.findall(log))
        # Combine error tests into failed_tests
        failed_tests.update(error_tests)
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
