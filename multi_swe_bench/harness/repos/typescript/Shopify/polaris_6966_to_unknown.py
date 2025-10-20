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
                """echo -e '#!/bin/bash
yarn test -- --verbose' > /home/polaris/test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential python3 curl
###ACTION_DELIMITER###
echo -e '#!/bin/bash
turbo run test -- --verbose' > /home/polaris/test_commands.sh
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
###ACTION_DELIMITER###
apt-get install nodejs -y
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo -e '#!/bin/bash
turbo run test -- --verbose' > /home/polaris/test_commands.sh && chmod +x /home/polaris/test_commands.sh
###ACTION_DELIMITER###
bash /home/polaris/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn turbo run test -- --verbose' > /home/polaris/test_commands.sh && chmod +x /home/polaris/test_commands.sh
###ACTION_DELIMITER###
bash /home/polaris/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn turbo run test -- --verbose' > /home/polaris/test_commands.sh && chmod +x /home/polaris/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn test -- -- --verbose' > /home/polaris/test_commands.sh && chmod +x /home/polaris/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn workspaces run test --verbose' > /home/polaris/test_commands.sh && chmod +x /home/polaris/test_commands.sh
###ACTION_DELIMITER###
bash /home/polaris/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn turbo run test --filter=!polaris-for-figma -- --verbose' > /home/polaris/test_commands.sh && chmod +x /home/polaris/test_commands.sh
###ACTION_DELIMITER###
bash /home/polaris/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
workspaces=("polaris-tokens" "polaris-for-vscode" "polaris-icons" "polaris-react" "stylelint-polaris" "polaris.shopify.com")
for ws in "${workspaces[@]}"; do
  cd "$ws"
  if [ -f "package.json" ] && grep -q "test" "package.json"; then
    yarn test --verbose
  fi
  cd ..
done' > /home/polaris/test_commands.sh && chmod +x /home/polaris/test_commands.sh
###ACTION_DELIMITER###
bash /home/polaris/test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y jq && echo -e '#!/bin/bash
set -e
workspaces=("polaris-tokens" "polaris-for-vscode" "polaris-icons" "polaris-react" "stylelint-polaris" "polaris.shopify.com")
for ws in "${workspaces[@]}"; do
  cd "$ws"
  if [ -f "package.json" ] && jq -e '.scripts.test' package.json > /dev/null; then
    yarn test --verbose
  fi
  cd ..
done' > /home/polaris/test_commands.sh && chmod +x /home/polaris/test_commands.sh
###ACTION_DELIMITER###
bash /home/polaris/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
# Build polaris-tokens first as it is a dependency
cd polaris-tokens
if [ -f "package.json" ] && jq -e '.scripts.build' package.json > /dev/null; then
  yarn build
fi
cd ..
# Run tests in valid workspaces
workspaces=("polaris-tokens" "polaris-for-vscode" "polaris-icons" "polaris-react" "stylelint-polaris" "polaris.shopify.com")
for ws in "${workspaces[@]}"; do
  cd "$ws"
  if [ -f "package.json" ] && jq -e '.scripts.test' package.json > /dev/null; then
    yarn test --verbose
  fi
  cd ..
done' > /home/polaris/test_commands.sh && chmod +x /home/polaris/test_commands.sh
###ACTION_DELIMITER###
bash /home/polaris/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
# Build dependencies first
cd polaris-tokens
if [ -f "package.json" ] && jq -e '.scripts.build' package.json > /dev/null; then
  yarn build
fi
cd ..
cd polaris-icons
if [ -f "package.json" ] && jq -e '.scripts.build' package.json > /dev/null; then
  yarn build
fi
cd ..
# Run tests in valid workspaces
workspaces=("polaris-tokens" "polaris-for-vscode" "polaris-icons" "polaris-react" "stylelint-polaris" "polaris.shopify.com")
for ws in "${workspaces[@]}"; do
  cd "$ws"
  if [ -f "package.json" ] && jq -e '.scripts.test' package.json > /dev/null; then
    yarn test --verbose
  fi
  cd ..
done' > /home/polaris/test_commands.sh && chmod +x /home/polaris/test_commands.sh
###ACTION_DELIMITER###
bash /home/polaris/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e
# Build dependencies first
cd polaris-tokens
if [ -f "package.json" ] && jq -e .scripts.build package.json > /dev/null; then
  yarn build
fi
cd ..
cd polaris-icons
if [ -f "package.json" ] && jq -e .scripts.build package.json > /dev/null; then
  yarn build
fi
cd ..
# Run tests in valid workspaces
workspaces=("polaris-tokens" "polaris-for-vscode" "polaris-icons" "polaris-react" "stylelint-polaris" "polaris.shopify.com")
for ws in "${workspaces[@]}"; do
  cd "$ws"
  if [ -f "package.json" ] && jq -e .scripts.test package.json > /dev/null; then
    yarn test --verbose
  fi
  cd ..
done

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
#!/bin/bash
set -e
# Build dependencies first
cd polaris-tokens
if [ -f "package.json" ] && jq -e .scripts.build package.json > /dev/null; then
  yarn build
fi
cd ..
cd polaris-icons
if [ -f "package.json" ] && jq -e .scripts.build package.json > /dev/null; then
  yarn build
fi
cd ..
# Run tests in valid workspaces
workspaces=("polaris-tokens" "polaris-for-vscode" "polaris-icons" "polaris-react" "stylelint-polaris" "polaris.shopify.com")
for ws in "${workspaces[@]}"; do
  cd "$ws"
  if [ -f "package.json" ] && jq -e .scripts.test package.json > /dev/null; then
    yarn test --verbose
  fi
  cd ..
done

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
#!/bin/bash
set -e
# Build dependencies first
cd polaris-tokens
if [ -f "package.json" ] && jq -e .scripts.build package.json > /dev/null; then
  yarn build
fi
cd ..
cd polaris-icons
if [ -f "package.json" ] && jq -e .scripts.build package.json > /dev/null; then
  yarn build
fi
cd ..
# Run tests in valid workspaces
workspaces=("polaris-tokens" "polaris-for-vscode" "polaris-icons" "polaris-react" "stylelint-polaris" "polaris.shopify.com")
for ws in "${workspaces[@]}"; do
  cd "$ws"
  if [ -f "package.json" ] && jq -e .scripts.test package.json > /dev/null; then
    yarn test --verbose
  fi
  cd ..
done

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
RUN git clone https://github.com/Shopify/polaris.git /home/polaris

WORKDIR /home/polaris
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Shopify", "polaris_6966_to_unknown")
class POLARIS_6966_TO_UNKNOWN(Instance):
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
        passed_tests = set() # Tests that passed successfully
        failed_tests = set() # Tests that failed
        skipped_tests = set() # Tests that were skipped
        import re
        # Remove ANSI escape codes (e.g., color codes) from log content
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        log_clean = ansi_escape.sub('', log)
        # Regex patterns for passed, failed, and skipped tests (Jest format with line numbers)
        passed_pattern = re.compile(r'✓\s+(.*)(?:\s*\(\d+ ms\))?')
        failed_pattern = re.compile(r'✕\s+(.*)(?:\s*\(\d+ ms\))?')
        skipped_pattern = re.compile(r'○\s+(.*)(?:\s*\(\d+ ms\))?')
        lines = log_clean.split('\n')
        # Regex to remove trailing time components
        time_pattern = re.compile(r'\s*\(\d+ ms\)$')
        for line in lines:
            # Check for passed tests
            passed_match = passed_pattern.search(line)
            if passed_match:
                test_name = passed_match.group(1).strip()
                test_name = time_pattern.sub('', test_name).strip()
                passed_tests.add(test_name)
            # Check for failed tests
            failed_match = failed_pattern.search(line)
            if failed_match:
                test_name = failed_match.group(1).strip()
                test_name = time_pattern.sub('', test_name).strip()
                failed_tests.add(test_name)
            # Check for skipped tests
            skipped_match = skipped_pattern.search(line)
            if skipped_match:
                test_name = skipped_match.group(1).strip()
                skipped_tests.add(test_name)
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
