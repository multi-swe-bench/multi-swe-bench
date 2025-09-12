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
                """sed -i 's/git:\/\/github.com\/flask-restful\/flask-restful.git/https:\/\/github.com\/flask-restful\/flask-restful.git/' requirements.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y libpq-dev gcc
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
pip install --force-reinstall Flask==0.10.1 flask-restful==0.2.0
###ACTION_DELIMITER###
pip install --force-reinstall flask-sqlalchemy==2.1.0
###ACTION_DELIMITER###
pip install --force-reinstall Flask==0.10.1 flask-restful==0.2.0 flask-sqlalchemy==2.1.0
###ACTION_DELIMITER###
scripts/bootstrap/fec_bootstrap.sh
###ACTION_DELIMITER###
pip install --force-reinstall Flask==0.10.1 flask-restful==0.3.8 flask-sqlalchemy==2.1.0 SQLAlchemy==1.4.46
###ACTION_DELIMITER###
pip install --upgrade python-dateutil>=2.8.2
###ACTION_DELIMITER###
echo 'nosetests -v' > /home/openFEC/test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y postgresql postgresql-contrib
###ACTION_DELIMITER###
pg_ctlcluster 15 main start
###ACTION_DELIMITER###
bash /home/openFEC/test_commands.sh
###ACTION_DELIMITER###
pip install --force-reinstall Jinja2==2.11.3
###ACTION_DELIMITER###
bash /home/openFEC/test_commands.sh
###ACTION_DELIMITER###
pip install --force-reinstall MarkupSafe==1.1.1
###ACTION_DELIMITER###
pip install --force-reinstall Werkzeug==0.16.1
###ACTION_DELIMITER###
bash /home/openFEC/test_commands.sh
###ACTION_DELIMITER###
pip install --force-reinstall itsdangerous==0.24
###ACTION_DELIMITER###
bash /home/openFEC/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/flask.ext.restful.representations.json.settings["cls"] = TolerantJSONEncoder/app.config["RESTFUL_JSON"] = {"cls": TolerantJSONEncoder}/' /home/openFEC/webservices/rest.py
###ACTION_DELIMITER###
bash /home/openFEC/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/flask\.ext\.restful\.representations\.json\.settings\[.*\] = TolerantJSONEncoder/app.config["RESTFUL_JSON"] = {"cls": TolerantJSONEncoder}/' /home/openFEC/webservices/rest.py
###ACTION_DELIMITER###
sed -i 's/flask\.ext\.restful\.representations\.json\.settings\["cls"] = TolerantJSONEncoder/app.config["RESTFUL_JSON"] = {"cls": TolerantJSONEncoder}/' /home/openFEC/webservices/rest.py
###ACTION_DELIMITER###
sed -i '29s/.*/app.config["RESTFUL_JSON"] = {"cls": TolerantJSONEncoder}/' /home/openFEC/webservices/rest.py
###ACTION_DELIMITER###
bash /home/openFEC/test_commands.sh
###ACTION_DELIMITER###
sed -i '29d' /home/openFEC/webservices/rest.py && sed -i '/app = Flask/a app.config["RESTFUL_JSON"] = {"cls": TolerantJSONEncoder}' /home/openFEC/webservices/rest.py
###ACTION_DELIMITER###
bash /home/openFEC/test_commands.sh
###ACTION_DELIMITER###
su postgres -c 'createuser -s root'
###ACTION_DELIMITER###
bash /home/openFEC/test_commands.sh
###ACTION_DELIMITER###
su postgres -c 'createdb cfdm-unit-test'
###ACTION_DELIMITER###
bash /home/openFEC/test_commands.sh
###ACTION_DELIMITER###
invoke build_test postgresql://postgres@localhost/postgres postgresql://root@localhost/cfdm-unit-test
###ACTION_DELIMITER###
sed -i 's/def build_test(/def build_test(ctx, /' /home/openFEC/tasks.py
###ACTION_DELIMITER###
invoke build_test postgresql://postgres@localhost/postgres postgresql://root@localhost/cfdm-unit-test
###ACTION_DELIMITER###
sed -i 's/def add_hooks():/def add_hooks(ctx):/' /home/openFEC/tasks.py
###ACTION_DELIMITER###
sed -i 's/def build_test(/def build_test(ctx, /' /home/openFEC/tasks.py
###ACTION_DELIMITER###
sed -i 's/def add_hooks(/def add_hooks(ctx, /' /home/openFEC/tasks.py
###ACTION_DELIMITER###
sed -i 's/def add_hooks():/def add_hooks(ctx):/' /home/openFEC/tasks.py
###ACTION_DELIMITER###
sed -i 's/def add_hooks\s*():/def add_hooks(ctx):/' /home/openFEC/tasks.py
###ACTION_DELIMITER###
sed -i 's/def add_hooks(\s*):/def add_hooks(ctx):/' /home/openFEC/tasks.py
###ACTION_DELIMITER###
sed -i 's/def add_hooks\s*([^)]*):/def add_hooks(ctx):/' /home/openFEC/tasks.py
###ACTION_DELIMITER###
sed -i 's/def add_hooks\s*():/def add_hooks(ctx):/' /home/openFEC/tasks.py
###ACTION_DELIMITER###
sed -i 's/def build_test\s*(/def build_test(ctx, /' /home/openFEC/tasks.py
###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i 's/def add_hooks\s*():/def add_hooks(ctx):/' /home/openFEC/tasks.py
###ACTION_DELIMITER###
sed -i '74s/def add_hooks():/def add_hooks(ctx):/' /home/openFEC/tasks.py
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
nosetests -v

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
nosetests -v

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
nosetests -v

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
RUN git clone https://github.com/fecgov/openFEC.git /home/openFEC

WORKDIR /home/openFEC
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("fecgov", "openFEC_719_to_449")
class OPENFEC_719_TO_449(Instance):
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
        lines = log.split('\n')
        current_test = None  # Track test name across lines
        test_pattern = re.compile(r'(test_\w+)\s*\(.*?\)\s*\.\.\.')  # Matches test name
        status_pattern = re.compile(r'(?:\.\.\.\s*)?(ok|FAIL|ERROR|SKIP)(:.*)?$')  # Matches status with optional ... and message
        for line in lines:
            # Capture test name if present
            test_match = test_pattern.search(line)
            if test_match:
                current_test = test_match.group(1)
            # Capture status if present and we have a pending test
            status_match = status_pattern.search(line)
            if status_match and current_test:
                status = status_match.group(1)
                if status == 'ok':
                    passed_tests.add(current_test)
                elif status in ['FAIL', 'ERROR']:
                    failed_tests.add(current_test)
                elif status == 'SKIP':
                    skipped_tests.add(current_test)
                current_test = None  # Reset after processing
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
