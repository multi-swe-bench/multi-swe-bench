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
        return "aiidateam/aiida-prerequisites:0.4.0"
    
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
ls -a
###ACTION_DELIMITER###
ls -a .github
###ACTION_DELIMITER###
ls .github/workflows
###ACTION_DELIMITER###
ls requirements
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
pip install -r requirements/requirements-py-3.8.txt
###ACTION_DELIMITER###

###ACTION_DELIMITER###

###ACTION_DELIMITER###
echo -e '#!/bin/bash
AIIDA_TEST_PROFILE=test_aiida pytest --cov aiida --verbose tests -m "not nightly"' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install .
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
verdi quicksetup --non-interactive --profile test_aiida --email test@example.com --first-name Test --last-name User --institution Test
###ACTION_DELIMITER###
apt-get update && apt-get install -y sudo
###ACTION_DELIMITER###
verdi quicksetup --non-interactive --profile test_aiida --email test@example.com --first-name Test --last-name User --institution Test
###ACTION_DELIMITER###
apt-get update && apt-get install -y postgresql postgresql-contrib && service postgresql start
###ACTION_DELIMITER###
sudo -u postgres psql -c "CREATE USER aiida WITH PASSWORD 'aiida';" && sudo -u postgres psql -c "CREATE DATABASE aiida_db OWNER aiida;" && verdi quicksetup --non-interactive --profile test_aiida --email test@example.com --first-name Test --last-name User --institution Test --db-user aiida --db-name aiida_db --db-password aiida --db-host localhost
###ACTION_DELIMITER###
sudo -u postgres psql -c "CREATE USER aiida WITH PASSWORD 'aiida';" && sudo -u postgres psql -c "CREATE DATABASE aiida_db OWNER aiida;" && verdi quicksetup --non-interactive --profile test_aiida --email test@example.com --first-name Test --last-name User --institution Test --db-username aiida --db-name aiida_db --db-password aiida --db-host localhost
###ACTION_DELIMITER###
sudo -u postgres psql -c "CREATE DATABASE IF NOT EXISTS aiida_db OWNER aiida;" && verdi quicksetup --non-interactive --profile test_aiida --email test@example.com --first-name Test --last-name User --institution Test --db-username aiida --db-name aiida_db --db-password aiida --db-host localhost
###ACTION_DELIMITER###
sudo -u postgres psql -c "CREATE DATABASE aiida_db OWNER aiida;" || true && verdi quicksetup --non-interactive --profile test_aiida --email test@example.com --first-name Test --last-name User --institution Test --db-username aiida --db-name aiida_db --db-password aiida --db-host localhost
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install --force-reinstall pymatgen
###ACTION_DELIMITER###
pip install pyyaml~=5.4 importlib-metadata~=4.3 pytz~=2021.1 tabulate~=0.8.5
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y rabbitmq-server && service rabbitmq-server start && bash test_commands.sh
###ACTION_DELIMITER###
verdi status
###ACTION_DELIMITER###
verdi daemon start && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y openssh-server && service ssh start
###ACTION_DELIMITER###
ssh-keygen -t rsa -N '' -f ~/.ssh/id_rsa && cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh && service ssh restart && bash test_commands.sh
###ACTION_DELIMITER###
AIIDA_TEST_PROFILE=test_aiida pytest --cov aiida --verbose tests/test_calculation_node.py
###ACTION_DELIMITER###
verdi profile delete -f test_aiida && verdi quicksetup --non-interactive --test-profile --profile test_aiida --email test@example.com --first-name Test --last-name User --institution Test --db-username aiida --db-name aiida_db --db-password aiida --db-host localhost
###ACTION_DELIMITER###
verdi daemon stop && sudo -u postgres psql -c 'SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE datname = ''aiida_db'' AND pid <> pg_backend_pid();' && verdi profile delete -f test_aiida && verdi quicksetup --non-interactive --test-profile --profile test_aiida --email test@example.com --first-name Test --last-name User --institution Test --db-username aiida --db-name aiida_db --db-password aiida --db-host localhost
###ACTION_DELIMITER###
verdi daemon stop && sudo -u postgres psql -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE datname = 'aiida_db' AND pid <> pg_backend_pid();" && verdi profile delete -f test_aiida && verdi quicksetup --non-interactive --test-profile --profile test_aiida --email test@example.com --first-name Test --last-name User --institution Test --db-username aiida --db-name aiida_db --db-password aiida --db-host localhost
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
AIIDA_TEST_PROFILE=test_aiida pytest --cov aiida --verbose tests -m "not nightly"

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
AIIDA_TEST_PROFILE=test_aiida pytest --cov aiida --verbose tests -m "not nightly"

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
AIIDA_TEST_PROFILE=test_aiida pytest --cov aiida --verbose tests -m "not nightly"

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
FROM aiidateam/aiida-prerequisites:0.4.0

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
RUN git clone https://github.com/aiidateam/aiida-core.git /home/aiida-core

WORKDIR /home/aiida-core
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("aiidateam", "aiida_core_5549_to_5444")
class AIIDA_CORE_5549_TO_5444(Instance):
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
        # Regex patterns to match test lines
        # Pattern 1: Test name followed by status and [percentage]
        pattern1 = re.compile(r'^(.*?)\s+(PASSED|FAILED|SKIPPED|ERROR)\s+\[.*$')
        # Pattern 2: Status followed by test name
        pattern2 = re.compile(r'^(PASSED|FAILED|SKIPPED|ERROR)\s+(.*)$')
        for line in log.split('\n'):
            line = line.strip()
            match1 = pattern1.match(line)
            match2 = pattern2.match(line)
            if match1:
                test_name = match1.group(1).strip()
                status = match1.group(2).strip()
            elif match2:
                status = match2.group(1).strip()
                test_name = match2.group(2).strip()
            else:
                continue
            # Clean test name by removing any trailing error messages
            if ' - ' in test_name:
                test_name = test_name.split(' - ')[0].strip()
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
