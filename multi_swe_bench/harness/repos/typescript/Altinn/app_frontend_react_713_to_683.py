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
        return "node:18-bullseye-slim"

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
ls src
###ACTION_DELIMITER###
corepack enable
###ACTION_DELIMITER###
yarn --version
###ACTION_DELIMITER###
npm install -g yarn@3.3.0
###ACTION_DELIMITER###
corepack prepare yarn@3.3.0 --activate
###ACTION_DELIMITER###
yarn --version
###ACTION_DELIMITER###
cd src && yarn install
###ACTION_DELIMITER###
cd ../test/cypress && yarn install
###ACTION_DELIMITER###
echo -e '#!/bin/bash
 yarn --cwd src test --verbose
 yarn --cwd test/cypress test:all --verbose' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
bash /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
 yarn --cwd src test
 yarn --cwd test/cypress test:all' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
bash /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y xvfb libgobject-2.0-0 libglib2.0-0 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libgtk-3-0 libgbm1 libasound2
###ACTION_DELIMITER###
apt-get update && apt-get install -y xvfb libglib2.0-0 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libgtk-3-0 libgbm1 libasound2
###ACTION_DELIMITER###
bash /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd src && yarn workspaces foreach run test
CYPRESS_ENV=local yarn --cwd ../test/cypress test:all' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
bash /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd "$(dirname "$0")" || exit 1
cd src && yarn workspaces foreach run test
CYPRESS_ENV=local yarn --cwd ../test/cypress test:all' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd /home/app-frontend-react || exit 1
# Run workspace tests
cd src/altinn-app-frontend && yarn test
# Run Cypress tests with valid environment
cd ../../test/cypress && ENV=local yarn test:all' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
bash /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd /home/app-frontend-react || exit 1
cd src/altinn-app-frontend && yarn test
cd ../../test/cypress && ENV=local yarn test:all' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd /home/app-frontend-react || exit 1
cd src/altinn-app-frontend && yarn test
cd ../../test/cypress && CYPRESS_env=local yarn test:all' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd /home/app-frontend-react || exit 1
cd src/altinn-app-frontend && yarn test
cd ../../test/cypress && CYPRESS_ENV=local yarn test:all' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd /home/app-frontend-react || exit 1
# Run workspace tests
cd src/altinn-app-frontend && yarn test
# Run Cypress tests with explicit environment
cd ../../test/cypress && export ENV=local && yarn test:all' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
bash /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd /home/app-frontend-react || exit 1
# Run workspace tests
cd src/altinn-app-frontend && yarn test
# Run Cypress tests with inline environment variable
cd ../../test/cypress && ENV=local yarn test:all' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd /home/app-frontend-react || exit 1
# Run workspace tests
cd src/altinn-app-frontend && yarn test
# Run Cypress tests with explicit environment via --env
cd ../../test/cypress && yarn test:all --env ENV=local' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd /home/app-frontend-react || exit 1
# Run workspace tests
cd src/altinn-app-frontend && yarn test
# Run Cypress tests with explicit config environment
cd ../../test/cypress && yarn test:all --config env=local' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd /home/app-frontend-react || exit 1
# Run workspace tests
cd src/altinn-app-frontend && yarn test
# Run Cypress tests with explicit --env flag
cd ../../test/cypress && yarn delete:reports && cypress run -b chrome -s "e2e/integration/*/*.js" --env env=local' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd /home/app-frontend-react || exit 1
# Run workspace tests
cd src/altinn-app-frontend && yarn test
# Export environment variable and run Cypress tests
cd ../../test/cypress && export ENV=local && yarn test:all' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd /home/app-frontend-react || exit 1
# Run workspace tests
cd src/altinn-app-frontend && yarn test
# Run Cypress tests with explicit environment variable
cd ../../test/cypress && yarn test:all --env environment=local' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
bash /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd /home/app-frontend-react || exit 1
# Run workspace tests
cd src/altinn-app-frontend && yarn test
# Run Cypress tests with Electron browser and start server
cd ../../test/cypress && yarn install && start-server-and-test "yarn before:appfrontend" http://local.altinn.cloud "yarn cy:run --env environment=local -b electron"' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd /home/app-frontend-react || exit 1
# Run workspace tests
cd src/altinn-app-frontend && yarn test
# Run Cypress tests with Electron, start server, and set environment
cd ../../test/cypress && yarn delete:reports || true && start-server-and-test "yarn before:appfrontend" http://local.altinn.cloud "yarn cy:run --env environment=local -b electron"' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
bash /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd /home/app-frontend-react || exit 1
# Run workspace tests
cd src/altinn-app-frontend && yarn test
# Run Cypress tests with Yarn-managed start-server-and-test
cd ../../test/cypress && yarn delete:reports || true && yarn run start-server-and-test "yarn before:appfrontend" http://local.altinn.cloud "yarn cy:run --env environment=local -b electron"' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd /home/app-frontend-react || exit 1
# Run workspace tests
cd src/altinn-app-frontend && yarn test
# Run Cypress tests with Yarn-managed dependencies and server
cd ../../test/cypress && yarn delete:reports || true && yarn run start-server-and-test --timeout 300000 "yarn before:appfrontend" http://local.altinn.cloud "yarn cy:run --env environment=local -b electron"' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
bash /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
apt-get update && apt-get install -y procps
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd /home/app-frontend-react || exit 1
# Run workspace tests
cd src/altinn-app-frontend && yarn test
# Run Cypress tests with proper timeout and server setup
cd ../../test/cypress && yarn delete:reports || true && yarn run start-server-and-test "yarn before:appfrontend" http://local.altinn.cloud "yarn cy:run --env environment=local -b electron" --timeout 300000' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
bash /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
echo -e 'LOCALTEST_PATH=/home/app-frontend-react/test/cypress
APP_FRONTEND_PATH=/home/app-frontend-react/src/altinn-app-frontend
APP_PATH=/home/app-frontend-react' > /home/app-frontend-react/test/cypress/.env && echo -e '#!/bin/bash
cd /home/app-frontend-react || exit 1
cd src/altinn-app-frontend && yarn test
cd ../../test/cypress && yarn delete:reports || true && yarn run start-server-and-test "yarn before:appfrontend" http://local.altinn.cloud "yarn cy:run --env environment=local -b electron" --timeout 300000' > /home/app-frontend-react/test_commands.sh && chmod +x /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
bash /home/app-frontend-react/test_commands.sh
###ACTION_DELIMITER###
""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
cd /home/app-frontend-react || exit 1
cd src/altinn-app-frontend && yarn test
cd ../../test/cypress && yarn delete:reports || true && yarn run start-server-and-test "yarn before:appfrontend" http://local.altinn.cloud "yarn cy:run --env environment=local -b electron" --timeout 300000

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
cd /home/app-frontend-react || exit 1
cd src/altinn-app-frontend && yarn test
cd ../../test/cypress && yarn delete:reports || true && yarn run start-server-and-test "yarn before:appfrontend" http://local.altinn.cloud "yarn cy:run --env environment=local -b electron" --timeout 300000

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
cd /home/app-frontend-react || exit 1
cd src/altinn-app-frontend && yarn test
cd ../../test/cypress && yarn delete:reports || true && yarn run start-server-and-test "yarn before:appfrontend" http://local.altinn.cloud "yarn cy:run --env environment=local -b electron" --timeout 300000

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

# Choose an appropriate base image based on the project's requirements - replace node:18-bullseye-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:18-bullseye-slim

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
RUN git clone https://github.com/Altinn/app-frontend-react.git /home/app-frontend-react

WORKDIR /home/app-frontend-react
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Altinn", "app_frontend_react_713_to_683")
class APP_FRONTEND_REACT_713_TO_683(Instance):
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
        passed_tests: set[str] = set()
        failed_tests: set[str] = set()
        skipped_tests: set[str] = set()
        import re

        # Unified pattern to match PASS/FAIL/SKIP with variations
        pattern = re.compile(
            r"^(?:\[\s*\d+\]\s+)?(PASS|FAIL(?:ED)?|SKIP(?:PED)?)\s+([^\s]+)(?:\s*\(\d+\.\d+\s+s\))?$",
            re.MULTILINE | re.IGNORECASE,
        )
        for match in pattern.finditer(log):
            status = match.group(1).upper()  # Normalize to uppercase
            test_name = match.group(2).strip()
            if status.startswith("PASS"):
                passed_tests.add(test_name)
            elif status.startswith("FAIL"):
                failed_tests.add(test_name)
            elif status.startswith("SKIP"):
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
