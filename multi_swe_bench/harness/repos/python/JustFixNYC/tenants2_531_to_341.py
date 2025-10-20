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
apt-get update && apt-get install -y python3.7 python3.7-venv python3.7-dev libpq-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl && git clone https://github.com/pyenv/pyenv.git /root/.pyenv && echo 'export PYENV_ROOT="/root/.pyenv"' >> ~/.bashrc && echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc && echo 'eval "$(pyenv init -)"' >> ~/.bashrc && source ~/.bashrc && pyenv install 3.7.0 && pyenv local 3.7.0
###ACTION_DELIMITER###
pip install pipenv
###ACTION_DELIMITER###
pipenv install --dev
###ACTION_DELIMITER###
pyenv install 3.7.17 --force && pyenv local 3.7.17 && rm -rf /root/.local/share/virtualenvs/tenants2-bdka8-Jl && pipenv --python 3.7.17 install --dev --skip-lock
###ACTION_DELIMITER###
pyenv local 3.7.17 && python -m pip install pipenv && rm -rf /root/.local/share/virtualenvs/tenants2-* && pipenv --python 3.7.17 install --dev --skip-lock
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
apt-get update && apt-get install -y nodejs npm
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye main' > /etc/apt/sources.list.d/bullseye.list && apt-get update && apt-get install -y python2.7 && npm config set python python2.7 && npm install
###ACTION_DELIMITER###
PYTHON=python2.7 npm install
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && source ~/.bashrc && nvm install 14 && nvm use 14 && npm install
###ACTION_DELIMITER###
npm config set python /usr/bin/python2.7 && npm cache clean --force && npm install
###ACTION_DELIMITER###
nvm install 10 && nvm use 10 && npm install
###ACTION_DELIMITER###
pipenv run pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
rm -rf /root/.local/share/virtualenvs/tenants2-* && pipenv lock && pipenv install --dev
###ACTION_DELIMITER###
pipenv run pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
sed -i '/\[dev-packages\]/a attrs = "==19.3.0"' Pipfile && pipenv install --dev
###ACTION_DELIMITER###
rm -rf /root/.local/share/virtualenvs/tenants2-* && pipenv install --dev && pipenv run pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
sed -i '/\[dev-packages\]/a six = "==1.14.0"' Pipfile && sed -i '/\[dev-packages\]/a attrs = "==19.2.0"' Pipfile && rm -rf /root/.local/share/virtualenvs/tenants2-* && pipenv install --dev && pipenv run pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
sed -i '/attrs =/d' Pipfile && sed -i '/six =/d' Pipfile && sed -i '/\[dev-packages\]/a attrs = "==19.2.0"' Pipfile && sed -i '/\[dev-packages\]/a six = "==1.14.0"' Pipfile && rm -rf /root/.local/share/virtualenvs/tenants2-* && pipenv install --dev && pipenv run pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
sed -i '/attrs =/d' Pipfile && sed -i '/six =/d' Pipfile && sed -i '/\[dev-packages\]/a attrs = "==18.2.0"' Pipfile && sed -i '/\[dev-packages\]/a six = "==1.14.0"' Pipfile && rm -rf /root/.local/share/virtualenvs/tenants2-* && pipenv install --dev && pipenv run pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
sed -i '/attrs =/d' Pipfile && sed -i '/six =/d' Pipfile && sed -i '/\[dev-packages\]/a attrs = "==19.1.0"' Pipfile && sed -i '/\[dev-packages\]/a six = "==1.14.0"' Pipfile && rm -rf /root/.local/share/virtualenvs/tenants2-* && pipenv install --dev && pipenv run pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
sed -i '/pytest =/d' Pipfile && sed -i '/attrs =/d' Pipfile && sed -i '/six =/d' Pipfile && sed -i '/\[dev-packages\]/a pytest = "==4.2.1"' Pipfile && sed -i '/\[dev-packages\]/a attrs = "==19.3.0"' Pipfile && sed -i '/\[dev-packages\]/a six = "==1.14.0"' Pipfile && rm -rf Pipfile.lock /root/.local/share/virtualenvs/tenants2-* && pipenv install --dev && pipenv run pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
sed -i '/attrs =/d' Pipfile && sed -i '/\[dev-packages\]/a attrs = "==18.2.0"' Pipfile && rm -rf /root/.local/share/virtualenvs/tenants2-* && pipenv install --dev && pipenv run pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
rm -rf /root/.local/share/virtualenvs/tenants2-* && pipenv install --dev && pipenv run pip install attrs==18.2.0 pytest==4.2.1 six==1.14.0 && pipenv run pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
export DATABASE_URL='sqlite:///test.db' && pipenv run pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
apt-get update && apt-get install -y gdal-bin libgdal-dev python3-gdal && export DATABASE_URL='sqlite:///test.db' && pipenv run pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
echo 'export DATABASE_URL="sqlite:///test.db"' > /home/tenants2/test_commands.sh && echo 'pipenv run pytest -v -rA --tb=no -p no:cacheprovider' >> /home/tenants2/test_commands.sh && chmod +x /home/tenants2/test_commands.sh && bash /home/tenants2/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
export DATABASE_URL="sqlite:///test.db"
pipenv run pytest -v -rA --tb=no -p no:cacheprovider

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
export DATABASE_URL="sqlite:///test.db"
pipenv run pytest -v -rA --tb=no -p no:cacheprovider

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
export DATABASE_URL="sqlite:///test.db"
pipenv run pytest -v -rA --tb=no -p no:cacheprovider

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
RUN git clone https://github.com/JustFixNYC/tenants2.git /home/tenants2

WORKDIR /home/tenants2
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("JustFixNYC", "tenants2_531_to_341")
class TENANTS2_531_TO_341(Instance):
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
        # Regex pattern to match test lines with status
        pattern = re.compile(r'^(.*?)\s+(PASSED|FAILED|SKIPPED)\s+\[\s*\d+%\]')
        for line in log.split('\n'):
            line = line.strip()
            match = pattern.match(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
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
