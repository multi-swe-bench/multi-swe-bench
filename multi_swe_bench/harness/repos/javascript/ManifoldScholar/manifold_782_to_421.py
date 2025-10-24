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
sudo apt-key adv --fetch-keys http://dl.yarnpkg.com/debian/pubkey.gpg
###ACTION_DELIMITER###
apt-key adv --fetch-keys http://dl.yarnpkg.com/debian/pubkey.gpg
###ACTION_DELIMITER###
apt-get install -y gnupg
###ACTION_DELIMITER###
echo 'deb http://dl.yarnpkg.com/debian/ stable main' | tee /etc/apt/sources.list.d/yarn.list
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 23E7166788B63E1E
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y yarn
###ACTION_DELIMITER###
rm -rf ~/.nvm && git clone https://github.com/creationix/nvm.git ~/.nvm && (cd ~/.nvm && git checkout `git describe --abbrev=0 --tags`) && source ~/.nvm/nvm.sh && nvm install 6.10.3
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
rm -rf ~/.nvm && git clone https://github.com/creationix/nvm.git ~/.nvm && (cd ~/.nvm && git checkout `git describe --abbrev=0 --tags`) && source ~/.nvm/nvm.sh && nvm install 6.10.3
###ACTION_DELIMITER###
gpg --keyserver hkp://keyserver.ubuntu.com --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3 7D2BAF1CF37B13E2069D6956105BD0E739499BDB
###ACTION_DELIMITER###
\curl -sSL https://get.rvm.io | bash -s stable
###ACTION_DELIMITER###
source /etc/profile.d/rvm.sh
###ACTION_DELIMITER###
rvm install 2.3.3
###ACTION_DELIMITER###
apt-get install -y bzip2 gawk g++ gcc autoconf automake bison libc6-dev libffi-dev libgdbm-dev libncurses5-dev libsqlite3-dev libtool libyaml-dev make pkg-config sqlite3 zlib1g-dev libgmp-dev libreadline-dev
###ACTION_DELIMITER###
echo 'deb http://archive.ubuntu.com/ubuntu bionic main' | tee /etc/apt/sources.list.d/bionic.list && apt-get update && apt-get install -y libssl1.0-dev
###ACTION_DELIMITER###
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3B4FE6ACC0B21F32
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y libssl1.0-dev
###ACTION_DELIMITER###
rvm install 2.3.3
###ACTION_DELIMITER###
rvm use 2.3.3 --default
###ACTION_DELIMITER###
cp .env.sample .env
###ACTION_DELIMITER###
cd client && yarn install --production=false
###ACTION_DELIMITER###
yarn test -- --maxWorkers=4
###ACTION_DELIMITER###
cd ../api && bundle install
###ACTION_DELIMITER###
rvm install 2.3.5
###ACTION_DELIMITER###
rvm use 2.3.5
###ACTION_DELIMITER###
bundle install
###ACTION_DELIMITER###
bundle update mimemagic
###ACTION_DELIMITER###
apt-get install -y libpq-dev
###ACTION_DELIMITER###
bundle install
###ACTION_DELIMITER###
sed -i 's/mimemagic (0.3.2)/mimemagic (0.3.5)/' Gemfile && bundle update mimemagic
###ACTION_DELIMITER###
apt-get install -y postgresql postgresql-contrib
###ACTION_DELIMITER###
service postgresql start && su postgres -c 'psql -c "create database manifold_test;"'
###ACTION_DELIMITER###
RAILS_ENV=test bundle exec rails db:migrate --trace
###ACTION_DELIMITER###
sed -i 's/local   all             postgres                                peer/local   all             postgres                                trust/' /etc/postgresql/14/main/pg_hba.conf && service postgresql restart
###ACTION_DELIMITER###
RAILS_ENV=test bundle exec rails db:migrate --trace
###ACTION_DELIMITER###
sed -i 's/host    all             all             127.0.0.1\/32            md5/host    all             all             127.0.0.1\/32            trust/' /etc/postgresql/14/main/pg_hba.conf && sed -i 's/host    all             all             ::1\/128                 md5/host    all             all             ::1\/128                 trust/' /etc/postgresql/14/main/pg_hba.conf && service postgresql restart
###ACTION_DELIMITER###
cat config/database.yml
###ACTION_DELIMITER###
export RAILS_DB_USER=postgres && export RAILS_DB_PASS='' && RAILS_ENV=test bundle exec rails db:migrate --trace
###ACTION_DELIMITER###
export RAILS_DB_HOST='' && export RAILS_DB_USER=postgres && export RAILS_DB_PASS='' && RAILS_ENV=test bundle exec rails db:migrate --trace
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
cd client && yarn test --verbose --maxWorkers=4
cd ../api && RAILS_ENV=test bundle exec rspec spec -fd --tag ~@integration --verbose' > /home/manifold/test_commands.sh && chmod +x /home/manifold/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/^cd ../api/export RAILS_DB_USER=postgres\nexport RAILS_DB_PASS=\"\"\ncd ../api/' /home/manifold/test_commands.sh && bash /home/manifold/test_commands.sh
###ACTION_DELIMITER###
sed -i 's|^cd ../api|export RAILS_DB_USER=postgres\nexport RAILS_DB_PASS=""\ncd ../api|' /home/manifold/test_commands.sh && bash /home/manifold/test_commands.sh
###ACTION_DELIMITER###
""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e
cd client && yarn test --verbose --maxWorkers=4
export RAILS_DB_USER=postgres
export RAILS_DB_PASS=""
cd ../api && RAILS_ENV=test bundle exec rspec spec -fd --tag ~@integration --verbose

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
cd client && yarn test --verbose --maxWorkers=4
export RAILS_DB_USER=postgres
export RAILS_DB_PASS=""
cd ../api && RAILS_ENV=test bundle exec rspec spec -fd --tag ~@integration --verbose

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
cd client && yarn test --verbose --maxWorkers=4
export RAILS_DB_USER=postgres
export RAILS_DB_PASS=""
cd ../api && RAILS_ENV=test bundle exec rspec spec -fd --tag ~@integration --verbose

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:22.04 with actual base image
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


@Instance.register("ManifoldScholar", "manifold_782_to_421")
class MANIFOLD_782_TO_421(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re

        # Extract test suites from RUNS and FAIL lines (matches log structure)
        # Capture test suite names from RUNS lines (e.g., 'RUNS  ...Searchable-test.js')
        all_tests = set(re.findall(r".*RUNS\s+.*?([\w-]+-test\.js)", log))
        # Capture failed test suite names from FAIL lines (e.g., 'FAIL  src/.../ListItem-test.js')
        failed_tests = set(re.findall(r".*FAIL\s+.*?([\w-]+-test\.js)", log))
        # Passed tests = all tests - failed tests
        passed_tests = all_tests - failed_tests
        # Skipped tests (no evidence in logs; default to empty set)
        skipped_tests = set()
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
