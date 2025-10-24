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
        return "golang:1.21"

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
ls -la .github
###ACTION_DELIMITER###
ls -la .github/workflows
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
ls -la
###ACTION_DELIMITER###
apt-get install -y nodejs npm
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
apt-get install -y postgresql postgresql-contrib
###ACTION_DELIMITER###
service postgresql start
###ACTION_DELIMITER###
su - postgres -c "createuser tests" && su - postgres -c "createdb -O tests tests"
###ACTION_DELIMITER###
go install github.com/jackc/tern/v2@latest
###ACTION_DELIMITER###
echo '#!/bin/bash
cd /home/hub
go test -v -count=1 ./...' > /home/test_commands.sh && chmod +x /home/test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
# Run backend tests
cd /home/hub
GOFLAGS=-mod=readonly go test -v -count=1 -cover -race ./...

# Run database tests
pg_prove --host localhost --dbname tests --username tests --verbose database/tests/schema/*.sql database/tests/functions/*/*.sql' > /home/hub/test_commands.sh && chmod +x /home/hub/test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
# Run backend tests
cd /home/hub
GOFLAGS=-mod=readonly go test -v -cover -race ./...

# Run database tests
pg_prove --host localhost --dbname tests --username tests --verbose database/tests/schema/*.sql database/tests/functions/*/*.sql

# Run frontend tests
cd /home/hub/web
yarn test --watchAll=false --passWithNoTests --verbose' > /home/hub/test_commands.sh && chmod +x /home/hub/test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
# Run backend tests
cd /home/hub
GOFLAGS=-mod=readonly go test -v -cover -race ./...

# Run database tests
pg_prove --host localhost --dbname tests --username tests --verbose database/tests/schema/*.sql database/tests/functions/*/*.sql

# Run frontend tests
cd /home/hub/web
yarn test --watchAll=false --passWithNoTests --verbose

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
#!/bin/bash
# Run backend tests
cd /home/hub
GOFLAGS=-mod=readonly go test -v -cover -race ./...

# Run database tests
pg_prove --host localhost --dbname tests --username tests --verbose database/tests/schema/*.sql database/tests/functions/*/*.sql

# Run frontend tests
cd /home/hub/web
yarn test --watchAll=false --passWithNoTests --verbose

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
#!/bin/bash
# Run backend tests
cd /home/hub
GOFLAGS=-mod=readonly go test -v -cover -race ./...

# Run database tests
pg_prove --host localhost --dbname tests --username tests --verbose database/tests/schema/*.sql database/tests/functions/*/*.sql

# Run frontend tests
cd /home/hub/web
yarn test --watchAll=false --passWithNoTests --verbose

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

# Choose an appropriate base image based on the project's requirements - replace golang:1.21 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM golang:1.21

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
RUN git clone https://github.com/artifacthub/hub.git /home/hub

WORKDIR /home/hub
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("artifacthub", "hub_1268_to_1119")
class HUB_1268_TO_1119(Instance):
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

        # TODO: Implement the parse_log function
        # Regular expression to match test results (PASS/FAIL/SKIP)
        pattern = re.compile(r"--- (PASS|FAIL|SKIP): (.*?) \((?:\d+\.\d+|\d+)s\)")
        matches = pattern.findall(log)
        for status, test_name in matches:
            test_name = test_name.strip()
            if status == "PASS":
                passed_tests.add(test_name)
            elif status == "FAIL":
                failed_tests.add(test_name)
            elif status == "SKIP":
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
