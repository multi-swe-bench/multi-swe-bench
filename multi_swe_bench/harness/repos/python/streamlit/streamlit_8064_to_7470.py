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
                """ls -la
###ACTION_DELIMITER###
make all
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make all
###ACTION_DELIMITER###
make all USE_CONSTRAINTS_FILE=false
###ACTION_DELIMITER###
apt-get update && apt-get install -y libmysqlclient-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y libmariadb-dev
###ACTION_DELIMITER###
make all USE_CONSTRAINTS_FILE=false
###ACTION_DELIMITER###
export MYSQLCLIENT_CFLAGS="-I/usr/include/mariadb" && export MYSQLCLIENT_LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lmariadb" && make all USE_CONSTRAINTS_FILE=false
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
export MYSQLCLIENT_CFLAGS="-I/usr/include/mariadb" && export MYSQLCLIENT_LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lmariadb" && make all USE_CONSTRAINTS_FILE=false
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && apt-get install -y nodejs && npm install -g yarn
###ACTION_DELIMITER###
export MYSQLCLIENT_CFLAGS="-I/usr/include/mariadb" && export MYSQLCLIENT_LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lmariadb" && make all USE_CONSTRAINTS_FILE=false
###ACTION_DELIMITER###
apt-get update && apt-get install -y protobuf-compiler
###ACTION_DELIMITER###
export MYSQLCLIENT_CFLAGS="-I/usr/include/mariadb" && export MYSQLCLIENT_LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lmariadb" && make all USE_CONSTRAINTS_FILE=false
###ACTION_DELIMITER###
apt-get update && apt-get install -y rsync
###ACTION_DELIMITER###
export MYSQLCLIENT_CFLAGS="-I/usr/include/mariadb" && export MYSQLCLIENT_LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lmariadb" && make all USE_CONSTRAINTS_FILE=false
###ACTION_DELIMITER###
cat << EOF > test_commands.sh
#!/bin/bash

# Run Python unit tests with verbose output and JUnit XML logs
cd lib
PYTHONPATH=. pytest -v --junitxml=test-reports/pytest/junit.xml -l tests/
cd ..

# Run integration tests
python3 scripts/run_bare_integration_tests.py

# Run CLI smoke tests
python3 scripts/cli_smoke_tests.py
EOF
###ACTION_DELIMITER###
echo -e '#!/bin/bash\n\n# Run unit tests with verbose output and JUnit logs\ncd lib\nPYTHONPATH=. pytest -v --junitxml=test-reports/pytest/junit.xml -l tests/\ncd ..\n\n# Run integration tests\npython3 scripts/run_bare_integration_tests.py\n\n# Run CLI smoke tests\npython3 scripts/cli_smoke_tests.py' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash

# Run unit tests with verbose output and JUnit logs
cd lib
PYTHONPATH=. pytest -v --junitxml=test-reports/pytest/junit.xml -l tests/
cd ..

# Run integration tests
python3 scripts/run_bare_integration_tests.py

# Run CLI smoke tests
python3 scripts/cli_smoke_tests.py

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

# Run unit tests with verbose output and JUnit logs
cd lib
PYTHONPATH=. pytest -v --junitxml=test-reports/pytest/junit.xml -l tests/
cd ..

# Run integration tests
python3 scripts/run_bare_integration_tests.py

# Run CLI smoke tests
python3 scripts/cli_smoke_tests.py

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

# Run unit tests with verbose output and JUnit logs
cd lib
PYTHONPATH=. pytest -v --junitxml=test-reports/pytest/junit.xml -l tests/
cd ..

# Run integration tests
python3 scripts/run_bare_integration_tests.py

# Run CLI smoke tests
python3 scripts/cli_smoke_tests.py

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim with actual base image
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
RUN git clone https://github.com/streamlit/streamlit.git /home/streamlit

WORKDIR /home/streamlit
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("streamlit", "streamlit_8064_to_7470")
class STREAMLIT_8064_TO_7470(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re
        # import json  # Not used in this implementation
        # Regex pattern to match test lines with status
        pattern = re.compile(r'^\s*(?:\[\s*\d+\s*\]\s*)?(tests/.*?)\s+(?:\x1b\[[0-9;]*m)*\s*(PASSED|SKIPPED|FAILED)\s*(?:\x1b\[[0-9;]*m)*\s+\[\s*\d+%\s*\]')
        for line in log.splitlines():
            match = pattern.match(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
                elif status == 'FAILED':
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
