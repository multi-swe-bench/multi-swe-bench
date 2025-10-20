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
apt-get update
###ACTION_DELIMITER###
apt-get install -y postgresql golang nodejs yarn
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
apt-get install -y npm
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
go install github.com/jackc/tern/v2@latest
###ACTION_DELIMITER###
apt-get remove -y golang golang-1.18
###ACTION_DELIMITER###
wget https://dl.google.com/go/go1.23.0.linux-amd64.tar.gz
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget https://dl.google.com/go/go1.23.0.linux-amd64.tar.gz
###ACTION_DELIMITER###
tar -C /usr/local -xzf go1.23.0.linux-amd64.tar.gz
###ACTION_DELIMITER###
export PATH=$PATH:/usr/local/go/bin
###ACTION_DELIMITER###
go install github.com/jackc/tern/v2@latest
###ACTION_DELIMITER###
git clone https://github.com/jackc/tern.git
###ACTION_DELIMITER###
sed -i 's/go 1.23.0/go 1.23/' tern/go.mod
###ACTION_DELIMITER###
cd tern && go install ./...
###ACTION_DELIMITER###
export GOROOT=/usr/local/go && export PATH=$GOROOT/bin:$PATH && go version
###ACTION_DELIMITER###
cd tern && go mod tidy && go install ./...
###ACTION_DELIMITER###
go mod tidy && go install ./...
###ACTION_DELIMITER###
tern --version
###ACTION_DELIMITER###
go env GOPATH && ls $(go env GOPATH)/bin && export PATH=$PATH:$(go env GOPATH)/bin && tern --version
###ACTION_DELIMITER###
service postgresql start && pg_isready -U postgres -d postgres
###ACTION_DELIMITER###
sudo -u postgres createdb hub
###ACTION_DELIMITER###
su postgres -c 'createdb hub'
###ACTION_DELIMITER###
mkdir -p ~/.cfg && echo -e '[database]\nhost = localhost\nport = 5432\ndatabase = hub\nuser = postgres\n\n[data]\nloadSampleData = true' > ~/.cfg/tern.conf && cd /home/hub && tern migrate --config ~/.cfg/tern.conf --migrations database/migrations
###ACTION_DELIMITER###
sed -i 's/local   all             postgres                                .*/local   all             postgres                                trust/' /etc/postgresql/14/main/pg_hba.conf && service postgresql reload && tern migrate --config ~/.cfg/tern.conf --migrations database/migrations
###ACTION_DELIMITER###
echo -e '[database]\nhost = /var/run/postgresql\nport = 5432\ndatabase = hub\nuser = postgres\n\n[data]\nloadSampleData = true' > ~/.cfg/tern.conf && service postgresql restart && tern migrate --config ~/.cfg/tern.conf --migrations database/migrations
###ACTION_DELIMITER###
ls -l database/migrations && tern migrate --config ~/.cfg/tern.conf --migrations /home/hub/database/migrations
###ACTION_DELIMITER###
ls -l database/migrations/schema && tern migrate --config ~/.cfg/tern.conf --migrations database/migrations/schema
###ACTION_DELIMITER###
cd web && yarn install && yarn build
###ACTION_DELIMITER###
cd .. && echo 'go test -v -count=1 ./...' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
go test -v -count=1 ./...

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
go test -v -count=1 ./...

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
go test -v -count=1 ./...

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
RUN git clone https://github.com/artifacthub/hub.git /home/hub

WORKDIR /home/hub
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("artifacthub", "hub_852_to_804")
class HUB_852_TO_804(Instance):
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
        import json
        # Capture test statuses using combined patterns
        # Passed tests: match both '--- PASS: TestName (duration)' and '=== RUN TestName ... PASS'
        test_status = {}
        for line in log.split("\n"):
            pass_match = re.match(r"--- PASS: (\S+) \(\d+\.\d+s\)", line)
            fail_match = re.match(r"--- FAIL: (\S+) \(\d+\.\d+s\)", line)
            skip_match = re.match(r"--- SKIP: (\S+) \(\d+\.\d+s\)", line)
            if pass_match:
                test_name = pass_match.group(1)
                test_status[test_name] = "passed"
            elif fail_match:
                test_name = fail_match.group(1)
                test_status[test_name] = "failed"
            elif skip_match:
                test_name = skip_match.group(1)
                test_status[test_name] = "skipped"
        for test_name, status in test_status.items():
            if status == "passed":
                passed_tests.add(test_name)
            elif status == "failed":
                failed_tests.add(test_name)
            elif status == "skipped":
                skipped_tests.add(test_name)
        # Failed tests: match both '--- FAIL: TestName (duration)' and '=== RUN TestName ... FAIL'
        # Skipped tests: match both '--- SKIP: TestName (duration)' and '=== RUN TestName ... SKIP'
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
