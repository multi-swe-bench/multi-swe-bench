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
        return "ruby:3.2-slim-bullseye"

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
ls bin
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-key adv --fetch-keys http://dl.yarnpkg.com/debian/pubkey.gpg
###ACTION_DELIMITER###
apt-get install -y gnupg
###ACTION_DELIMITER###
apt-key adv --fetch-keys http://dl.yarnpkg.com/debian/pubkey.gpg
###ACTION_DELIMITER###
echo 'deb http://dl.yarnpkg.com/debian/ stable main' | tee /etc/apt/sources.list.d/yarn.list
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y yarn
###ACTION_DELIMITER###
wget https://github.com/jgm/pandoc/releases/download/2.2/pandoc-2.2-1-amd64.deb
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget https://github.com/jgm/pandoc/releases/download/2.2/pandoc-2.2-1-amd64.deb
###ACTION_DELIMITER###
dpkg -i pandoc-2.2-1-amd64.deb
###ACTION_DELIMITER###
apt-get install -y postgresql
###ACTION_DELIMITER###
service postgresql start
###ACTION_DELIMITER###
psql -c 'create database manifold_test;' -U postgres
###ACTION_DELIMITER###
sudo -u postgres psql -c 'create database manifold_test;'
###ACTION_DELIMITER###
su - postgres -c "psql -c 'create database manifold_test;'"
###ACTION_DELIMITER###
cp .env.sample .env
###ACTION_DELIMITER###
rm -rf ~/.nvm && git clone https://github.com/creationix/nvm.git ~/.nvm && (cd ~/.nvm && git checkout `git describe --abbrev=0 --tags`) && source ~/.nvm/nvm.sh && nvm install 8.16.0
###ACTION_DELIMITER###
cd client && yarn install --production=false
###ACTION_DELIMITER###
yarn test -- --maxWorkers=4
###ACTION_DELIMITER###
cd ../api && bundle install
###ACTION_DELIMITER###
bundle _2.4.19_ install
###ACTION_DELIMITER###
bundle update
###ACTION_DELIMITER###
rm Gemfile.lock && bundle _2.4.19_ install
###ACTION_DELIMITER###
\curl -sSL https://get.rvm.io | bash -s stable && source /etc/profile.d/rvm.sh && rvm install 2.4.4 && rvm use 2.4.4
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
\curl -sSL https://get.rvm.io | bash -s stable && source /etc/profile.d/rvm.sh && rvm install 2.4.4 && rvm use 2.4.4
###ACTION_DELIMITER###
curl -sSL https://rvm.io/mpapis.asc | gpg --import - && curl -sSL https://rvm.io/pkuczynski.asc | gpg --import -
###ACTION_DELIMITER###
\curl -sSL https://get.rvm.io | bash -s stable && source /etc/profile.d/rvm.sh && rvm install 2.4.4 && rvm use 2.4.4 --default
###ACTION_DELIMITER###
apt-get install -y procps && source /etc/profile.d/rvm.sh && unset GEM_HOME && rvm install 2.4.4 && rvm use 2.4.4 --default
###ACTION_DELIMITER###
bundle install
###ACTION_DELIMITER###
apt-get install -y shared-mime-info
###ACTION_DELIMITER###
bundle install
###ACTION_DELIMITER###
apt-get install -y libicu-dev
###ACTION_DELIMITER###
bundle install
###ACTION_DELIMITER###
apt-get install -y libpq-dev
###ACTION_DELIMITER###
bundle install
###ACTION_DELIMITER###
RAILS_ENV=test bundle exec rails db:schema:load --trace
###ACTION_DELIMITER###
sed -i '8i gem "dalli", "~> 2.7.11"' Gemfile
###ACTION_DELIMITER###
bundle install
###ACTION_DELIMITER###
bundle update dalli
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
cd client && yarn test -- --maxWorkers=4
cd ../api && RAILS_ENV=test bundle exec rspec spec -v' > /home/manifold/test_commands.sh && chmod +x /home/manifold/test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e
cd client && yarn test -- --maxWorkers=4
cd ../api && RAILS_ENV=test bundle exec rspec spec -v

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
cd client && yarn test -- --maxWorkers=4
cd ../api && RAILS_ENV=test bundle exec rspec spec -v

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
cd client && yarn test -- --maxWorkers=4
cd ../api && RAILS_ENV=test bundle exec rspec spec -v

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
FROM ruby:3.2-slim-bullseye

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


@Instance.register("ManifoldScholar", "manifold_2403_to_1524")
class MANIFOLD_2403_TO_1524(Instance):
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

        current_context = []
        lines = log.split("\n")
        for line in lines:
            leading_spaces = len(line) - len(line.lstrip(" "))
            line_text = line.strip()
            if not line_text:
                continue
            # Check if it's a test case line with ✓ (passed)
            if "✓" in line_text:
                match = re.match(r"✓\s*(.*?)(\s*\(\d+ms\))?$", line_text)
                if match:
                    test_desc = match.group(1).strip()
                    full_test_name = " ".join(current_context + [test_desc])
                    passed_tests.add(full_test_name)
            # Check if it's a test case line with ✕ (failed)
            elif "✕" in line_text:
                match = re.match(r"✕\s*(.*?)(\s*\(\d+ms\))?$", line_text)
                if match:
                    test_desc = match.group(1).strip()
                    full_test_name = " ".join(current_context + [test_desc])
                    failed_tests.add(full_test_name)
            # Check if it's a skipped test (marked with → or SKIPPED)
            elif "→" in line_text or "SKIPPED" in line_text:
                match = re.match(r"(→|SKIPPED)\s*(.*?)(\s*\(\d+ms\))?$", line_text)
                if match:
                    test_desc = match.group(2).strip()
                    full_test_name = " ".join(current_context + [test_desc])
                    skipped_tests.add(full_test_name)
            else:
                # Update current context for group/subgroup lines (ignore top-level lines)
                if leading_spaces == 0:
                    continue
                level = leading_spaces // 2
                current_context = current_context[: level - 1]
                current_context.append(line_text)
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
