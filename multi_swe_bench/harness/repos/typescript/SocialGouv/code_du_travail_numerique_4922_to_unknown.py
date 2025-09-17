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
                """ls -la
###ACTION_DELIMITER###
node -v
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_14.x | bash -
###ACTION_DELIMITER###
apt-get install -y nodejs
###ACTION_DELIMITER###
curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor | tee /usr/share/keyrings/yarnkey.gpg >/dev/null
###ACTION_DELIMITER###
echo "deb [signed-by=/usr/share/keyrings/yarnkey.gpg] https://dl.yarnpkg.com/debian stable main" | tee /etc/apt/sources.list.d/yarn.list
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y yarn
###ACTION_DELIMITER###
yarn bootstrap
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
yarn cache clean
###ACTION_DELIMITER###
sed -i 's/"@maxgfr\/react-accessible-accordion": "4.0.1"/"@maxgfr\/react-accessible-accordion": "^4.0.0"/' packages/react-ui/package.json
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
sed -i 's/"@maxgfr\/react-accessible-accordion": "^4.0.0"/"react-accessible-accordion": "^4.0.0"/' packages/react-ui/package.json
###ACTION_DELIMITER###
yarn test
###ACTION_DELIMITER###
yarn lerna run test
###ACTION_DELIMITER###
node_modules/.bin/lerna run test
###ACTION_DELIMITER###
node_modules/@lerna/cli/bin/lerna.js run test
###ACTION_DELIMITER###
yarn add lerna
###ACTION_DELIMITER###
yarn test
###ACTION_DELIMITER###
yarn add jest
###ACTION_DELIMITER###
yarn workspace @cdt/api add jest --dev
###ACTION_DELIMITER###
yarn workspace @cdt/api add jest@^27.0.6 --dev
###ACTION_DELIMITER###
yarn workspace @cdt/api list
###ACTION_DELIMITER###
ls -la packages/code-du-travail-api/node_modules/.bin | grep jest
###ACTION_DELIMITER###
yarn workspace @cdt/api add jest@27.0.6 --dev
###ACTION_DELIMITER###
yarn workspace @cdt/api run test
###ACTION_DELIMITER###
apt-get install -y openjdk-11-jre && wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add - && echo 'deb https://artifacts.elastic.co/packages/8.x/apt stable main' | tee /etc/apt/sources.list.d/elastic.list && apt-get update && apt-get install -y elasticsearch=8.5.2
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg && echo 'deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main' | tee /etc/apt/sources.list.d/elastic.list
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y elasticsearch=8.5.2
###ACTION_DELIMITER###

###ACTION_DELIMITER###
echo 'yarn test' > test_commands.sh
###ACTION_DELIMITER###
echo 'yarn test' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn test

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
yarn test

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
yarn test

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
RUN git clone https://github.com/SocialGouv/code-du-travail-numerique.git /home/code-du-travail-numerique

WORKDIR /home/code-du-travail-numerique
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("SocialGouv", "code_du_travail_numerique_4922_to_unknown")
class CODE_DU_TRAVAIL_NUMERIQUE_4922_TO_UNKNOWN(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re
        # Extract test names from test definitions (e.g., test("name"))
        test_pattern = r'(?:test|it)\("([^"]+)"'
        all_tests = set(re.findall(test_pattern, log))
        # Identify failed tests using failure indicators (Expected:/Received:)
        failed_pattern = r'test\("([^"]+)"[\s\S]*?Expected: (?:\d+)\n[\s\S]*?Received: (?:\d+)'
        failed_tests = set(re.findall(failed_pattern, log))
        # Passed tests are all tests not in failed_tests
        passed_tests = all_tests - failed_tests
        # Skipped tests (not present in sample logs, default to empty)
        skipped_tests = set()
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
