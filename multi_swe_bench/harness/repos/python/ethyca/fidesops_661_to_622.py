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
                """ls
###ACTION_DELIMITER###
./venv/bin/pip install -e .
###ACTION_DELIMITER###
apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.10 python3.10-venv
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.10 python3.10-venv
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y && apt-get update
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y && apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.10 python3.10-venv
###ACTION_DELIMITER###
rm -rf venv && python3.10 -m venv venv
###ACTION_DELIMITER###
./venv/bin/pip install --upgrade pip && ./venv/bin/pip install -r requirements.txt
###ACTION_DELIMITER###
./venv/bin/pip install cython && ./venv/bin/pip install -r requirements.txt
###ACTION_DELIMITER###
./venv/bin/pip uninstall -y cython && ./venv/bin/pip install cython==0.29.36 && ./venv/bin/pip install -r requirements.txt
###ACTION_DELIMITER###
./venv/bin/pip install -e .
###ACTION_DELIMITER###
apt-get install -y libssl-dev libffi-dev
###ACTION_DELIMITER###
./venv/bin/pip install --upgrade setuptools && ./venv/bin/pip install -r requirements.txt
###ACTION_DELIMITER###
./venv/bin/pip install setuptools==58.0.0 && ./venv/bin/pip install -r requirements.txt
###ACTION_DELIMITER###
./venv/bin/pip install --no-build-isolation -r requirements.txt
###ACTION_DELIMITER###
./venv/bin/pip install wheel && ./venv/bin/pip install --no-build-isolation -r requirements.txt
###ACTION_DELIMITER###
apt-get install -y gcc build-essential
###ACTION_DELIMITER###
./venv/bin/pip install --no-build-isolation -r requirements.txt
###ACTION_DELIMITER###
apt-get install -y python3.10-dev
###ACTION_DELIMITER###
./venv/bin/pip install --no-build-isolation -r requirements.txt
###ACTION_DELIMITER###
echo './venv/bin/pytest -v -rA --tb=short' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
./venv/bin/pip install -e .
###ACTION_DELIMITER###
echo 'PYTHONPATH=. ./venv/bin/pytest -v -rA --tb=short' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
./venv/bin/pip install toml
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
./venv/bin/pip install --force-reinstall numpy==1.21.6
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
./venv/bin/pip install faker
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
./venv/bin/pip install requests-mock
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
./venv/bin/pip install pytest-xdist && echo 'PYTHONPATH=. ./venv/bin/pytest -v -rA --tb=short -n auto' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y redis-server && service redis-server start && bash test_commands.sh
###ACTION_DELIMITER###
redis-cli ping
###ACTION_DELIMITER###
echo 'PYTHONPATH=. REDIS_URL=redis://localhost:6379 ./venv/bin/pytest -v -rA --tb=short -n auto' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/HOST = "redis"/HOST = "localhost"/' fidesops.toml && sed -i 's/PASSWORD = "testpassword"/PASSWORD = ""/' fidesops.toml && sed -i 's/redis:\/\/:testpassword@redis:6379/redis:\/\/localhost:6379/' fidesops.toml
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y postgresql postgresql-contrib && service postgresql start && su - postgres -c 'createdb test' && su - postgres -c "psql -c \"ALTER USER postgres WITH PASSWORD '216f4b49bea5da4f84f05288258471852c3e325cd336821097e1e65ff92b528a';\"" && sed -i 's/SERVER = "db"/SERVER = "localhost"/' fidesops.toml && echo -e "\n[testing]\nTESTING = true" >> fidesops.toml && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/\[testing\]/d; /TESTING = true/d' fidesops.toml && bash test_commands.sh
###ACTION_DELIMITER###
echo '127.0.0.1 db' >> /etc/hosts && export TESTING=true && ./venv/bin/alembic upgrade head && bash test_commands.sh
###ACTION_DELIMITER###
./venv/bin/alembic upgrade head --config src/alembic.ini && bash test_commands.sh
###ACTION_DELIMITER###
./venv/bin/alembic -c src/alembic.ini upgrade head && bash test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
PYTHONPATH=. REDIS_URL=redis://localhost:6379 ./venv/bin/pytest -v -rA --tb=short -n auto

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
PYTHONPATH=. REDIS_URL=redis://localhost:6379 ./venv/bin/pytest -v -rA --tb=short -n auto

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
PYTHONPATH=. REDIS_URL=redis://localhost:6379 ./venv/bin/pytest -v -rA --tb=short -n auto

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
RUN git clone https://github.com/ethyca/fidesops.git /home/fidesops

WORKDIR /home/fidesops
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ethyca", "fidesops_661_to_622")
class FIDESOPS_661_TO_622(Instance):
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
        # Regex pattern to match test status and name
        pattern = re.compile(r'(PASSED|FAILED|ERROR|SKIPPED)\s+(tests/[\w/]+\.py::[\w:]+)')
        for match in pattern.finditer(log):
            status = match.group(1)
            test_name = match.group(2)
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ('FAILED', 'ERROR'):
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
