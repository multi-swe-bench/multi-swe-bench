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
        return "ubuntu:22.04"

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
                """ls -la
###ACTION_DELIMITER###
make dev-config
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make dev-config
###ACTION_DELIMITER###
make setup
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
make setup
###ACTION_DELIMITER###
pip install cython
###ACTION_DELIMITER###
make setup
###ACTION_DELIMITER###
pip install --no-build-isolation -r requirements.txt
###ACTION_DELIMITER###
pip install git+https://github.com/psf/black.git@20.8b1
###ACTION_DELIMITER###
make setup
###ACTION_DELIMITER###
pip uninstall -y cython && pip install cython==0.29.36
###ACTION_DELIMITER###
make setup
###ACTION_DELIMITER###
pip install cffi==1.14.3
###ACTION_DELIMITER###
apt-get install -y libffi-dev
###ACTION_DELIMITER###
pip install cffi==1.14.3
###ACTION_DELIMITER###
make setup
###ACTION_DELIMITER###
pip install --upgrade setuptools wheel
###ACTION_DELIMITER###
sed -i 's/django-rest-framework/djangorestframework/' requirements.txt
###ACTION_DELIMITER###
make setup
###ACTION_DELIMITER###
sed -i '65d' requirements.txt
###ACTION_DELIMITER###
make setup
###ACTION_DELIMITER###
apt-get install -y build-essential
###ACTION_DELIMITER###
cat requirements.txt | grep -v '^#' | grep -v '^$' | xargs -n 1 pip install
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
pip install setuptools==65.0.0
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
pip install --no-build-isolation coverage==5.3
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
pip install -r requirements.txt --no-build-isolation
###ACTION_DELIMITER###
sed -i 's/black==20.8b1/black==21.7b0/' requirements.txt && pip install -r requirements.txt
###ACTION_DELIMITER###
sed -i 's/pathspec==0.8.0/pathspec==0.8.1/' requirements.txt && pip install -r requirements.txt
###ACTION_DELIMITER###
sed -i 's/typed-ast==1.4.1/typed-ast==1.5.5/' requirements.txt && pip install -r requirements.txt
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
ln -s /usr/bin/python3 /usr/bin/python
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
export SECRET_KEY='test-secret-key' && make test
###ACTION_DELIMITER###
export SECRET_KEY='test-secret-key' && export SOCIAL_AUTH_GITHUB_KEY='dummy-key' && export SOCIAL_AUTH_GITHUB_SECRET='dummy-secret' && export GITHUB_TOKEN='dummy-token' && make test
###ACTION_DELIMITER###
sed -i 's/pytest==6.0.2/pytest==7.0.0/' requirements.txt && pip install -r requirements.txt && export SECRET_KEY='test-secret-key' && export SOCIAL_AUTH_GITHUB_KEY='dummy-key' && export SOCIAL_AUTH_GITHUB_SECRET='dummy-secret' && export GITHUB_TOKEN='dummy-token' && make test
###ACTION_DELIMITER###
sed -i 's/typing-extensions==3.7.4.3/typing-extensions==4.1.1/' requirements.txt && pip install -r requirements.txt && export SECRET_KEY='test-secret-key' && export SOCIAL_AUTH_GITHUB_KEY='dummy-key' && export SOCIAL_AUTH_GITHUB_SECRET='dummy-secret' && export GITHUB_TOKEN='dummy-token' && make test
###ACTION_DELIMITER###
sed -i 's/typing-extensions==4.1.1/typing-extensions==4.9.0/' requirements.txt && pip install -r requirements.txt && export SECRET_KEY='test-secret-key' && export SOCIAL_AUTH_GITHUB_KEY='dummy-key' && export SOCIAL_AUTH_GITHUB_SECRET='dummy-secret' && export GITHUB_TOKEN='dummy-token' && make test
###ACTION_DELIMITER###
echo 'pytest -v --cov=jobserver --cov=services --cov=tests' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'python manage.py collectstatic --no-input
pytest -v --cov=jobserver --cov=services --cov=tests' > test_commands.sh && chmod +x test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
python manage.py collectstatic --no-input
pytest -v --cov=jobserver --cov=services --cov=tests

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
python manage.py collectstatic --no-input
pytest -v --cov=jobserver --cov=services --cov=tests

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
python manage.py collectstatic --no-input
pytest -v --cov=jobserver --cov=services --cov=tests

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:22.04 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:22.04

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


@Instance.register("opensafely-core", "job_server_461_to_395")
class JOB_SERVER_461_TO_395(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re

        # Regex pattern to match test names and their statuses
        pattern = re.compile(r"(tests/[^:]+::\w+)\s+(PASSED|FAILED|SKIPPED)")
        matches = pattern.findall(log)
        for test_name, status in matches:
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status == "FAILED":
                failed_tests.add(test_name)
            elif status == "SKIPPED":
                skipped_tests.add(test_name)
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
