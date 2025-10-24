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
        return "python:3.10-slim"
    
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
node -v
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y nodejs npm
###ACTION_DELIMITER###
apt-get install -y postgresql
###ACTION_DELIMITER###
service postgresql start
###ACTION_DELIMITER###
pip install pipenv
###ACTION_DELIMITER###
pipenv install --dev
###ACTION_DELIMITER###
pipenv --python 3.10 install --dev
###ACTION_DELIMITER###
pipenv run pip install pip<24.1
###ACTION_DELIMITER###
pipenv run pip install 'pip<24.1'
###ACTION_DELIMITER###
pipenv install --dev
###ACTION_DELIMITER###
pipenv update celery
###ACTION_DELIMITER###
sed -i 's/celery = {version = "*", extras = \["redis"\]}/celery = {version = ">=4.2.2", extras = ["redis"]}/' Pipfile
###ACTION_DELIMITER###
pipenv install --dev
###ACTION_DELIMITER###
rm Pipfile.lock
###ACTION_DELIMITER###
pipenv install --dev
###ACTION_DELIMITER###
sed -i 's/django-elasticsearch-dsl = ">=0.5.0.<0.6.0"/django-elasticsearch-dsl = ">=0.5.0,<0.6.0"/' Pipfile
###ACTION_DELIMITER###
pipenv install --dev
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
apt-get install -y python2.7 && ln -s /usr/bin/python2.7 /usr/bin/python2
###ACTION_DELIMITER###
apt-get install -y python2 && ln -s /usr/bin/python2 /usr/bin/python2.7
###ACTION_DELIMITER###
sed -i 's/"node-sass": "^4.10.0"/"sass": "^1.69.5"/' package.json
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
pip install -r requirements.txt && pip install -r requirements_dev.txt && echo -e 'npm test --verbose
pipenv run pytest -v' > /home/saleor/test_commands.sh && chmod +x /home/saleor/test_commands.sh
###ACTION_DELIMITER###
pip install pycparser && pip install -r requirements.txt && pip install -r requirements_dev.txt
###ACTION_DELIMITER###
sed -i 's/maxminddb==1.4.1/maxminddb>=2.0.0/' requirements.txt && pip install -r requirements.txt && pip install -r requirements_dev.txt
###ACTION_DELIMITER###
apt-get install -y uwsgi uwsgi-plugin-python3 && pip install -r requirements.txt && pip install -r requirements_dev.txt && echo -e 'npm test --verbose
pytest -v' > /home/saleor/test_commands.sh && chmod +x /home/saleor/test_commands.sh
###ACTION_DELIMITER###
sed -i '/uwsgi/d' requirements.txt && pip install -r requirements.txt && pip install -r requirements_dev.txt && echo -e 'npm test --verbose
pipenv run pytest -v' > /home/saleor/test_commands.sh && chmod +x /home/saleor/test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libpq-dev && pip install -r requirements.txt && pip install -r requirements_dev.txt && echo -e 'npm test --verbose
pipenv run pytest -v' > /home/saleor/test_commands.sh && chmod +x /home/saleor/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/psycopg2-binary==2.7.6.1/psycopg2-binary>=2.8.0/' requirements.txt && pip install -r requirements.txt && pip install -r requirements_dev.txt && echo -e 'npm test --verbose
pipenv run pytest -v' > /home/saleor/test_commands.sh && chmod +x /home/saleor/test_commands.sh
###ACTION_DELIMITER###
apt-get install -y zlib1g-dev && pip install -r requirements.txt && pip install -r requirements_dev.txt && echo -e 'npm test --verbose
pipenv run pytest -v' > /home/saleor/test_commands.sh && chmod +x /home/saleor/test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libjpeg-dev && pip install -r requirements.txt && pip install -r requirements_dev.txt && echo -e 'npm test --verbose
pipenv run pytest -v' > /home/saleor/test_commands.sh && chmod +x /home/saleor/test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libffi-dev && pip install -r requirements.txt && pip install -r requirements_dev.txt && echo -e 'npm test --verbose
pipenv run pytest -v' > /home/saleor/test_commands.sh && chmod +x /home/saleor/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/cffi==1.11.5/cffi>=1.15.0/' requirements.txt && pip install -r requirements.txt && pip install -r requirements_dev.txt && echo -e 'npm test --verbose
pipenv run pytest -v' > /home/saleor/test_commands.sh && chmod +x /home/saleor/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/codecov==2.0.15/codecov==2.1.13/' requirements_dev.txt && pip install -r requirements.txt && pip install -r requirements_dev.txt && echo -e 'npm test --verbose
pipenv run pytest -v' > /home/saleor/test_commands.sh && chmod +x /home/saleor/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/transifex-client==0.13.5/transifex-client==0.12.5/' requirements_dev.txt && pip install -r requirements.txt && pip install -r requirements_dev.txt && echo -e 'npm test --verbose
pipenv run pytest -v' > /home/saleor/test_commands.sh && chmod +x /home/saleor/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npm test --verbose
pipenv run pytest -v

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
npm test --verbose
pipenv run pytest -v

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
npm test --verbose
pipenv run pytest -v

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

# Choose an appropriate base image based on the project's requirements - replace python:3.10-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.10-slim

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


@Instance.register("saleor", "saleor_3435_to_3431")
class SALEOR_3435_TO_3431(Instance):
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
        skipped_tests: set[str] = set() # Tests that were skipped
        import re
        current_group = ""
        lines = log.split('\n')
        for line in lines:
            # Extract content after the line number bracket
            if ']' in line:
                content = line.split(']', 1)[1].strip()
            else:
                content = line.strip()
            # Check if it's a group line (e.g., "Generics / ActionDialog")
            group_match = re.match(r'^[\w\s/]+$', content)
            if group_match and not re.search(r'[✓✕-]', content):
                current_group = content
                continue
            # Check if it's a test case line (e.g., "✓ default (37ms)")
            test_match = re.match(r'^([✓✕-])\s+([^\(]+)\s*\(\d+ms\)$', content)
            if test_match:
                symbol = test_match.group(1)
                test_case = test_match.group(2).strip()
                full_test_name = f"{current_group} {test_case}" if current_group else test_case
                if symbol == '✓':
                    passed_tests.add(full_test_name)
                elif symbol == '✕':
                    failed_tests.add(full_test_name)
                elif symbol == '-':
                    skipped_tests.add(full_test_name)
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
