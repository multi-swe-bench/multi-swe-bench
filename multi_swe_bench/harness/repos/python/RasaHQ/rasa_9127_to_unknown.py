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
                """ls /home/rasa
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
###ACTION_DELIMITER###
apt-get install -y curl python3
###ACTION_DELIMITER###
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH"
###ACTION_DELIMITER###
poetry --version
###ACTION_DELIMITER###
cat Makefile
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
apt-get install -y make
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
apt-get install -y python3.8
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.8
###ACTION_DELIMITER###
poetry env use python3.8
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
poetry run python --version
###ACTION_DELIMITER###
which python3.8
###ACTION_DELIMITER###
poetry env use /usr/bin/python3.8
###ACTION_DELIMITER###
poetry run python --version
###ACTION_DELIMITER###
poetry env list
###ACTION_DELIMITER###
poetry env remove python3.8 && poetry env use /usr/bin/python3.8
###ACTION_DELIMITER###
poetry run python --version
###ACTION_DELIMITER###
source /root/.cache/pypoetry/virtualenvs/rasa-hmJQ5vQ6-py3.8/bin/activate && python --version
###ACTION_DELIMITER###
python3.8 -m venv .venv && source .venv/bin/activate && poetry install
###ACTION_DELIMITER###
apt-get install -y python3.8-venv
###ACTION_DELIMITER###
python3.8 -m venv .venv && source .venv/bin/activate && poetry install
###ACTION_DELIMITER###
source .venv/bin/activate && pip install --upgrade pip setuptools && poetry install
###ACTION_DELIMITER###
source .venv/bin/activate && poetry update
###ACTION_DELIMITER###
source .venv/bin/activate && rm -f poetry.lock && poetry install
###ACTION_DELIMITER###
sed -i 's/types-pkg-resources = "^0.1.3"/# types-pkg-resources = "^0.1.3"/' /home/rasa/pyproject.toml
###ACTION_DELIMITER###
source .venv/bin/activate && poetry install
###ACTION_DELIMITER###
echo -e '#!/bin/bash
source .venv/bin/activate
poetry run pytest -v tests/' > /home/rasa/test_commands.sh
###ACTION_DELIMITER###
chmod +x /home/rasa/test_commands.sh
###ACTION_DELIMITER###
cat /home/rasa/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/poetry run pytest -v tests//poetry run pytest -v -n auto tests//' /home/rasa/test_commands.sh
###ACTION_DELIMITER###
sed -i 's|pytest -v tests/|pytest -v -n auto tests/|' /home/rasa/test_commands.sh
###ACTION_DELIMITER###
cat /home/rasa/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
source .venv/bin/activate
poetry run pytest -v -n auto tests/

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
#!/bin/bash
source .venv/bin/activate
poetry run pytest -v -n auto tests/

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
#!/bin/bash
source .venv/bin/activate
poetry run pytest -v -n auto tests/

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
RUN git clone https://github.com/RasaHQ/rasa.git /home/rasa

WORKDIR /home/rasa
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("RasaHQ", "rasa_9127_to_unknown")
class RASA_9127_TO_UNKNOWN(Instance):
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
        # Regex patterns to match test statuses
        passed_pattern = re.compile(r"PASSED (tests/.*)$")
        failed_pattern = re.compile(r"(FAILED|ERROR) (tests/.*)$")
        skipped_pattern = re.compile(r"SKIPPED (tests/.*)$")
        # Iterate through each line in the log
        for line in log.split('\n'):
            # Check for passed tests
            passed_match = passed_pattern.search(line)
            if passed_match:
                test_name = passed_match.group(1).strip()
                passed_tests.add(test_name)
            # Check for failed tests
            failed_match = failed_pattern.search(line)
            if failed_match:
                test_name = failed_match.group(2).strip()
                failed_tests.add(test_name)
            # Check for skipped tests
            skipped_match = skipped_pattern.search(line)
            if skipped_match:
                test_name = skipped_match.group(1).strip()
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
