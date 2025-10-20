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
        return "python:3.11-slim"
    
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
                """cat setup.py
###ACTION_DELIMITER###
pip list
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
python -c 'from google.cloud import environment_vars'
###ACTION_DELIMITER###

###ACTION_DELIMITER###
ls google/cloud
###ACTION_DELIMITER###
pip uninstall -y google-cloud-ndb && pip install .
###ACTION_DELIMITER###
pip show -f google-api-core | grep environment_vars.py
###ACTION_DELIMITER###
find /usr/local/lib/python3.11/site-packages -name 'environment_vars.py'
###ACTION_DELIMITER###
sed -i 's/from google.cloud import environment_vars/from google.auth import environment_vars/' tests/conftest.py
###ACTION_DELIMITER###
python -c 'from google.auth import environment_vars'
###ACTION_DELIMITER###
pytest --verbose --no-header -rA --tb=no -p no:cacheprovider tests/unit tests/system
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
pytest --verbose --no-header -rA --tb=no -p no:cacheprovider tests/unit tests/system
###ACTION_DELIMITER###
pip install six
###ACTION_DELIMITER###
pytest --verbose --no-header -rA --tb=no -p no:cacheprovider tests/unit tests/system
###ACTION_DELIMITER###
pytest -vv --no-header -rA --tb=short -p no:cacheprovider tests/unit tests/system
###ACTION_DELIMITER###
ls tests
###ACTION_DELIMITER###
find . -name 'test_utils'
###ACTION_DELIMITER###
PYTHONPATH=. pytest -vv --no-header -rA --tb=short -p no:cacheprovider tests/unit tests/system
###ACTION_DELIMITER###
ls
###ACTION_DELIMITER###
ls testing
###ACTION_DELIMITER###
pip install google-cloud-testutils
###ACTION_DELIMITER###
PYTHONPATH=. pytest -vv --no-header -rA --tb=short -p no:cacheprovider tests/unit tests/system
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl gnupg
###ACTION_DELIMITER###
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
###ACTION_DELIMITER###
echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y google-cloud-sdk
###ACTION_DELIMITER###
apt-get install -y google-cloud-cli-datastore-emulator
###ACTION_DELIMITER###
gcloud beta emulators datastore start --project=testing-project --host-port=localhost:8081 &
###ACTION_DELIMITER###
export DATASTORE_EMULATOR_HOST=localhost:8081 && export GOOGLE_CLOUD_PROJECT=testing-project
###ACTION_DELIMITER###
PYTHONPATH=. pytest -vv --no-header -rA --tb=short -p no:cacheprovider tests/unit tests/system
###ACTION_DELIMITER###
pkill -f datastore-emulator; gcloud emulators datastore start --project=testing --host-port=localhost:8081 & sleep 5; $(gcloud emulators datastore env-init); pytest -vv --no-header -rA --tb=short -p no:cacheprovider tests/unit tests/system
###ACTION_DELIMITER###
pkill -f datastore-emulator; gcloud beta emulators datastore start --project=testing --host-port=localhost:8081 & sleep 10; eval $(gcloud beta emulators datastore env-init); pytest -vv --no-header -rA --tb=short -p no:cacheprovider tests/unit tests/system
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-21-jre && update-alternatives --set java /usr/lib/jvm/java-21-openjdk-amd64/bin/java
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bookworm-backports main' | tee -a /etc/apt/sources.list.d/backports.list && apt-get update && apt-get install -y -t bookworm-backports openjdk-21-jre && update-alternatives --set java /usr/lib/jvm/java-21-openjdk-amd64/bin/java
###ACTION_DELIMITER###
curl -fsSL https://packages.adoptium.net/artifactory/api/gpg/key/public | gpg --dearmor -o /usr/share/keyrings/adoptium.gpg && echo "deb [signed-by=/usr/share/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print$2}' /etc/os-release) main" | tee /etc/apt/sources.list.d/adoptium.list && apt-get update && apt-get install -y temurin-21-jre && update-alternatives --set java /usr/lib/jvm/temurin-21-jre/bin/java && pkill -f datastore-emulator; gcloud beta emulators datastore start --project=testing --host-port=localhost:8081 & sleep 10; eval $(gcloud beta emulators datastore env-init); pytest -vv --no-header -rA --tb=short -p no:cacheprovider tests/unit tests/system
###ACTION_DELIMITER###
echo -e '#!/bin/bash

gcloud beta emulators datastore start --project=testing --host-port=localhost:8081 &
EMULATOR_PID=$!
sleep 10
eval $(gcloud beta emulators datastore env-init)
pytest -vv --no-header -rA --tb=short -p no:cacheprovider tests/unit tests/system
kill $EMULATOR_PID' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash

# Kill existing processes on port 8081
fuser -k 8081/tcp || true

# Start emulator with project matching test expectations
gcloud beta emulators datastore start --project=testing --host-port=localhost:8081 &
EMULATOR_PID=$!

# Wait for emulator to initialize
sleep 15

eval $(gcloud beta emulators datastore env-init)

# Run tests with verbose output
pytest -vv --no-header -rA --tb=short -p no:cacheprovider tests/unit tests/system

# Clean up emulator
kill $EMULATOR_PID' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash

# Kill existing processes on port 8081
fuser -k 8081/tcp || true

# Start emulator with project matching test expectations
gcloud beta emulators datastore start --project=testing --host-port=localhost:8081 &
EMULATOR_PID=$!

# Wait for emulator to initialize
sleep 15

eval $(gcloud beta emulators datastore env-init)

# Run tests with verbose output
pytest -vv --no-header -rA --tb=short -p no:cacheprovider tests/unit tests/system

# Clean up emulator
kill $EMULATOR_PID

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

# Kill existing processes on port 8081
fuser -k 8081/tcp || true

# Start emulator with project matching test expectations
gcloud beta emulators datastore start --project=testing --host-port=localhost:8081 &
EMULATOR_PID=$!

# Wait for emulator to initialize
sleep 15

eval $(gcloud beta emulators datastore env-init)

# Run tests with verbose output
pytest -vv --no-header -rA --tb=short -p no:cacheprovider tests/unit tests/system

# Clean up emulator
kill $EMULATOR_PID

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

# Kill existing processes on port 8081
fuser -k 8081/tcp || true

# Start emulator with project matching test expectations
gcloud beta emulators datastore start --project=testing --host-port=localhost:8081 &
EMULATOR_PID=$!

# Wait for emulator to initialize
sleep 15

eval $(gcloud beta emulators datastore env-init)

# Run tests with verbose output
pytest -vv --no-header -rA --tb=short -p no:cacheprovider tests/unit tests/system

# Clean up emulator
kill $EMULATOR_PID

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

# Choose an appropriate base image based on the project's requirements - replace python:3.11-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.11-slim

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
RUN git clone https://github.com/googleapis/python-ndb.git /home/python-ndb

WORKDIR /home/python-ndb
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("googleapis", "python_ndb_882_to_714")
class PYTHON_NDB_882_TO_714(Instance):
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
        # Regex patterns to match test names and statuses
        # Pattern 1: Test name followed by status (e.g., "tests/...::test_name PASSED")
        pattern1 = re.compile(r'(tests/[\w/]+\.py::[\w\[\]:-]+)\s+(PASSED|FAILED|SKIPPED)')
        # Pattern 2: Status followed by test name (e.g., "PASSED tests/...::test_name")
        pattern2 = re.compile(r'(PASSED|FAILED|SKIPPED)\s+(tests/[\w/]+\.py::[\w\[\]:-]+)')
        for line in log.split('\n'):
            line = line.strip()
            # Check for pattern1
            match = pattern1.search(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
            else:
                # Check for pattern2
                match = pattern2.search(line)
                if match:
                    status = match.group(1)
                    test_name = match.group(2)
                else:
                    continue  # No match in this line
            # Normalize status to uppercase (though logs seem to use uppercase)
            status = status.upper()
            # Add to the appropriate set
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
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
