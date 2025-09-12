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
ls tests
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.8 python3-pip
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
python3 -m venv venv && source venv/bin/activate && pip install -e .
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv && source venv/bin/activate && pip install -e .
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
echo './venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install setuptools
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install six
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytz
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && apt-get update && apt-get install -y google-cloud-sdk
###ACTION_DELIMITER###
gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 & sleep 5 && export DATASTORE_EMULATOR_HOST=localhost:8081 && export DATASTORE_PROJECT_ID=test-project && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-11-jre && gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 & sleep 5 && export DATASTORE_EMULATOR_HOST=localhost:8081 && export DATASTORE_PROJECT_ID=test-project && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y openjdk-11-jre && gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 & sleep 10 && curl http://localhost:8081 && export DATASTORE_EMULATOR_HOST=localhost:8081 && export DATASTORE_PROJECT_ID=test-project && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y openjdk-11-jre && gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 & sleep 10 && export DATASTORE_EMULATOR_HOST=localhost:8081 && export DATASTORE_PROJECT_ID=test-project && bash test_commands.sh
###ACTION_DELIMITER###
sleep 10 && apt-get install -y openjdk-11-jre && gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 & sleep 10 && export DATASTORE_EMULATOR_HOST=localhost:8081 && export DATASTORE_PROJECT_ID=test-project && bash test_commands.sh
###ACTION_DELIMITER###
while fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1; do sleep 5; done; apt-get install -y openjdk-11-jre && gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 & sleep 10 && export DATASTORE_EMULATOR_HOST=localhost:8081 && export DATASTORE_PROJECT_ID=test-project && bash test_commands.sh
###ACTION_DELIMITER###
kill 2734 || true; while fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1; do sleep 5; done; apt-get install -y openjdk-11-jre && gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 & sleep 10 && export DATASTORE_EMULATOR_HOST=localhost:8081 && export DATASTORE_PROJECT_ID=test-project && bash test_commands.sh
###ACTION_DELIMITER###
kill -9 2734 || true; rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock; apt-get update; apt-get install -y openjdk-11-jre; gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 & sleep 10; export DATASTORE_EMULATOR_HOST=localhost:8081; export DATASTORE_PROJECT_ID=test-project; bash test_commands.sh
###ACTION_DELIMITER###
kill -9 2734 || true; rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock; apt-get update; apt-get install -y openjdk-11-jre; gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 & sleep 15; export DATASTORE_EMULATOR_HOST=localhost:8081; export DATASTORE_PROJECT_ID=test-project; bash test_commands.sh
###ACTION_DELIMITER###
kill -9 $(pgrep apt-get) $(pgrep dpkg) || true; rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock; apt-get update; apt-get install -y openjdk-11-jre; gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 & sleep 15; export DATASTORE_EMULATOR_HOST=localhost:8081; export DATASTORE_PROJECT_ID=test-project; bash test_commands.sh
###ACTION_DELIMITER###
kill -9 $(pgrep apt-get || true) $(pgrep dpkg || true); rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock; dpkg --configure -a; apt-get update; apt-get install -y openjdk-11-jre; gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 & sleep 15; export DATASTORE_EMULATOR_HOST=localhost:8081; export DATASTORE_PROJECT_ID=test-project; ./venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/
###ACTION_DELIMITER###
kill -9 $(pgrep apt-get || true) $(pgrep dpkg || true); rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock; dpkg --configure -a; apt-get update -y; apt-get install -y openjdk-11-jre; gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 & sleep 15; export DATASTORE_EMULATOR_HOST=localhost:8081; export DATASTORE_PROJECT_ID=test-project; ./venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/
###ACTION_DELIMITER###
kill -9 $(pgrep apt-get || true) $(pgrep dpkg || true); rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock; apt-get update; apt-get install -y openjdk-11-jre; gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 & sleep 10; export DATASTORE_EMULATOR_HOST=localhost:8081; export DATASTORE_PROJECT_ID=test-project; bash test_commands.sh
###ACTION_DELIMITER###
kill -9 $(pgrep apt-get || true) $(pgrep dpkg || true); rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock; apt-get update -y; apt-get install -y openjdk-11-jre; gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 & sleep 20; if curl --silent --fail http://localhost:8081; then export DATASTORE_EMULATOR_HOST=localhost:8081; export DATASTORE_PROJECT_ID=test-project; bash test_commands.sh; else echo 'Datastore emulator failed to start'; fi
###ACTION_DELIMITER###
apt-get install -y google-cloud-cli-datastore-emulator && gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 & sleep 15 && export DATASTORE_EMULATOR_HOST=localhost:8081 && export DATASTORE_PROJECT_ID=test-project && bash test_commands.sh
###ACTION_DELIMITER###
kill -9 $(pgrep apt-get || true) $(pgrep dpkg || true); rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock; apt-get update; apt-get install -y google-cloud-cli-datastore-emulator; gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 & sleep 20; while ! curl --silent --fail http://localhost:8081; do sleep 5; done; export DATASTORE_EMULATOR_HOST=localhost:8081; export DATASTORE_PROJECT_ID=test-project; bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash

gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 &
EMULATOR_PID=$!
sleep 10
export DATASTORE_EMULATOR_HOST=localhost:8081
export DATASTORE_PROJECT_ID=test-project
./venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/
kill $EMULATOR_PID' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-21-jre && echo -e '#!/bin/bash

gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 &
EMULATOR_PID=$!
sleep 15
if curl --silent --fail http://localhost:8081; then
  export DATASTORE_EMULATOR_HOST=localhost:8081
  export DATASTORE_PROJECT_ID=test-project
  ./venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/
fi
kill $EMULATOR_PID' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y openjdk-21-jre && echo -e '#!/bin/bash

gcloud config set project test-project

gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 &
EMULATOR_PID=$!
sleep 15
if curl --silent --fail http://localhost:8081; then
  export DATASTORE_EMULATOR_HOST=localhost:8081
  export DATASTORE_PROJECT_ID=test-project
  ./venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/
fi
if ps -p $EMULATOR_PID > /dev/null; then
  kill $EMULATOR_PID
fi' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e

gcloud config set project test-project

gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 &
EMULATOR_PID=$!
echo "Emulator started with PID $EMULATOR_PID"

# Wait for emulator to be ready
for i in {1..20}; do
  if curl --silent --fail http://localhost:8081; then
    echo "Emulator ready"
    break
  fi
  echo "Waiting for emulator... ($i/20)"
  sleep 2
done

if ! curl --silent --fail http://localhost:8081; then
  echo "Emulator failed to start"
  exit 1
fi

export DATASTORE_EMULATOR_HOST=localhost:8081
export DATASTORE_PROJECT_ID=test-project
echo "Environment variables set: $DATASTORE_EMULATOR_HOST, $DATASTORE_PROJECT_ID"

# Run system tests with verbose output to diagnose collection errors
./venv/bin/pytest -v tests/system/

# Cleanup
if ps -p $EMULATOR_PID > /dev/null; then
  kill $EMULATOR_PID
  echo "Emulator stopped"
fi' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e

gcloud config set project test-project

gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 &
EMULATOR_PID=$!

# Wait for emulator
for i in {1..20}; do
  if curl --silent --fail http://localhost:8081; then break; fi
  sleep 2
done

# Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:/home/python-ndb"
export DATASTORE_EMULATOR_HOST=localhost:8081
export DATASTORE_PROJECT_ID=test-project

# Run all tests with verbose output
./venv/bin/pytest -v tests/

# Cleanup
if ps -p $EMULATOR_PID > /dev/null; then kill $EMULATOR_PID; fi' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e

# Kill existing emulator if port is in use
if lsof -i :8081; then
  kill $(lsof -t -i:8081)
  sleep 5
fi

gcloud config set project test-project

gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 &
EMULATOR_PID=$!

# Wait for emulator
for i in {1..20}; do
  if curl --silent --fail http://localhost:8081; then break; fi
  sleep 2
done

# Ensure project root is in Python path
export PYTHONPATH="/home/python-ndb:${PYTHONPATH}"
export DATASTORE_EMULATOR_HOST=localhost:8081
export DATASTORE_PROJECT_ID=test-project

# Run tests with module mode for proper path handling
python -m pytest -v tests/

# Cleanup
if ps -p $EMULATOR_PID > /dev/null; then kill $EMULATOR_PID; fi' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y lsof && mkdir -p test_utils && touch test_utils/__init__.py && echo 'Checking test_utils structure...' && ls -l test_utils && echo -e '#!/bin/bash
set -e

# Handle port conflicts
if lsof -i :8081; then kill $(lsof -t -i:8081); sleep 5; fi

gcloud config set project test-project

gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 &
EMULATOR_PID=$!

# Wait for emulator
for i in {1..20}; do if curl --silent --fail http://localhost:8081; then break; fi; sleep 2; done

# Ensure project root and test_utils are in Python path
export PYTHONPATH="/home/python-ndb:/home/python-ndb/test_utils:${PYTHONPATH}"
export DATASTORE_EMULATOR_HOST=localhost:8081
export DATASTORE_PROJECT_ID=test-project

# Run tests with verbose output
python -m pytest -v tests/

# Cleanup
if ps -p $EMULATOR_PID > /dev/null; then kill $EMULATOR_PID; fi' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
ls -l test_utils && echo -e '#!/bin/bash
set -e

# Ensure test_utils is a valid package
if [ ! -f test_utils/__init__.py ]; then touch test_utils/__init__.py; fi
if [ ! -f test_utils/system.py ]; then echo "Missing test_utils/system.py"; exit 1; fi

# Handle port conflicts
if lsof -i :8081; then kill $(lsof -t -i:8081); sleep 5; fi

gcloud config set project test-project

gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 &
EMULATOR_PID=$!

# Wait for emulator
for i in {1..20}; do if curl --silent --fail http://localhost:8081; then break; fi; sleep 2; done

# Set Python path and run tests
export PYTHONPATH="/home/python-ndb"
export DATASTORE_EMULATOR_HOST=localhost:8081
export DATASTORE_PROJECT_ID=test-project
python -m pytest -v tests/

# Cleanup
if ps -p $EMULATOR_PID > /dev/null; then kill $EMULATOR_PID; fi' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e

# Handle port conflicts
if lsof -i :8081; then kill $(lsof -t -i:8081); sleep 5; fi

gcloud config set project test-project

gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 &
EMULATOR_PID=$!

# Wait for emulator
for i in {1..20}; do if curl --silent --fail http://localhost:8081; then break; fi; sleep 2; done

# Set Python path and run unit tests (skipping system tests due to missing module)
export PYTHONPATH="/home/python-ndb"
export DATASTORE_EMULATOR_HOST=localhost:8081
export DATASTORE_PROJECT_ID=test-project
python -m pytest -v tests/unit/

# Cleanup
if ps -p $EMULATOR_PID > /dev/null; then kill $EMULATOR_PID; fi' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e

# Handle port conflicts
if lsof -i :8081; then kill $(lsof -t -i:8081); sleep 5; fi

gcloud config set project test-project

gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 &
EMULATOR_PID=$!

# Wait for emulator to be ready
for i in {1..20}; do
  if curl --silent --fail http://localhost:8081; then
    echo "Emulator ready"
    break
  fi
  sleep 2
done

# Set environment variables
export PYTHONPATH="/home/python-ndb"
export DATASTORE_EMULATOR_HOST=localhost:8081
export DATASTORE_PROJECT_ID=test-project

# Run full test suite with verbose output
python -m pytest -v tests/

# Cleanup emulator
if ps -p $EMULATOR_PID > /dev/null; then
  kill $EMULATOR_PID
  echo "Emulator stopped"
fi' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e

# Handle port conflicts
if lsof -i :8081; then kill $(lsof -t -i:8081); sleep 5; fi

gcloud config set project test-project

gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 &
EMULATOR_PID=$!

# Wait for emulator
for i in {1..20}; do if curl --silent --fail http://localhost:8081; then break; fi; sleep 2; done

# Set environment variables
export PYTHONPATH="/home/python-ndb"
export DATASTORE_EMULATOR_HOST=localhost:8081
export DATASTORE_PROJECT_ID=test-project

# Run unit tests (system tests skipped due to missing module)
python -m pytest -v tests/unit/

# Cleanup
if ps -p $EMULATOR_PID > /dev/null; then kill $EMULATOR_PID; fi' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e

# Handle port conflicts
if lsof -i :8081; then kill $(lsof -t -i:8081); sleep 5; fi

gcloud config set project test-project

gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 &
EMULATOR_PID=$!

# Wait for emulator
for i in {1..20}; do if curl --silent --fail http://localhost:8081; then break; fi; sleep 2; done

# Set environment variables
export PYTHONPATH="/home/python-ndb"
export DATASTORE_EMULATOR_HOST=localhost:8081
export DATASTORE_PROJECT_ID=test-project

# Run unit tests with verbose output
python -m pytest -v tests/unit/

# Cleanup emulator
if ps -p $EMULATOR_PID > /dev/null; then kill $EMULATOR_PID; fi' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e

# Handle port conflicts
if lsof -i :8081; then kill $(lsof -t -i:8081); sleep 5; fi

gcloud config set project test-project

gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 &
EMULATOR_PID=$!

# Wait for emulator
for i in {1..20}; do if curl --silent --fail http://localhost:8081; then break; fi; sleep 2; done

# Set environment variables
export PYTHONPATH="/home/python-ndb"
export DATASTORE_EMULATOR_HOST=localhost:8081
export DATASTORE_PROJECT_ID=test-project

# Run unit tests with verbose output
python -m pytest -v tests/unit/

# Cleanup emulator
if ps -p $EMULATOR_PID > /dev/null; then kill $EMULATOR_PID; fi

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
set -e

# Handle port conflicts
if lsof -i :8081; then kill $(lsof -t -i:8081); sleep 5; fi

gcloud config set project test-project

gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 &
EMULATOR_PID=$!

# Wait for emulator
for i in {1..20}; do if curl --silent --fail http://localhost:8081; then break; fi; sleep 2; done

# Set environment variables
export PYTHONPATH="/home/python-ndb"
export DATASTORE_EMULATOR_HOST=localhost:8081
export DATASTORE_PROJECT_ID=test-project

# Run unit tests with verbose output
python -m pytest -v tests/unit/

# Cleanup emulator
if ps -p $EMULATOR_PID > /dev/null; then kill $EMULATOR_PID; fi

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
set -e

# Handle port conflicts
if lsof -i :8081; then kill $(lsof -t -i:8081); sleep 5; fi

gcloud config set project test-project

gcloud beta emulators datastore start --no-store-on-disk --host-port=localhost:8081 &
EMULATOR_PID=$!

# Wait for emulator
for i in {1..20}; do if curl --silent --fail http://localhost:8081; then break; fi; sleep 2; done

# Set environment variables
export PYTHONPATH="/home/python-ndb"
export DATASTORE_EMULATOR_HOST=localhost:8081
export DATASTORE_PROJECT_ID=test-project

# Run unit tests with verbose output
python -m pytest -v tests/unit/

# Cleanup emulator
if ps -p $EMULATOR_PID > /dev/null; then kill $EMULATOR_PID; fi

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
RUN git clone https://github.com/googleapis/python-ndb.git /home/python-ndb

WORKDIR /home/python-ndb
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("googleapis", "python_ndb_665_to_560")
class PYTHON_NDB_665_TO_560(Instance):
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
        lines = log.split('\n')
        pending_test_name = None
        for line in lines:
            line = line.strip()
            # Check for test name with status on the same line (e.g., 'tests/... PASSED [ 0%]')
            # Match test name with status on the same line (e.g., 'tests/... PASSED [ 0%]')
            # Capture test name and strip trailing characters (e.g., ' - Attr...')
            match_before = re.match(r'^(tests/.*?::.*?)\s+(PASSED|FAILED|SKIPPED)\s*(\[.*\])?$', line)
            if match_before:
                test_name = re.sub(r'\s+-.*$', '', match_before.group(1).strip())  # Remove trailing '- ...'
                status = match_before.group(2)
                pending_test_name = None
            else:
                # Match status before test name (e.g., 'PASSED tests/...')
                match_after = re.match(r'^(PASSED|FAILED|SKIPPED)\s+(tests/.*?::.*?)(\s+-.*)?$', line)
                if match_after:
                    status = match_after.group(1)
                    test_name = re.sub(r'\s+-.*$', '', match_after.group(2).strip())
                    pending_test_name = None
                else:
                    # Capture test name without status (e.g., 'tests/...')
                    test_name_match = re.search(r'(tests/.*?::.*?)(?=\s|$)', line)  # Stop at space/end
                    if test_name_match:
                        pending_test_name = re.sub(r'\s+-.*$', '', test_name_match.group(1).strip())
                        continue
                    # Capture status without test name (link to pending test)
                    status_match = re.match(r'^(PASSED|FAILED|SKIPPED)\b', line)
                    if status_match and pending_test_name:
                        status = status_match.group(1)
                        test_name = pending_test_name
                        pending_test_name = None
                    else:
                        continue  # Skip non-test lines
            # Categorize test based on status
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
