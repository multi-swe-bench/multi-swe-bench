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
apt-get update && apt-get install -y postgresql
###ACTION_DELIMITER###
apt-get install -y golang
###ACTION_DELIMITER###
go install github.com/jackc/tern/v2@latest
###ACTION_DELIMITER###
su postgres -c 'pg_ctl start -D /var/lib/postgresql/16/main'
###ACTION_DELIMITER###
su postgres -c '/usr/lib/postgresql/16/bin/pg_ctl start -D /var/lib/postgresql/16/main'
###ACTION_DELIMITER###
su postgres -c '/usr/lib/postgresql/16/bin/initdb -D /var/lib/postgresql/16/main'
###ACTION_DELIMITER###
su postgres -c 'rm -rf /var/lib/postgresql/16/main && /usr/lib/postgresql/16/bin/initdb -D /var/lib/postgresql/16/main'
###ACTION_DELIMITER###
su postgres -c '/usr/lib/postgresql/16/bin/pg_ctl start -D /var/lib/postgresql/16/main'
###ACTION_DELIMITER###
su postgres -c 'createdb hub'
###ACTION_DELIMITER###
mkdir -p ~/.cfg && echo -e '[database]\nhost = localhost\nport = 5432\ndatabase = hub\nuser = postgres\n\n[data]\nloadSampleData = true' > ~/.cfg/tern.conf
###ACTION_DELIMITER###
~/go/bin/tern migrate --config ~/.cfg/tern.conf
###ACTION_DELIMITER###
~/go/bin/tern migrate --config ~/.cfg/tern.conf --migrations ./database/migrations
###ACTION_DELIMITER###
ls -l ./database
###ACTION_DELIMITER###
ls -l ./database/migrations
###ACTION_DELIMITER###
ls -l ./database/migrations/schema
###ACTION_DELIMITER###
~/go/bin/tern migrate --config ~/.cfg/tern.conf --migrations ./database/migrations/schema
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && echo 'deb https://dl.yarnpkg.com/debian/ stable main' | tee /etc/apt/sources.list.d/yarn.list && apt-get update && apt-get install -y yarn
###ACTION_DELIMITER###
apt-get install -y gnupg
###ACTION_DELIMITER###
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && echo 'deb https://dl.yarnpkg.com/debian/ stable main' | tee /etc/apt/sources.list.d/yarn.list && apt-get update && apt-get install -y yarn
###ACTION_DELIMITER###
cd web && yarn install
###ACTION_DELIMITER###
apt-get install -y python3 && ln -s /usr/bin/python3 /usr/bin/python
###ACTION_DELIMITER###
cd web && yarn install
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
apt-get install -y python2 && PYTHON=python2 yarn install
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2.7 && ln -s /usr/bin/python2.7 /usr/bin/python && PYTHON=python2.7 yarn install
###ACTION_DELIMITER###
apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python2.7 && ln -sf /usr/bin/python2.7 /usr/bin/python && PYTHON=python2.7 yarn install
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && source ~/.nvm/nvm.sh && nvm install 14 && nvm use 14 && yarn install
###ACTION_DELIMITER###
echo -e '#!/bin/bash\n\n# Database tests\npg_prove --host localhost --dbname hub --username postgres --verbose ./database/tests/**/*.sql\n\n# Backend tests\ngo test -cover -race -v -mod=readonly ./...\n\n# Frontend tests\ncd web && yarn test --watchAll=false --passWithNoTests --verbose' > /home/hub/test_commands.sh && chmod +x /home/hub/test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash

# Database tests
pg_prove --host localhost --dbname hub --username postgres --verbose ./database/tests/**/*.sql

# Backend tests
go test -cover -race -v -mod=readonly ./...

# Frontend tests
cd web && yarn test --watchAll=false --passWithNoTests --verbose

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

# Database tests
pg_prove --host localhost --dbname hub --username postgres --verbose ./database/tests/**/*.sql

# Backend tests
go test -cover -race -v -mod=readonly ./...

# Frontend tests
cd web && yarn test --watchAll=false --passWithNoTests --verbose

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

# Database tests
pg_prove --host localhost --dbname hub --username postgres --verbose ./database/tests/**/*.sql

# Backend tests
go test -cover -race -v -mod=readonly ./...

# Frontend tests
cd web && yarn test --watchAll=false --passWithNoTests --verbose

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
RUN git clone https://github.com/artifacthub/hub.git /home/hub

WORKDIR /home/hub
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("artifacthub", "hub_788_to_199")
class HUB_788_TO_199(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        import json

        # Extract test names and statuses using regex
        # Pattern for passed tests: matches --- PASS: TestName and PASS TestFile.tsx (no line start anchor)
        pass_pattern = re.compile(
            r"(--- PASS:\s+(\S+)|PASS\s+(.*\.test\.tsx))", re.MULTILINE
        )
        pass_matches = pass_pattern.findall(log)
        passed_tests = set()
        for match in pass_matches:
            # Capture test names from both --- PASS and PASS lines
            test_name = match[1] if match[1] else match[2].strip()
            passed_tests.add(test_name)
        # Pattern for failed tests: matches --- FAIL: TestName, FAIL TestFile.tsx, and ● TestName (no line start anchor)
        fail_pattern = re.compile(
            r"(--- FAIL:\s+(\S+)|FAIL\s+(.*\.test\.tsx)|●\s+(.*)$)", re.MULTILINE
        )
        fail_matches = fail_pattern.findall(log)
        failed_tests = set()
        for match in fail_matches:
            # Capture test names from --- FAIL, FAIL, and ● lines
            test_name = (
                match[1]
                if match[1]
                else (match[2].strip() if match[2] else match[3].strip())
            )
            if test_name:
                failed_tests.add(test_name)
        # Pattern for skipped tests: matches --- SKIP: TestName
        skip_pattern = re.compile(r"--- SKIP:\s+(\S+)", re.MULTILINE)
        skipped_tests = set(skip_pattern.findall(log))
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
