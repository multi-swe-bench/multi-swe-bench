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
                """node -v
###ACTION_DELIMITER###
apt-get install -y nodejs npm
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y nodejs npm
###ACTION_DELIMITER###
node -v
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_14.x | bash -
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
###ACTION_DELIMITER###
nvm install 14
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
npm test -- --reporter spec
###ACTION_DELIMITER###
apt-get install -y jq
###ACTION_DELIMITER###
jq '.resolutions = {"graceful-fs": "4.2.11"}' package.json > package.tmp && mv package.tmp package.json
###ACTION_DELIMITER###
npm install --save-dev npm-force-resolutions
###ACTION_DELIMITER###
jq '.scripts.preinstall = "npx npm-force-resolutions"' package.json > package.tmp && mv package.tmp package.json
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
npm config set unsafe-perm true && npm install
###ACTION_DELIMITER###
npm test -- --reporter spec
###ACTION_DELIMITER###
ls -l node_modules/@adobe/petridish/src/
###ACTION_DELIMITER###
sed -n '11p' src/up.cmd.js
###ACTION_DELIMITER###
sed -n '10,15p' src/up.cmd.js
###ACTION_DELIMITER###
grep -n '@adobe/petridish/src/logger' src/up.cmd.js
###ACTION_DELIMITER###
jq '.dependencies."@adobe/petridish" = "1.0.0"' package.json > package.tmp && mv package.tmp package.json && npm install
###ACTION_DELIMITER###
ls -R node_modules/@adobe/petridish/
###ACTION_DELIMITER###
jq '.dependencies."@adobe/petridish" = "1.0.0"' package.json > package.tmp && mv package.tmp package.json && npm install
###ACTION_DELIMITER###
cat node_modules/@adobe/petridish/src/utils.js
###ACTION_DELIMITER###
jq '.dependencies."@adobe/petridish" = "1.0.1"' package.json > package.tmp && mv package.tmp package.json && npm install
###ACTION_DELIMITER###
jq '.dependencies."@adobe/petridish" = "1.3.0"' package.json > package.tmp && mv package.tmp package.json && npm install
###ACTION_DELIMITER###
cat node_modules/@adobe/petridish/src/index.js
###ACTION_DELIMITER###
cat src/cli-util.js
###ACTION_DELIMITER###
sed -i '18s|.*|const logger = console;|' src/up.cmd.js
###ACTION_DELIMITER###
npm test -- --reporter spec
###ACTION_DELIMITER###
echo 'npm test -- --reporter spec' > /home/helix-cli/test_commands.sh && chmod +x /home/helix-cli/test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npm test -- --reporter spec

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
npm test -- --reporter spec

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
npm test -- --reporter spec

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
RUN git clone https://github.com/adobe/helix-cli.git /home/helix-cli

WORKDIR /home/helix-cli
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("adobe", "helix_cli_278_to_36")
class HELIX_CLI_278_TO_36(Instance):
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
        import json

        # Parse passed tests
        passed_pattern = re.compile(r"^\s+✓\s+(.*)$", re.MULTILINE)
        passed_tests.update(passed_pattern.findall(log))
        # Parse failed tests
        failed_pattern = re.compile(r"^\s+\d+\)\s+(.*)$", re.MULTILINE)
        failed_tests.update(failed_pattern.findall(log))
        # Skipped tests are not observed in the sampled logs, so leaving as empty set
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
