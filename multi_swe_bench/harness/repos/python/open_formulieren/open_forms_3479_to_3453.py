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
                """apt-get update && apt-get install -y pkg-config libmagic1 libxml2-dev libxmlsec1-openssl libpq-dev gettext gdal-bin chromium-driver postgresql postgresql-client redis-server python3.9-dev build-essential
###ACTION_DELIMITER###
apt-get update && apt-get install -y pkg-config libmagic1 libxml2-dev libxmlsec1-openssl libpq-dev gettext gdal-bin chromium-driver postgresql postgresql-client redis-server python3-dev build-essential
###ACTION_DELIMITER###
python3 -m venv env && source env/bin/activate && pip install -r requirements/dev.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y libxslt-dev
###ACTION_DELIMITER###
source env/bin/activate && pip install -r requirements/dev.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y xmlsec1
###ACTION_DELIMITER###
source env/bin/activate && pip install -r requirements/dev.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y libxmlsec1-dev
###ACTION_DELIMITER###
which xmlsec1 && xmlsec1 --version
###ACTION_DELIMITER###
source env/bin/activate && pip install --upgrade pip && pip install -r requirements/dev.txt
###ACTION_DELIMITER###
cat requirements/dev.txt | grep 'maykin-django-two-factor-auth' && pip install maykin-django-two-factor-auth==2.0.4
###ACTION_DELIMITER###
source env/bin/activate && pip install --upgrade pip==24.0 && pip install -r requirements/dev.txt
###ACTION_DELIMITER###
service postgresql start && service redis-server start
###ACTION_DELIMITER###
source env/bin/activate && python src/manage.py test src -v 2
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.10 python3.10-venv python3.10-dev
###ACTION_DELIMITER###
curl https://pyenv.run | bash && echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc && echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc && echo 'eval "$(pyenv init -)"' >> ~/.bashrc && source ~/.bashrc && pyenv install 3.10.0 && pyenv local 3.10.0 && python -m venv env && source env/bin/activate && pip install -r requirements/dev.txt
###ACTION_DELIMITER###
source ~/.bashrc && pyenv local 3.10.0 && python --version && rm -rf env && python -m venv env && source env/bin/activate && pip install -r requirements/dev.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y libffi-dev && pyenv uninstall -f 3.10.0 && pyenv install 3.10.0 && pyenv local 3.10.0 && rm -rf env && python -m venv env && source env/bin/activate && pip install -r requirements/dev.txt
###ACTION_DELIMITER###
export PATH="$HOME/.pyenv/bin:$PATH" && eval "$(pyenv init -)" && pyenv uninstall -f 3.10.0 && pyenv install 3.10.0 && pyenv local 3.10.0 && rm -rf env && python -m venv env && source env/bin/activate && pip install -r requirements/dev.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y libbz2-dev && export PATH="$HOME/.pyenv/bin:$PATH" && eval "$(pyenv init -)" && pyenv uninstall -f 3.10.0 && pyenv install 3.10.0 && pyenv local 3.10.0 && rm -rf env && python -m venv env && source env/bin/activate && pip install -r requirements/dev.txt
###ACTION_DELIMITER###
source env/bin/activate && python src/manage.py test src -v 2
###ACTION_DELIMITER###
service postgresql stop && sed -i 's/local   all             all                                     peer/local   all             all                                     trust/' /etc/postgresql/15/main/pg_hba.conf && sed -i 's/host    all             all             127.0.0.1\/32            scram-sha-256/host    all             all             127.0.0.1\/32            trust/' /etc/postgresql/15/main/pg_hba.conf && sed -i 's/host    all             all             ::1\/128                 scram-sha-256/host    all             all             ::1\/128                 trust/' /etc/postgresql/15/main/pg_hba.conf && service postgresql start && service redis-server start
###ACTION_DELIMITER###
sudo -u postgres createuser --superuser openforms
###ACTION_DELIMITER###
su - postgres -c 'createuser --superuser openforms'
###ACTION_DELIMITER###
su - postgres -c 'createdb openforms'
###ACTION_DELIMITER###
source env/bin/activate && python src/manage.py test src -v 2
###ACTION_DELIMITER###
echo 'python src/manage.py test src -v 2' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
python src/manage.py test src -v 2

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
python src/manage.py test src -v 2

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
python src/manage.py test src -v 2

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
RUN git clone https://github.com/open-formulieren/open-forms.git /home/open-forms

WORKDIR /home/open-forms
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("open-formulieren", "open_forms_3479_to_3453")
class OPEN_FORMS_3479_TO_3453(Instance):
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
        # Regex pattern to match test lines
        test_pattern = re.compile(r'(?:\[\s*\d+\]\s+)?(test[^(]+)\s+\([^)]+\)\s+\.\.\.\s+(\w+)', re.IGNORECASE)
        # Find all matches in the log
        matches = test_pattern.findall(log)
        for test_name, status in matches:
            status_lower = status.lower()
            if status_lower == 'ok':
                passed_tests.add(test_name)
            elif status_lower in ['failed', 'fail', 'error']:
                failed_tests.add(test_name)
            elif status_lower == 'skipped':
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
