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
node -v
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && apt-get update && apt-get install -y nodejs && npm install -g yarn
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && apt-get install -y nodejs && npm install -g yarn
###ACTION_DELIMITER###
apt-get remove -y libnode72 nodejs && apt-get update && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && apt-get install -y nodejs && npm install -g yarn
###ACTION_DELIMITER###
yarn
###ACTION_DELIMITER###
apt-get remove -y nodejs && curl -fsSL https://deb.nodesource.com/setup_12.x | bash - && apt-get install -y nodejs && npm install -g yarn
###ACTION_DELIMITER###
yarn install --ignore-engines
###ACTION_DELIMITER###
apt-get update && apt-get remove -y nodejs libnode72 && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && apt-get install -y nodejs && node -v && npm -v
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
yarn install --ignore-engines
###ACTION_DELIMITER###
yarn build
###ACTION_DELIMITER###
echo 'lerna run test --stream --verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'yarn lerna run test --stream --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'yarn lerna run test --stream -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo 'yarn lerna run test --stream' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-11-jre
###ACTION_DELIMITER###
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add - && echo 'deb https://artifacts.elastic.co/packages/7.x/apt stable main' | tee /etc/apt/sources.list.d/elastic.list && apt-get update && apt-get install -y elasticsearch && service elasticsearch start && sleep 10 && curl http://localhost:9200
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget && wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg && echo 'deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/7.x/apt stable main' | tee /etc/apt/sources.list.d/elastic.list && apt-get update && apt-get install -y elasticsearch && service elasticsearch start && sleep 10 && curl http://localhost:9200
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
yarn workspace @cdt/data populate-dev && bash test_commands.sh
###ACTION_DELIMITER###
/usr/share/elasticsearch/bin/elasticsearch-plugin install -b analysis-icu && service elasticsearch restart && sleep 10 && yarn workspace @cdt/data populate-dev && bash test_commands.sh
###ACTION_DELIMITER###
yarn workspace @cdt/api test -u && bash test_commands.sh
###ACTION_DELIMITER###
yarn workspace @cdt/frontend test -u && bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn lerna run test --stream

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
yarn lerna run test --stream

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
yarn lerna run test --stream

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
RUN git clone https://github.com/SocialGouv/code-du-travail-numerique.git /home/code-du-travail-numerique

WORKDIR /home/code-du-travail-numerique
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("SocialGouv", "code_du_travail_numerique_2554_to_2247")
class CODE_DU_TRAVAIL_NUMERIQUE_2554_TO_2247(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re

        # Parse test results using regex
        pattern = re.compile(r":\s*(PASS|FAIL|SKIPPED)\s+([^\n]+test\.js)")
        matches = pattern.findall(log)
        for status, test_path in matches:
            test_name = test_path.strip()
            if status == "PASS":
                passed_tests.add(test_name)
            elif status == "FAIL":
                failed_tests.add(test_name)
            elif status == "SKIPPED":
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
