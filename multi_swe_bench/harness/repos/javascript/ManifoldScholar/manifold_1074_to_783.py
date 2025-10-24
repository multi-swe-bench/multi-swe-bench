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
apt-get update
###ACTION_DELIMITER###
rm -rf ~/.nvm && git clone https://github.com/creationix/nvm.git ~/.nvm && (cd ~/.nvm && git checkout `git describe --abbrev=0 --tags`) && source ~/.nvm/nvm.sh && nvm install 6.10.3
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
rm -rf ~/.nvm && git clone https://github.com/creationix/nvm.git ~/.nvm && (cd ~/.nvm && git checkout `git describe --abbrev=0 --tags`) && source ~/.nvm/nvm.sh && nvm install 6.10.3
###ACTION_DELIMITER###
apt-key adv --fetch-keys http://dl.yarnpkg.com/debian/pubkey.gpg && echo "deb http://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list && apt-get update && apt-get install -y yarn
###ACTION_DELIMITER###
apt-get install -y gnupg
###ACTION_DELIMITER###
apt-key adv --fetch-keys http://dl.yarnpkg.com/debian/pubkey.gpg && echo "deb http://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list && apt-get update && apt-get install -y yarn
###ACTION_DELIMITER###
cd client && yarn install --production=false
###ACTION_DELIMITER###
apt-get install -y postgresql postgresql-contrib
###ACTION_DELIMITER###
service postgresql start && psql -c 'create database manifold_test;' -U postgres
###ACTION_DELIMITER###
service postgresql start && sudo -u postgres psql -c 'create database manifold_test;'
###ACTION_DELIMITER###
service postgresql start && su - postgres -c 'psql -c "create database manifold_test;"'
###ACTION_DELIMITER###
cd .. && curl -sSL https://get.rvm.io | bash -s stable
###ACTION_DELIMITER###
curl -sSL https://rvm.io/mpapis.asc | gpg --import - && curl -sSL https://rvm.io/pkuczynski.asc | gpg --import -
###ACTION_DELIMITER###
curl -sSL https://get.rvm.io | bash -s stable
###ACTION_DELIMITER###
source /etc/profile.d/rvm.sh
###ACTION_DELIMITER###
rvm install "ruby-2.3.5"
###ACTION_DELIMITER###
apt-get install -y bzip2 gawk g++ gcc autoconf automake bison libc6-dev libffi-dev libgdbm-dev libncurses5-dev libsqlite3-dev libtool libyaml-dev make pkg-config sqlite3 zlib1g-dev libgmp-dev libreadline-dev libssl-dev
###ACTION_DELIMITER###
rvm install "ruby-2.3.5"
###ACTION_DELIMITER###
wget http://security.ubuntu.com/ubuntu/pool/main/o/openssl1.0/libssl1.0.0_1.0.2n-1ubuntu5.10_amd64.deb && wget http://security.ubuntu.com/ubuntu/pool/main/o/openssl1.0/libssl1.0-dev_1.0.2n-1ubuntu5.10_amd64.deb && dpkg -i libssl1.0.0_1.0.2n-1ubuntu5.10_amd64.deb && dpkg -i libssl1.0-dev_1.0.2n-1ubuntu5.10_amd64.deb
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget http://security.ubuntu.com/ubuntu/pool/main/o/openssl1.0/libssl1.0.0_1.0.2n-1ubuntu5.10_amd64.deb && wget http://security.ubuntu.com/ubuntu/pool/main/o/openssl1.0/libssl1.0-dev_1.0.2n-1ubuntu5.10_amd64.deb && dpkg -i libssl1.0.0_1.0.2n-1ubuntu5.10_amd64.deb && dpkg -i libssl1.0-dev_1.0.2n-1ubuntu5.10_amd64.deb
###ACTION_DELIMITER###
wget http://old-releases.ubuntu.com/ubuntu/pool/main/o/openssl1.0/libssl1.0.0_1.0.2n-1ubuntu5_amd64.deb && wget http://old-releases.ubuntu.com/ubuntu/pool/main/o/openssl1.0/libssl1.0-dev_1.0.2n-1ubuntu5_amd64.deb && dpkg -i libssl1.0.0_1.0.2n-1ubuntu5_amd64.deb && dpkg -i libssl1.0-dev_1.0.2n-1ubuntu5_amd64.deb
###ACTION_DELIMITER###
echo 'deb http://old-releases.ubuntu.com/ubuntu xenial main restricted universe multiverse' >> /etc/apt/sources.list && apt-get update && apt-get install -y libssl1.0.0 libssl1.0-dev
###ACTION_DELIMITER###
echo 'deb http://old-releases.ubuntu.com/ubuntu/ xenial main restricted universe multiverse' >> /etc/apt/sources.list && apt-get update && apt-get install -y libssl1.0.0 libssl1.0-dev
###ACTION_DELIMITER###
wget http://old-releases.ubuntu.com/ubuntu/pool/main/o/openssl1.0/libssl1.0.0_1.0.2g-1ubuntu4.15_amd64.deb && wget http://old-releases.ubuntu.com/ubuntu/pool/main/o/openssl1.0/libssl1.0-dev_1.0.2g-1ubuntu4.15_amd64.deb && dpkg -i libssl1.0.0_1.0.2g-1ubuntu4.15_amd64.deb && dpkg -i libssl1.0-dev_1.0.2g-1ubuntu4.15_amd64.deb
###ACTION_DELIMITER###
wget https://www.openssl.org/source/openssl-1.0.2u.tar.gz && tar xzf openssl-1.0.2u.tar.gz && cd openssl-1.0.2u && ./config --prefix=$HOME/openssl-1.0.2u --openssldir=$HOME/openssl-1.0.2u shared zlib && make && make install && cd .. && rvm install 2.3.5 --with-openssl-dir=$HOME/openssl-1.0.2u
###ACTION_DELIMITER###
sed -i '/old-releases.ubuntu.com/d' /etc/apt/sources.list && apt-get update && rvm install 2.3.5 --with-openssl-dir=$HOME/openssl-1.0.2u
###ACTION_DELIMITER###
rvm install 2.3.5 --with-openssl-dir=$HOME/openssl-1.0.2u --autolibs=read-fail
###ACTION_DELIMITER###
rvm install 2.3.5 --with-openssl-dir=$HOME/openssl-1.0.2u --autolibs=disable
###ACTION_DELIMITER###
rvm use 2.3.5 && cd api && bundle install
###ACTION_DELIMITER###
bundle update mimemagic && bundle install
###ACTION_DELIMITER###
apt-get install -y ca-certificates && bundle install
###ACTION_DELIMITER###
SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt bundle update mimemagic && bundle install
###ACTION_DELIMITER###
apt-get install -y libicu-dev && bundle install
###ACTION_DELIMITER###
bundle update mimemagic && bundle install
###ACTION_DELIMITER###
SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt bundle update mimemagic && bundle install
###ACTION_DELIMITER###
apt-get install -y libpq-dev && bundle install
###ACTION_DELIMITER###
SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt bundle update mimemagic && bundle install
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
cd client && yarn test -- --maxWorkers=4 --verbose
cd ../api && bundle exec rspec spec -fd --tag ~@integration -v' > /home/manifold/test_commands.sh && chmod +x /home/manifold/test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e
cd client && yarn test -- --maxWorkers=4 --verbose
cd ../api && bundle exec rspec spec -fd --tag ~@integration -v

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
set -e
cd client && yarn test -- --maxWorkers=4 --verbose
cd ../api && bundle exec rspec spec -fd --tag ~@integration -v

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
set -e
cd client && yarn test -- --maxWorkers=4 --verbose
cd ../api && bundle exec rspec spec -fd --tag ~@integration -v

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
RUN git clone https://github.com/ManifoldScholar/manifold.git /home/manifold

WORKDIR /home/manifold
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ManifoldScholar", "manifold_1074_to_783")
class MANIFOLD_1074_TO_783(Instance):
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

        # Parse the log content to extract test names and statuses
        lines = log.split("\n")
        # Regex patterns to identify test suites, suite names, test cases, and errors
        suite_pattern = re.compile(
            r"^(PASS|FAIL|SKIPPED)\s+(.+)$"
        )  # Identifies suite status and file path
        suite_name_pattern = re.compile(r"^\s+(.+)$")  # Captures indented suite names
        test_case_pattern = re.compile(
            r"^\s+(✓|x|s|○)\s+(.+?)(?:\s*\(\d+ms\))?$"
        )  # Captures passed (✓), failed (x), or skipped (s/○) test descriptions
        error_line_pattern = re.compile(
            r"^\s+>\s+\d+\s\|\s+expect\(.+\)"
        )  # Identifies error lines in failed tests
        test_desc_pattern = re.compile(
            r'^\s+\d+\s\|\s+it\("(.+?)",'
        )  # Extracts test description from error context
        i = 0
        current_suite_status = None
        current_suite_name = None
        while i < len(lines):
            line = lines[i]
            suite_match = suite_pattern.match(line)
            if suite_match:
                current_suite_status, _ = suite_match.groups()
                i += 1
                # Skip empty lines to find suite name
                while i < len(lines) and lines[i].strip() == "":
                    i += 1
                if i < len(lines):
                    suite_name_match = suite_name_pattern.match(lines[i])
                    if suite_name_match:
                        current_suite_name = suite_name_match.group(1)
                        i += 1
            elif current_suite_status and current_suite_name:
                # Check for passed test cases in the suite
                test_match = test_case_pattern.match(line)
                if test_match:
                    test_status, test_desc = test_match.groups()
                    test_name = f"{current_suite_name} {test_desc.strip()}"
                    if test_status == "✓":
                        passed_tests.add(test_name)
                    elif test_status == "x":
                        failed_tests.add(test_name)
                    elif test_status in ("s", "○"):
                        skipped_tests.add(test_name)
                    i += 1
                # Check for error lines indicating failed tests
                elif error_line_pattern.match(line):
                    # Look back to find the test description
                    j = i - 1
                    test_desc = None
                    while j >= 0 and lines[j].strip() != "":
                        desc_match = test_desc_pattern.match(lines[j])
                        if desc_match:
                            test_desc = desc_match.group(1)
                            break
                        j -= 1
                    if test_desc:
                        test_name = f"{current_suite_name} {test_desc}"
                        failed_tests.add(test_name)
                    i += 1
                else:
                    i += 1
            else:
                i += 1
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
