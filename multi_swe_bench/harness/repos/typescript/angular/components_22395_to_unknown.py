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
        return "node:18-bullseye"
    
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
                """node -v && yarn -v
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && nvm install 12 && nvm alias default 12 && node -v
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo 'yarn test --verbose' > /home/components/test_commands.sh && echo 'yarn e2e' >> /home/components/test_commands.sh && echo 'yarn integration-tests:size-test' >> /home/components/test_commands.sh
###ACTION_DELIMITER###
cat /home/components/test_commands.sh
###ACTION_DELIMITER###
bash /home/components/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/^yarn test --verbose/yarn test all --verbose/' /home/components/test_commands.sh
###ACTION_DELIMITER###
cat /home/components/test_commands.sh
###ACTION_DELIMITER###
bash /home/components/test_commands.sh
###ACTION_DELIMITER###
echo 'fs.inotify.max_user_watches=524288' | tee -a /etc/sysctl.conf && sysctl -p
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential python3 chromium
###ACTION_DELIMITER###
echo 524288 > /proc/sys/fs/inotify/max_user_watches
###ACTION_DELIMITER###
echo 'export CHROME_BIN=/usr/bin/chromium' > /home/components/test_commands.sh && echo 'yarn test all' >> /home/components/test_commands.sh && echo 'yarn e2e --test_arg=--headless' >> /home/components/test_commands.sh && echo 'yarn integration-tests:size-test' >> /home/components/test_commands.sh
###ACTION_DELIMITER###
cat /home/components/test_commands.sh
###ACTION_DELIMITER###
bash /home/components/test_commands.sh
###ACTION_DELIMITER###
cat /root/.cache/bazel/_bazel_root/71a4d0fb8483275e3b7a2a68023bf59f/execroot/angular_material/bazel-out/k8-fastbuild/testlogs/integration/size-test/material/form-field/advanced/test.log
###ACTION_DELIMITER###
yarn build
###ACTION_DELIMITER###
bash /home/components/test_commands.sh
###ACTION_DELIMITER###
echo 'export CHROME_BIN=/usr/bin/chromium' > /home/components/test_commands.sh && echo 'yarn build' >> /home/components/test_commands.sh && echo 'bazel build //integration/size-test/...' >> /home/components/test_commands.sh && echo 'yarn test all' >> /home/components/test_commands.sh && echo 'yarn e2e --test_arg=--headless' >> /home/components/test_commands.sh && echo 'yarn integration-tests:size-test' >> /home/components/test_commands.sh
###ACTION_DELIMITER###
cat /home/components/test_commands.sh
###ACTION_DELIMITER###
bash /home/components/test_commands.sh
###ACTION_DELIMITER###
echo 'export CHROME_BIN=/usr/bin/chromium' > /home/components/test_commands.sh && echo 'yarn build --enable-ivy' >> /home/components/test_commands.sh && echo 'bazel build //integration/size-test/... --define=compile=ivy' >> /home/components/test_commands.sh && echo 'yarn test all --verbose' >> /home/components/test_commands.sh && echo 'yarn e2e --test_arg=--headless --test_output=all' >> /home/components/test_commands.sh && echo 'yarn integration-tests:size-test --test_output=all' >> /home/components/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
export CHROME_BIN=/usr/bin/chromium
yarn build --enable-ivy
bazel build //integration/size-test/... --define=compile=ivy
yarn test all --verbose
yarn e2e --test_arg=--headless --test_output=all
yarn integration-tests:size-test --test_output=all

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
export CHROME_BIN=/usr/bin/chromium
yarn build --enable-ivy
bazel build //integration/size-test/... --define=compile=ivy
yarn test all --verbose
yarn e2e --test_arg=--headless --test_output=all
yarn integration-tests:size-test --test_output=all

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
export CHROME_BIN=/usr/bin/chromium
yarn build --enable-ivy
bazel build //integration/size-test/... --define=compile=ivy
yarn test all --verbose
yarn e2e --test_arg=--headless --test_output=all
yarn integration-tests:size-test --test_output=all

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

# Choose an appropriate base image based on the project's requirements - replace node:18-bullseye with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:18-bullseye

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
RUN git clone https://github.com/angular/components.git /home/components

WORKDIR /home/components
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("angular", "components_22395_to_unknown")
class COMPONENTS_22395_TO_UNKNOWN(Instance):
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
        import json
        # Regex patterns to match test status lines
        prefix_pattern = re.compile(r'^\s*(FAIL|PASS|SKIPPED):\s*(//[\w/:.-]+)')
        test_pattern = re.compile(r'^\s*(//[\w/:.-]+)\s+(FAILED|PASSED|SKIPPED)\b')
        for line in log.split('\n'):
            # Check for lines starting with status prefix (e.g., "FAIL: //test")
            prefix_match = prefix_pattern.match(line)
            if prefix_match:
                status = prefix_match.group(1)
                test_name = prefix_match.group(2)
                # Normalize status to standard terms
                if status == 'FAIL':
                    status = 'FAILED'
                elif status == 'PASS':
                    status = 'PASSED'
                # Add to the corresponding set
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
                continue
            # Check for lines with test name followed by status (e.g., "//test FAILED")
            test_match = test_pattern.match(line)
            if test_match:
                test_name = test_match.group(1)
                status = test_match.group(2)
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
                continue
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
