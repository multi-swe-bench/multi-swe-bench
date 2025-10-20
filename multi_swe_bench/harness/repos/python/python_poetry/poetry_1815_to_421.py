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
                """ls -la
###ACTION_DELIMITER###
cat Makefile
###ACTION_DELIMITER###
python3 get-poetry.py -y
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
python3 get-poetry.py -y
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH"
###ACTION_DELIMITER###
poetry install
###ACTION_DELIMITER###
python3 -m venv .venv
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv .venv
###ACTION_DELIMITER###
source .venv/bin/activate
###ACTION_DELIMITER###
poetry install
###ACTION_DELIMITER###
pip install poetry
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
make setup
###ACTION_DELIMITER###
deactivate && poetry install
###ACTION_DELIMITER###
pip install intreehooks && pip install -e .
###ACTION_DELIMITER###
source .venv/bin/activate && pip install --break-system-packages poetry && poetry install
###ACTION_DELIMITER###
source .venv/bin/activate && pip install --break-system-packages cleo==0.7.6 clikit==0.4.1 requests==2.18 cachy==0.3.0 requests-toolbelt==0.8.0 jsonschema==3.1 pyrsistent==0.14.2 pyparsing==2.2 'cachecontrol[filecache]==0.12.4' pkginfo==1.4 html5lib==1.0 shellingham==1.1 tomlkit==0.5.8 pexpect==4.7.0 keyring==19.0 pytest==4.1 pytest-cov==2.5 mkdocs==1.0 pymdown-extensions==6.0 pygments==2.2 pytest-mock==1.9 pygments-github-lexers==0.0.5 black==19.10b0 pre-commit==1.10 tox==3.0 pytest-sugar==0.9.2 httpretty==0.9.6 markdown-include==0.5.1
###ACTION_DELIMITER###
source .venv/bin/activate && pip install --break-system-packages cleo==0.7.6 clikit==0.4.1 requests==2.18 cachy==0.3.0 requests-toolbelt==0.8.0 jsonschema==3.1 pyrsistent==0.14.2 pyparsing==2.2 'cachecontrol[filecache]==0.12.4' pkginfo==1.4 'html5lib>=1.0,<1.1' shellingham==1.1 tomlkit==0.5.8 pexpect==4.7.0 keyring==19.0 pytest==4.1 pytest-cov==2.5 mkdocs==1.0 pymdown-extensions==6.0 pygments==2.2 pytest-mock==1.9 pygments-github-lexers==0.0.5 black==19.10b0 pre-commit==1.10 tox==3.0 pytest-sugar==0.9.2 httpretty==0.9.6 markdown-include==0.5.1
###ACTION_DELIMITER###
echo 'pytest tests -v --junitxml=test-results.xml' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source .venv/bin/activate && pip install --upgrade pytest
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source .venv/bin/activate && pip install --upgrade httpretty
###ACTION_DELIMITER###
echo -e '#!/bin/bash
 source .venv/bin/activate
 pytest tests -v --junitxml=test-results.xml' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source .venv/bin/activate && pip install --upgrade pyparsing
###ACTION_DELIMITER###
source .venv/bin/activate && pip install pyparsing==2.4.7
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source .venv/bin/activate && pip install --upgrade pyrsistent
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source .venv/bin/activate && pip install --upgrade urllib3
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.8 python3.8-venv && python3.8 -m venv .venv38 && source .venv38/bin/activate && pip install --upgrade pip && pip install --break-system-packages -r <(poetry export --dev --format requirements.txt) && echo 'source .venv38/bin/activate && pytest tests -v --junitxml=test-results.xml' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.8 python3.8-venv && python3.8 -m venv .venv38 && source .venv38/bin/activate && pip install --upgrade pip && pip install --break-system-packages -r <(poetry export --dev --format requirements.txt) && echo 'source .venv38/bin/activate && pytest tests -v --junitxml=test-results.xml' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
source .venv38/bin/activate && pip install poetry && poetry export --dev --format requirements.txt --output requirements.txt && pip install -r requirements.txt && echo 'source .venv38/bin/activate && pytest tests -v --junitxml=test-results.xml' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
source .venv38/bin/activate && pip uninstall -y cleo && pip install cleo==0.7.6 clikit==0.4.1 && pip install -r <(poetry export --dev --format requirements.txt --without-hashes) && echo 'source .venv38/bin/activate && pytest tests -v --junitxml=test-results.xml' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
source .venv38/bin/activate && pip install jsonschema && echo 'source .venv38/bin/activate && pytest tests -v --junitxml=test-results.xml' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
source .venv38/bin/activate && pip install poetry==1.0.0 && poetry install && echo 'source .venv38/bin/activate && poetry run pytest tests -v --junitxml=test-results.xml' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
apt-get install -y python3.8-dev && source .venv38/bin/activate && poetry install
###ACTION_DELIMITER###
echo 'source .venv38/bin/activate && poetry run pytest tests -v --junitxml=test-results.xml' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
source .venv38/bin/activate && poetry run pytest tests -v --junitxml=test-results.xml

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
source .venv38/bin/activate && poetry run pytest tests -v --junitxml=test-results.xml

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
source .venv38/bin/activate && poetry run pytest tests -v --junitxml=test-results.xml

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
RUN git clone https://github.com/python-poetry/poetry.git /home/poetry

WORKDIR /home/poetry
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("python-poetry", "poetry_1815_to_421")
class POETRY_1815_TO_421(Instance):
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
        passed_tests: set[str] = set()
        failed_tests: set[str] = set()
        skipped_tests: set[str] = set()
        import re
        # Regex pattern to match test lines with status
        pattern = r".*?(tests/[^ ]+)\s+(PASSED|FAILED|SKIPPED)"
        # Extract all tests
        matches = re.findall(pattern, log, re.MULTILINE | re.IGNORECASE)
        for test_name, status in matches:
            status_upper = status.upper()
            if status_upper == "PASSED":
                passed_tests.add(test_name)
            elif status_upper == "FAILED":
                failed_tests.add(test_name)
            elif status_upper == "SKIPPED":
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
