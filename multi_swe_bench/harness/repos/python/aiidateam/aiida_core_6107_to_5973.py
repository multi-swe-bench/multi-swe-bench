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
        return "aiidateam/aiida-prerequisites:0.7.0"
    
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
pip install .[tests]
###ACTION_DELIMITER###
echo 'pytest --no-header -rA -v --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
service postgresql start
###ACTION_DELIMITER###
apt-get update && apt-get install -y postgresql
###ACTION_DELIMITER###
pg_ctlcluster 14 main start
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install .[tests,rest]
###ACTION_DELIMITER###
verdi quicksetup --non-interactive --profile test --email test@example.com --first-name Test --last-name User --institution TestInst --database-engine postgresql --database-name aiida_test --database-username aiida_test --database-password aiida_test --database-host localhost --database-port 5432
###ACTION_DELIMITER###
verdi quicksetup --non-interactive --profile test --email test@example.com --first-name Test --last-name User --institution TestInst --db-engine postgresql --db-name aiida_test --db-username aiida_test --db-password aiida_test --db-host localhost --db-port 5432
###ACTION_DELIMITER###
verdi quicksetup --non-interactive --profile test --email test@example.com --first-name Test --last-name User --institution TestInst --db-engine postgresql_psycopg2 --db-name aiida_test --db-username aiida_test --db-password aiida_test --db-host localhost --db-port 5432
###ACTION_DELIMITER###
apt-get update && apt-get install -y sudo
###ACTION_DELIMITER###
verdi quicksetup --non-interactive --profile test --email test@example.com --first-name Test --last-name User --institution TestInst --db-engine postgresql_psycopg2 --db-name aiida_test --db-username aiida_test --db-password aiida_test --db-host localhost --db-port 5432
###ACTION_DELIMITER###
echo 'export AIIDA_PROFILE=test && pytest --no-header -rA -v --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install .[tests,rest,atomic_tools]
###ACTION_DELIMITER###
pip install pymatgen
###ACTION_DELIMITER###
pip install tabulate==0.8.10
###ACTION_DELIMITER###
pip install pymatgen==2022.11.7
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential cython3
###ACTION_DELIMITER###
pip install pymatgen==2022.11.7
###ACTION_DELIMITER###
pip install cython==0.29.32 && pip install pymatgen==2022.11.7
###ACTION_DELIMITER###
apt-get update && apt-get install -y libopenblas-dev liblapack-dev libffi-dev
###ACTION_DELIMITER###
pip install --no-build-isolation pymatgen==2022.11.7
###ACTION_DELIMITER###
pytest tests/orm/nodes/data/test_jsonable.py -v
###ACTION_DELIMITER###
echo -e 'export AIIDA_PROFILE=test\nexport PGDATABASE=aiida_test\nexport PGUSER=aiida_test\nexport PGPASSWORD=aiida_test\nexport PGHOST=localhost\nexport PGPORT=5432\npytest --no-header -rA -v --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'export AIIDA_PROFILE=test\nexport PGTEST_DATABASE=aiida_test\nexport PGTEST_USER=aiida_test\nexport PGTEST_PASSWORD=aiida_test\nexport PGTEST_HOST=localhost\nexport PGTEST_PORT=5432\npytest --no-header -rA -v --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export AIIDA_PROFILE=test\nexport PGTEST_USE_EXISTING=1\nexport PGTEST_DATABASE=aiida_test\nexport PGTEST_USER=aiida_test\nexport PGTEST_PASSWORD=aiida_test\nexport PGTEST_HOST=localhost\nexport PGTEST_PORT=5432\npytest --no-header -rA -v --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
verdi profile show test && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nuseradd -m aiida\nchown -R aiida:aiida /home/aiida-core\nsu - aiida -c "export AIIDA_PROFILE=test\nexport PGTEST_USE_EXISTING=1\nexport PGTEST_DATABASE=aiida_test\nexport PGTEST_USER=aiida_test\nexport PGTEST_PASSWORD=aiida_test\nexport PGTEST_HOST=localhost\nexport PGTEST_PORT=5432\npytest --no-header -rA -v --tb=no -p no:cacheprovider tests/"' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
useradd -m aiida || true
chown -R aiida:aiida /home/aiida-core
su - aiida -c "cd /home/aiida-core && export AIIDA_PROFILE=test && export PGTEST_USE_EXISTING=1 && export PGTEST_DATABASE=aiida_test && export PGTEST_USER=aiida_test && export PGTEST_PASSWORD=aiida_test && export PGTEST_HOST=localhost && export PGTEST_PORT=5432 && pytest --no-header -rA -v --tb=no -p no:cacheprovider tests/"' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
useradd -m aiida || true
chown -R aiida:aiida /home/aiida-core
su - aiida -c "cd /home/aiida-core && ulimit -n 4096 && export AIIDA_PROFILE=test && export PGTEST_USE_EXISTING=1 && export PGTEST_DATABASE=aiida_test && export PGTEST_USER=aiida_test && export PGTEST_PASSWORD=aiida_test && export PGTEST_HOST=localhost && export PGTEST_PORT=5432 && pytest --no-header -rA -v --tb=no -p no:cacheprovider tests/"' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
useradd -m aiida || true
chown -R aiida:aiida /home/aiida-core
su - aiida -c "cd /home/aiida-core && ulimit -n 4096 && export AIIDA_PROFILE=test && export PGTEST_USE_EXISTING=1 && export PGTEST_DATABASE=aiida_test && export PGTEST_USER=aiida_test && export PGTEST_PASSWORD=aiida_test && export PGTEST_HOST=localhost && export PGTEST_PORT=5432 && pytest --no-header -rA -v --tb=no -p no:cacheprovider tests/"

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
useradd -m aiida || true
chown -R aiida:aiida /home/aiida-core
su - aiida -c "cd /home/aiida-core && ulimit -n 4096 && export AIIDA_PROFILE=test && export PGTEST_USE_EXISTING=1 && export PGTEST_DATABASE=aiida_test && export PGTEST_USER=aiida_test && export PGTEST_PASSWORD=aiida_test && export PGTEST_HOST=localhost && export PGTEST_PORT=5432 && pytest --no-header -rA -v --tb=no -p no:cacheprovider tests/"

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
useradd -m aiida || true
chown -R aiida:aiida /home/aiida-core
su - aiida -c "cd /home/aiida-core && ulimit -n 4096 && export AIIDA_PROFILE=test && export PGTEST_USE_EXISTING=1 && export PGTEST_DATABASE=aiida_test && export PGTEST_USER=aiida_test && export PGTEST_PASSWORD=aiida_test && export PGTEST_HOST=localhost && export PGTEST_PORT=5432 && pytest --no-header -rA -v --tb=no -p no:cacheprovider tests/"

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

# Choose an appropriate base image based on the project's requirements - replace aiidateam/aiida-prerequisites:0.7.0 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM aiidateam/aiida-prerequisites:0.7.0

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


@Instance.register("aiidateam", "aiida_core_6107_to_5973")
class AIIDA_CORE_6107_TO_5973(Instance):
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
        # Regex patterns to match test cases and statuses
        pattern1 = re.compile(r'^([^\s]+)\s+(PASSED|FAILED|SKIPPED|ERROR)\s+.*?(\[\s*\d+%\])?$')  # Test name (no spaces) followed by status
        pattern2 = re.compile(r'^(PASSED|FAILED|SKIPPED|ERROR)\s+([^\s]+)\s*.*$')  # Status followed by test name (no spaces)
        pattern3 = re.compile(r'^([^\s]+)\s+SKIPPED\s+\(\.\.\.\).*$')  # Test name (no spaces) followed by SKIPPED (...)
        lines = log.split('\n')
        for line in lines:
            line = line.strip()
            # Remove the [line_number] prefix if present
            prefix_match = re.match(r'^\[\s*\d+\]\s*(.*)$', line)
            if prefix_match:
                test_info = prefix_match.group(1).strip()
            else:
                test_info = line.strip()
            if not test_info:
                continue  # skip empty lines
            # Check against patterns
            match = pattern1.match(test_info)
            if match:
                test_name = match.group(1).strip()
                status = match.group(2)
            else:
                match = pattern2.match(test_info)
                if match:
                    status = match.group(1)
                    test_name = match.group(2).strip()
                else:
                    match = pattern3.match(test_info)
                    if match:
                        test_name = match.group(1).strip()
                        status = 'SKIPPED'
                    else:
                        continue  # no match
            # Categorize the test based on status
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
