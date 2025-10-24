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
        repo_name = self.pr.repo
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
python --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.8 python3.8-venv python3.8-dev
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye-backports main' > /etc/apt/sources.list.d/backports.list && apt-get update
###ACTION_DELIMITER###
echo 'deb http://archive.debian.org/debian bullseye-backports main' > /etc/apt/sources.list.d/backports.list && apt-get update -o Acquire::Check-Valid-Until=false
###ACTION_DELIMITER###
apt-get install -y python3.8 python3.8-venv python3.8-dev -t bullseye-backports
###ACTION_DELIMITER###
apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl
###ACTION_DELIMITER###
git clone https://github.com/pyenv/pyenv.git ~/.pyenv && export PYENV_ROOT="$HOME/.pyenv" && export PATH="$PYENV_ROOT/bin:$PATH" && eval "$(pyenv init -)" && pyenv install 3.8.18 && pyenv local 3.8.18
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 - && poetry env use 3.8.18
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3.8 - --version 1.1.15
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH" && poetry install
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH" && poetry run pip install --upgrade setuptools
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH" && poetry run pip install setuptools==58.0.0
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH" && poetry install
###ACTION_DELIMITER###
apt-get install -y postgresql
###ACTION_DELIMITER###
pg_ctlcluster 13 main start && su postgres -c 'createuser -s saleor' && su postgres -c 'createdb -O saleor saleor'
###ACTION_DELIMITER###
export SECRET_KEY=$(poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())") && poetry run python manage.py migrate
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH" && poetry add celery@^4.3.0
###ACTION_DELIMITER###
sed -i 's/codecov = "^2.0.15"/codecov = "^2.1.12"/' pyproject.toml
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH" && poetry install
###ACTION_DELIMITER###
rm poetry.lock && export PATH="/root/.local/bin:$PATH" && poetry install
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH" && poetry run python manage.py migrate
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH" && poetry add celery@^4.3.0
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH" && poetry run pip install pip==20.2 && poetry add celery@^4.3.0
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH" && poetry run pip list | grep celery && poetry run python manage.py migrate
###ACTION_DELIMITER###
apt-get install -y libmagic1
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH" && poetry add python-magic && poetry run python manage.py migrate
###ACTION_DELIMITER###
sed -i 's/peer/trust/g' /etc/postgresql/13/main/pg_hba.conf && sed -i 's/md5/trust/g' /etc/postgresql/13/main/pg_hba.conf && pg_ctlcluster 13 main restart && export SECRET_KEY=$(poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())") && poetry run python manage.py migrate
###ACTION_DELIMITER###
echo 'poetry run python manage.py test --verbosity 2' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i '48i PATTERNS_IGNORED_IN_QUERY_CAPTURES = []' saleor/settings.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
export SECRET_KEY=$(poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())") && poetry run python manage.py test --verbosity 2 --keepdb
###ACTION_DELIMITER###
echo 'poetry run pytest --verbosity=2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'export SECRET_KEY=$(poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())") && poetry run python manage.py test --verbosity 2 --testrunner django.test.runner.DiscoverRunner' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'export SECRET_KEY=$(poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())") && poetry run python manage.py test tests/ saleor/ --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'export SECRET_KEY=$(poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())") && poetry run pytest -n 1 --verbosity=2 tests/ saleor/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'export SECRET_KEY=$(poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
export DATABASE_URL="postgres://saleor@localhost:5432/saleor_test"
poetry run python manage.py test --verbosity 2 --keepdb' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'export SECRET_KEY=$(poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())") && poetry run pytest --verbosity=2 tests/ saleor/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'export SECRET_KEY=$(poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())") && poetry run python manage.py test --verbosity 2' > test_commands.sh && bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
export SECRET_KEY=$(poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())") && poetry run python manage.py test --verbosity 2

""".replace("[[REPO_NAME]]", repo_name),
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
export SECRET_KEY=$(poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())") && poetry run python manage.py test --verbosity 2

""".replace("[[REPO_NAME]]", repo_name),
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
export SECRET_KEY=$(poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())") && poetry run python manage.py test --verbosity 2

""".replace("[[REPO_NAME]]", repo_name),
            ),
        ]

    def dockerfile(self) -> str:
        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        dockerfile_content = """
# This is a template for creating a Dockerfile to test patches
# LLM should fill in the appropriate values based on the context

# Choose an appropriate base image based on the project's requirements - replace python:3.10-slim-bullseye with actual base image
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
RUN git clone https://github.com/saleor/saleor.git /home/saleor

WORKDIR /home/saleor
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("saleor", "saleor_5075_to_5072")
class SALEOR_5075_TO_5072(Instance):
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

        return "bash /home/run.sh"

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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        import json

        # TODO: Implement the parse_log function
        # Implement the log parsing logic here
        passed_pattern = r"PASSED (tests/.*?)(?:\s|$)"
        passed_tests = set(re.findall(passed_pattern, log))
        failed_pattern = r".*?(?:ERROR|FAILED) (tests/.*?)(?:[ -]|$)"
        failed_tests = set(re.findall(failed_pattern, log))
        skipped_tests = set()  # Placeholder as no skipped tests found in logs
        parsed_results = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
        }

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
