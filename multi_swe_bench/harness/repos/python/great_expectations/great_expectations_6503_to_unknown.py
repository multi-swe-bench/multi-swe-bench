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
        return "python:3.8"
    
    def image_prefix(self) -> str:
        return "envagent"
       
    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:
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
                """apt-get update && apt-get install -y postgresql libpq-dev
###ACTION_DELIMITER###
service postgresql start
###ACTION_DELIMITER###
su - postgres -c 'createdb great_expectations_test' && su - postgres -c "psql -c \"ALTER USER postgres PASSWORD 'postgres';\""
###ACTION_DELIMITER###
ls
###ACTION_DELIMITER###
ls scripts
###ACTION_DELIMITER###
su - postgres -c 'createdb test_ci'
###ACTION_DELIMITER###
sed -i 's/local   all             postgres                                peer/local   all             postgres                                trust/' /etc/postgresql/15/main/pg_hba.conf && service postgresql restart
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider -m "not e2e" --random-order --postgresql --cloud --ignore=tests/cli --ignore=tests/integration/usage_statistics' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install --requirement requirements-dev.txt --constraint constraints-dev.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
###ACTION_DELIMITER###
sed -i 's/^# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
export POSTGRES_USER=postgres POSTGRES_PASSWORD='' POSTGRES_DB=test_ci POSTGRES_HOST=localhost POSTGRES_PORT=5432 && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/local   all             all                                     peer/local   all             all                                     trust/' /etc/postgresql/15/main/pg_hba.conf && service postgresql restart && psql -U postgres -d test_ci -c 'SELECT 1;'
###ACTION_DELIMITER###
sed -i 's/host    all             all             127.0.0.1\/32            scram-sha-256/host    all             all             127.0.0.1\/32            trust/' /etc/postgresql/15/main/pg_hba.conf && sed -i 's/host    all             all             ::1\/128                 scram-sha-256/host    all             all             ::1\/128                 trust/' /etc/postgresql/15/main/pg_hba.conf && service postgresql restart
###ACTION_DELIMITER###
export DATABASE_URL='postgresql://postgres@localhost/test_ci' && bash test_commands.sh
###ACTION_DELIMITER###
export TZ=UTC && bash test_commands.sh
###ACTION_DELIMITER###
export LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 && bash test_commands.sh
###ACTION_DELIMITER###
locale -a && locale-gen en_US.UTF-8 && update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/--ignore=tests\/integration\/usage_statistics/--ignore=tests\/integration\/usage_statistics -k "not test_expectations_v3_api"/' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/--ignore=tests\/integration\/usage_statistics/--ignore=tests\/integration\/usage_statistics --ignore=tests\/test_definitions\/test_expectations_v3_api.py/' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y unixodbc unixodbc-dev openjdk-11-jre && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-17-jre libodbc2 && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider -m "not e2e" --random-order --postgresql --cloud --ignore=tests/cli --ignore=tests/integration/usage_statistics --ignore=tests/test_definitions/test_expectations_v3_api.py' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v --no-header -rA --tb=no -p no:cacheprovider -m "not e2e" --random-order --postgresql --cloud --ignore=tests/cli --ignore=tests/integration/usage_statistics --ignore=tests/test_definitions/test_expectations_v3_api.py

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
pytest -v --no-header -rA --tb=no -p no:cacheprovider -m "not e2e" --random-order --postgresql --cloud --ignore=tests/cli --ignore=tests/integration/usage_statistics --ignore=tests/test_definitions/test_expectations_v3_api.py

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn  /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
pytest -v --no-header -rA --tb=no -p no:cacheprovider -m "not e2e" --random-order --postgresql --cloud --ignore=tests/cli --ignore=tests/integration/usage_statistics --ignore=tests/test_definitions/test_expectations_v3_api.py

""".format(
                    pr=self.pr
                ),
            ),
        ]

    def dockerfile(self) -> str:
        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        dockerfile_content = """
# This is a template for creating a Dockerfile to test patches
# LLM should fill in the appropriate values based on the context

# Choose an appropriate base image based on the project's requirements - replace python:3.8 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.8

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
RUN git clone https://github.com/great-expectations/great_expectations.git /home/great_expectations

WORKDIR /home/great_expectations
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("great-expectations", "great_expectations_6503_to_unknown")
class GREAT_EXPECTATIONS_6503_TO_UNKNOWN(Instance):
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
        import json
        # Regex pattern to match test cases with status
        pattern = r'^(tests/.*?) (PASSED|FAILED|SKIPPED|XFAIL) \[\s*\d+%\]$|^(PASSED|FAILED|SKIPPED|XFAIL) (tests/.*)$'
        matches = re.finditer(pattern, log, re.MULTILINE)
        for match in matches:
            if match.group(1) is not None:
                test_name = match.group(1).strip()
                status = match.group(2)
            else:
                test_name = match.group(4).strip()
                status = match.group(3)
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
            elif status == 'XFAIL':
                failed_tests.add(test_name)
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
