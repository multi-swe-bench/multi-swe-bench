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
        return "python:3.11-slim"
    
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
                """npm install
###ACTION_DELIMITER###
apt-get update && apt-get install -y nodejs npm
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2.7
###ACTION_DELIMITER###
export PYTHON=python3 && npm install
###ACTION_DELIMITER###
npm install -g node-gyp && npm install
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && source ~/.nvm/nvm.sh && nvm install 8 && nvm use 8 && npm install
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && source ~/.nvm/nvm.sh && nvm install 8 && nvm use 8 && npm install
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl
###ACTION_DELIMITER###
git clone https://github.com/pyenv/pyenv.git ~/.pyenv && export PYENV_ROOT="$HOME/.pyenv" && export PATH="$PYENV_ROOT/bin:$PATH" && eval "$(pyenv init -)" && pyenv install 3.7.0 && pyenv local 3.7.0 && pipenv install --dev --python 3.7
###ACTION_DELIMITER###
pip install pipenv
###ACTION_DELIMITER###
pipenv install --dev --python 3.7
###ACTION_DELIMITER###
pipenv run pip install --upgrade pip
###ACTION_DELIMITER###
pipenv run pip install graphql-relay promise
###ACTION_DELIMITER###
cat Pipfile
###ACTION_DELIMITER###
sed -i 's/django = "*"/django = "<=3.2.18"/' Pipfile
###ACTION_DELIMITER###
pipenv install --dev
###ACTION_DELIMITER###
cat Pipfile
###ACTION_DELIMITER###
sed -i 's/pytest-django = "<=3.2.18"==3.3.3"/pytest-django = "==3.3.3"/' Pipfile && sed -i 's/django = "<=3.2.18"*"/django = "<=3.2.18"/' Pipfile && sed -i 's/graphene-django = "<=3.2.18"*"/graphene-django = "*"/' Pipfile
###ACTION_DELIMITER###
cat Pipfile
###ACTION_DELIMITER###
sed -i 's/django = "<=3.2.18"*"/django = "<=3.2.18"/' Pipfile && sed -i 's/graphene-django = "*"*"/graphene-django = "*"/' Pipfile
###ACTION_DELIMITER###
cat Pipfile
###ACTION_DELIMITER###
sed -i 's/django = "<=3.2.18"*"/django = "<=3.2.18"/' Pipfile && sed -i 's/graphene-django = "*"*"*"/graphene-django = "*"/' Pipfile
###ACTION_DELIMITER###
sed -i 's/django = "<=3.2.18"*"/django = "<=3.2.18"/' Pipfile && sed -i 's/graphene-django = "*"*"*"/graphene-django = "*"/' Pipfile
###ACTION_DELIMITER###
sed -i 's/^django = .*/django = "<=3.2.18"/' Pipfile && sed -i 's/^graphene-django = .*/graphene-django = "*"/' Pipfile
###ACTION_DELIMITER###
cat Pipfile
###ACTION_DELIMITER###
pipenv install --dev
###ACTION_DELIMITER###
echo 'promise = "==2.2.1"' >> Pipfile && pipenv install --dev
###ACTION_DELIMITER###
pipenv run pip install promise --no-binary :all:
###ACTION_DELIMITER###
sed -i '/promise/d' Pipfile && echo 'promise = "==2.2.1"' >> Pipfile && sed -i '/six/d' Pipfile && echo 'six = "==1.16.0"' >> Pipfile && pipenv install --dev
###ACTION_DELIMITER###
pyenv uninstall -f 3.7.0 && pyenv install 3.7.0 && pipenv install --dev
###ACTION_DELIMITER###
pip install pipenv
###ACTION_DELIMITER###
pipenv run pip install --upgrade pip && pipenv install --dev
###ACTION_DELIMITER###
pipenv run pip install setuptools==40.0.0 && pipenv install --dev
###ACTION_DELIMITER###
sed -i 's/promise = ".*"/promise = "==2.2.0"/' Pipfile && pipenv run pip cache purge && pipenv install --dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl && pyenv uninstall -f 3.7.0 && pyenv install 3.7.0 && pip install pipenv && pipenv install --dev
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pipenv run pytest
npm test' > /home/tenants2/test_commands.sh && chmod +x /home/tenants2/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
pipenv run pytest
npm test

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
pipenv run pytest
npm test

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
pipenv run pytest
npm test

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

# Choose an appropriate base image based on the project's requirements - replace python:3.11-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.11-slim

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


@Instance.register("JustFixNYC", "tenants2_178_to_23")
class TENANTS2_178_TO_23(Instance):
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
        import json
        pattern = re.compile(r'^(PASS|FAIL|SKIPPED)\s+(.*)$', re.MULTILINE)
        for match in pattern.finditer(log):
            status = match.group(1)
            test_name = match.group(2)
            if status == 'PASS':
                passed_tests.add(test_name)
            elif status == 'FAIL':
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
