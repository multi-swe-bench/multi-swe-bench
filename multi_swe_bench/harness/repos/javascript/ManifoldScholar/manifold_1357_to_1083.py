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
        return "ruby:3.2-slim"

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
                """ls
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y imagemagick postgresql nginx redis-server build-essential
###ACTION_DELIMITER###
bundle install
###ACTION_DELIMITER###
bundle _2.4.19_ install
###ACTION_DELIMITER###
ls client
###ACTION_DELIMITER###
apt-get install -y nodejs npm && npm install -g yarn
###ACTION_DELIMITER###
cd client && yarn install
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
###ACTION_DELIMITER###
nvm install 8.17.0
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
cat ../Gemfile
###ACTION_DELIMITER###
cat package.json
###ACTION_DELIMITER###
echo 'yarn --cwd client test' > /home/manifold/test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn --cwd client test

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
yarn --cwd client test

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
yarn --cwd client test

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
FROM ruby:3.2-slim

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


@Instance.register("ManifoldScholar", "manifold_1357_to_1083")
class MANIFOLD_1357_TO_1083(Instance):
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

        current_describe = None
        for line in log.split("\n"):
            line = line.rstrip()
            # Check for describe block (two spaces, not four)
            if line.startswith("  ") and not line.startswith("    "):
                current_describe = line.strip()
            # Check for passed test (four spaces, ✓)
            elif line.startswith("    ✓ "):
                if current_describe is None:
                    continue
                test_part = line.split("✓ ", 1)[1]
                # Remove time suffix
                if " (" in test_part:
                    test_desc = test_part.rsplit(" (", 1)[0].strip()
                else:
                    test_desc = test_part.strip()
                test_name = f"{current_describe} {test_desc}"
                passed_tests.add(test_name)
            # Check for failed test (four spaces, ✕)
            elif line.startswith("    ✕ "):
                if current_describe is None:
                    continue
                test_part = line.split("✕ ", 1)[1]
                if " (" in test_part:
                    test_desc = test_part.rsplit(" (", 1)[0].strip()
                else:
                    test_desc = test_part.strip()
                test_name = f"{current_describe} {test_desc}"
                failed_tests.add(test_name)
            # Check for skipped test (four spaces, ○)
            elif line.startswith("    ○ "):
                if current_describe is None:
                    continue
                test_part = line.split("○ ", 1)[1]
                if " (" in test_part:
                    test_desc = test_part.rsplit(" (", 1)[0].strip()
                else:
                    test_desc = test_part.strip()
                test_name = f"{current_describe} {test_desc}"
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
