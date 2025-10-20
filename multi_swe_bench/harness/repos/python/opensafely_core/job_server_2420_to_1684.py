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
                """ls
###ACTION_DELIMITER###
cat justfile
###ACTION_DELIMITER###
cat TESTING.md
###ACTION_DELIMITER###
cat requirements.dev.txt
###ACTION_DELIMITER###
pip install -r requirements.prod.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y libpq-dev
###ACTION_DELIMITER###
pip install -r requirements.prod.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip install -r requirements.prod.txt
###ACTION_DELIMITER###
pip install -r requirements.dev.txt
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider ./...' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider .' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y postgresql postgresql-contrib
###ACTION_DELIMITER###
service postgresql start && su - postgres -c 'createdb jobserver'
###ACTION_DELIMITER###
export DATABASE_URL=postgres://postgres@localhost/jobserver
###ACTION_DELIMITER###
sed -i 's/local   all             postgres                                peer/local   all             postgres                                trust/' /etc/postgresql/15/main/pg_hba.conf && service postgresql restart
###ACTION_DELIMITER###
python manage.py migrate
###ACTION_DELIMITER###
export SECRET_KEY='django-insecure-test-secret-key-12345'
###ACTION_DELIMITER###
python manage.py migrate
###ACTION_DELIMITER###
export SOCIAL_AUTH_GITHUB_KEY='dummy-key' && export SOCIAL_AUTH_GITHUB_SECRET='dummy-secret'
###ACTION_DELIMITER###
python manage.py migrate
###ACTION_DELIMITER###
export GITHUB_TOKEN='dummy-token'
###ACTION_DELIMITER###
GITHUB_TOKEN=dummy-token python manage.py migrate
###ACTION_DELIMITER###
cat /etc/postgresql/15/main/pg_hba.conf | grep 'local   all             postgres'
###ACTION_DELIMITER###
export DATABASE_URL=postgres://postgres@127.0.0.1/jobserver && python manage.py migrate
###ACTION_DELIMITER###
echo 'host    all             postgres        127.0.0.1/32            trust' >> /etc/postgresql/15/main/pg_hba.conf && service postgresql restart && python manage.py migrate
###ACTION_DELIMITER###
cat /etc/postgresql/15/main/pg_hba.conf
###ACTION_DELIMITER###
sed -i '/host    all             all             127.0.0.1\/32            scram-sha-256/i host    all             postgres        127.0.0.1/32            trust' /etc/postgresql/15/main/pg_hba.conf && sed -i '/host    all             postgres        127.0.0.1\/32            trust/d' /etc/postgresql/15/main/pg_hba.conf && service postgresql restart && python manage.py migrate
###ACTION_DELIMITER###
sed -i '/host    all             all             127.0.0.1\/32            scram-sha-256/i host    all             postgres        127.0.0.1/32            trust' /etc/postgresql/15/main/pg_hba.conf && service postgresql restart && python manage.py migrate
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && apt-get install -y nodejs && npm ci && npm run build && python manage.py collectstatic --noinput
###ACTION_DELIMITER###
apt-get install -y npm && npm ci && npm run build && python manage.py collectstatic --noinput
###ACTION_DELIMITER###
sed -i 's/git+ssh:\/\/git@github.com\/ebmdatalab\/alpine.git/git+https:\/\/github.com\/ebmdatalab\/alpine.git/g' package.json && npm ci && npm run build && python manage.py collectstatic --noinput
###ACTION_DELIMITER###
sed -i 's/git+ssh:\/\/git@github.com\/ebmdatalab\/alpine.git/git+https:\/\/github.com\/ebmdatalab\/alpine.git/g' package.json package-lock.json && npm ci && npm run build && python manage.py collectstatic --noinput
###ACTION_DELIMITER###
npm install git+https://github.com/ebmdatalab/alpine.git && npm ci && npm run build && python manage.py collectstatic --noinput
###ACTION_DELIMITER###
sed -i 's/git+ssh:\/\/git@github.com\/ebmdatalab\/alpine.git/git+https:\/\/github.com\/ebmdatalab\/alpine.git/g' package.json && rm -rf package-lock.json node_modules && npm install && npm run build && python manage.py collectstatic --noinput
###ACTION_DELIMITER###
cat package.json | grep alpine && npm cache clean --force && rm -rf node_modules package-lock.json && npm install && npm run build && python manage.py collectstatic --noinput
###ACTION_DELIMITER###
sed -i 's/git:\/\/github.com\/ebmdatalab\/alpine.git/git+https:\/\/github.com\/ebmdatalab\/alpine.git/g' package.json && rm -rf node_modules package-lock.json && npm install && npm run build && python manage.py collectstatic --noinput
###ACTION_DELIMITER###
sed -i 's/git:\/\/github.com\/ebmdatalab\/alpine.git/https:\/\/github.com\/ebmdatalab\/alpine.git/g' package.json && rm -rf node_modules package-lock.json && npm install && npm run build && python manage.py collectstatic --noinput
###ACTION_DELIMITER###
sed -i 's/git:\/\/github.com\/ebmdatalab\/alpine.git/https:\/\/github.com\/ebmdatalab\/alpine.git/g' package.json && npm cache clean --force && rm -rf node_modules package-lock.json && npm install && npm run build && python manage.py collectstatic --noinput
###ACTION_DELIMITER###
sed -i 's|git://github.com/ebmdatalab/alpine.git|git+https://github.com/ebmdatalab/alpine.git|g' package.json && npm cache clean --force && rm -rf node_modules package-lock.json && npm install && npm run build && python manage.py collectstatic --noinput
###ACTION_DELIMITER###
git config --global --unset url."git@github.com:".insteadOf && git config --global --unset url."ssh://git@github.com/".insteadOf && sed -i 's|git://github.com/ebmdatalab/alpine.git|https://github.com/ebmdatalab/alpine.git|g' package.json && npm install alpinejs@git+https://github.com/ebmdatalab/alpine.git#v3.10.3-csp && npm install && npm run build && python manage.py collectstatic --noinput
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
npm install alpinejs@git+https://github.com/ebmdatalab/alpine.git#v3.10.3-csp && npm run build && python manage.py collectstatic --noinput && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|git+ssh://git@github.com/ebmdatalab/alpine.git|git+https://github.com/ebmdatalab/alpine.git|g' package.json && rm -rf node_modules package-lock.json && npm cache clean --force && npm install && npm run build && python manage.py collectstatic --noinput && bash test_commands.sh
###ACTION_DELIMITER###
npm install git+https://github.com/ebmdatalab/alpine.git#v3.10.3-csp && npm run build && python manage.py collectstatic --noinput && bash test_commands.sh
###ACTION_DELIMITER###
git config --global url."https://github.com/".insteadOf "git@github.com:" && git config --global url."https://".insteadOf "git://" && rm -rf node_modules package-lock.json && npm cache clean --force && npm install git+https://github.com/ebmdatalab/alpine.git#v3.10.3-csp && npm install && npm run build && python manage.py collectstatic --noinput && bash test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v --no-header -rA --tb=no -p no:cacheprovider .

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider .

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider .

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
RUN git clone https://github.com/opensafely-core/job-server.git /home/job-server

WORKDIR /home/job-server
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("opensafely-core", "job_server_2420_to_1684")
class JOB_SERVER_2420_TO_1684(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        # Parse log content to extract test names and statuses
        # Regex pattern matches lines with test names and PASSED/FAILED/SKIPPED status
        pattern = r'(PASSED|FAILED|SKIPPED)\s+(tests/.*?)(?=\s|\[|$)|(tests/.*?)\s+(PASSED|FAILED|SKIPPED)(?=\s|\[|$)'
        matches = re.findall(pattern, log)
        for match in matches:
            # Handle both pattern groups (status before or after test name)
            if match[0] and match[1]:
                status, test = match[0].strip(), match[1].strip()
            else:
                test, status = match[2].strip(), match[3].strip()
            # Categorize tests into respective sets
            if status == 'PASSED':
                passed_tests.add(test)
            elif status == 'FAILED':
                failed_tests.add(test)
            elif status == 'SKIPPED':
                skipped_tests.add(test)
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
