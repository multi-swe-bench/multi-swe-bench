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
                """ls -la
###ACTION_DELIMITER###
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH"
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.8
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl
###ACTION_DELIMITER###
git clone https://github.com/pyenv/pyenv.git ~/.pyenv && export PYENV_ROOT="$HOME/.pyenv" && export PATH="$PYENV_ROOT/bin:$PATH" && eval "$(pyenv init -)"
###ACTION_DELIMITER###
pyenv install 3.8.18
###ACTION_DELIMITER###
pyenv local 3.8.18
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
eval "$(pyenv init -)" && python --version && poetry env use 3.8.18
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
eval "$(pyenv init -)" && make install
###ACTION_DELIMITER###
poetry env use /root/.pyenv/versions/3.8.18/bin/python && poetry install
###ACTION_DELIMITER###
ls -la .python-version && poetry env use /root/.pyenv/versions/3.8.18/bin/python && poetry env info && poetry install
###ACTION_DELIMITER###
rm -rf /root/.cache/pypoetry/virtualenvs/rasa-hmJQ5vQ6-py3.8 && poetry env use /root/.pyenv/versions/3.8.18/bin/python && poetry install
###ACTION_DELIMITER###
pyenv version && python --version && poetry env use $(pyenv which python) && poetry install
###ACTION_DELIMITER###
poetry cache clear --all pypi && rm -rf /root/.cache/pypoetry/virtualenvs/rasa-hmJQ5vQ6-py3.8 && poetry env use /root/.pyenv/versions/3.8.18/bin/python && poetry install
###ACTION_DELIMITER###
export POETRY_PYTHON=$(pyenv which python) && rm -rf /root/.cache/pypoetry/virtualenvs/rasa-hmJQ5vQ6-py3.8 && poetry env use $(pyenv which python) && poetry install
###ACTION_DELIMITER###
python -m venv .venv && source .venv/bin/activate && poetry install
###ACTION_DELIMITER###
source .venv/bin/activate && pip install setuptools>=41.0.0 && poetry install
###ACTION_DELIMITER###
/root/.pyenv/versions/3.8.18/bin/python -m venv .venv && source .venv/bin/activate && pip install setuptools>=41.0.0 && poetry install
###ACTION_DELIMITER###
eval "$(pyenv init -)" && pyenv local 3.8.18 && rm -rf .venv /root/.cache/pypoetry/virtualenvs/* && poetry env use $(pyenv which python) && poetry install --no-root
###ACTION_DELIMITER###
rm -rf /root/.cache/pypoetry/virtualenvs/rasa-hmJQ5vQ6-py3.8 && export PATH="/root/.pyenv/shims:$PATH" && poetry env use 3.8.18 && poetry install
###ACTION_DELIMITER###
rm -rf .venv && /root/.pyenv/versions/3.8.18/bin/python -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install setuptools>=41.0.0 && poetry install
###ACTION_DELIMITER###
rm -f poetry.lock && source .venv/bin/activate && poetry install --no-lock
###ACTION_DELIMITER###
rm -f poetry.lock && source .venv/bin/activate && poetry install
###ACTION_DELIMITER###
sed -i '/types-pkg-resources/d' pyproject.toml && poetry install
###ACTION_DELIMITER###
echo 'OMP_NUM_THREADS=1 TF_CPP_MIN_LOG_LEVEL=2 poetry run pytest -v tests --cov rasa' > test_commands.sh
###ACTION_DELIMITER###
echo 'OMP_NUM_THREADS=1 TF_CPP_MIN_LOG_LEVEL=2 poetry run pytest -v -rA tests --cov rasa' > test_commands.sh
###ACTION_DELIMITER###
echo 'OMP_NUM_THREADS=1 TF_CPP_MIN_LOG_LEVEL=2 poetry run pytest -v -rA -n auto tests --cov rasa' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
OMP_NUM_THREADS=1 TF_CPP_MIN_LOG_LEVEL=2 poetry run pytest -v -rA -n auto tests --cov rasa

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
OMP_NUM_THREADS=1 TF_CPP_MIN_LOG_LEVEL=2 poetry run pytest -v -rA -n auto tests --cov rasa

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
OMP_NUM_THREADS=1 TF_CPP_MIN_LOG_LEVEL=2 poetry run pytest -v -rA -n auto tests --cov rasa

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
RUN git clone https://github.com/RasaHQ/rasa.git /home/rasa

WORKDIR /home/rasa
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("RasaHQ", "rasa_9118_to_unknown")
class RASA_9118_TO_UNKNOWN(Instance):
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
        all_tests: set[str] = set()  # All tests found in the log
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        lines = log.split('\n')
        for line in lines:
            content = line.strip()
            if not content:
                continue
            # Extract test name if present
            test_match = re.search(r'(tests/[^:]+::test_\w+(?:\[.*?\])?)', content)
            if test_match:
                test_name = test_match.group(1)
                all_tests.add(test_name)
                # Check if this line indicates failure
                if 'FAILED' in content:
                    failed_tests.add(test_name)
                # Check if this line indicates skipped
                elif 'SKIPPED' in content:
                    skipped_tests.add(test_name)
        # Compute passed tests as all tests not failed or skipped
        passed_tests = all_tests - failed_tests - skipped_tests
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
