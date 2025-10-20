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
        return "node:18"
    
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
                """apt-get update && apt-get install -y libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libnss3 libcups2 libxss1 libxrandr2 libgconf-2-4 libasound2 libpangocairo-1.0-0 libatk1.0-0 libatk-bridge2.0-0 libgtk-3-0
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
###ACTION_DELIMITER###
nvm install 12
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo '#!/bin/bash
 yarn test -- --verbose --watch=false' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
 yarn test all --verbose --watch=false' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
 export CHROME_BIN=/usr/bin/chromium-browser
 export CHROME_FLAGS="--headless --disable-gpu --no-sandbox"
 yarn test all --verbose --watch=false' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
 echo fs.inotify.max_user_watches=524288 | tee -a /etc/sysctl.conf && sysctl -p
 export CHROME_BIN=/usr/bin/chromium-browser
 export CHROME_FLAGS="--headless --disable-gpu --no-sandbox --disable-dev-shm-usage"
 bazel test //... --test_output=all --test_arg=--verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y chromium-browser
###ACTION_DELIMITER###
apt-get update && apt-get install -y chromium
###ACTION_DELIMITER###
echo '#!/bin/bash
 export CHROME_BIN=/usr/bin/chromium
 export CHROME_FLAGS="--headless --disable-gpu --no-sandbox --disable-dev-shm-usage"
 yarn test all --verbose --watch=false' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
 sysctl -w fs.inotify.max_user_watches=524288
 export CHROME_BIN=/usr/bin/chromium
 export CHROME_FLAGS="--headless --disable-gpu --no-sandbox --disable-dev-shm-usage"
 yarn test all --verbose --watch=false --reporters=junit --reporters=json' > test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
 sysctl -w fs.inotify.max_user_watches=524288
 export CHROME_BIN=/usr/bin/chromium
 export CHROME_FLAGS="--headless --disable-gpu --no-sandbox --disable-dev-shm-usage"
 yarn test all --verbose --watch=false --browsers=ChromeHeadless' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
 export CHROME_BIN=/usr/bin/chromium
 export CHROME_FLAGS="--headless --disable-gpu --no-sandbox --disable-dev-shm-usage"
 yarn test all --verbose --watch=false --browsers=ChromeHeadless' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
 export CHROME_BIN=/usr/bin/chromium
 export CHROME_FLAGS="--headless --disable-gpu --no-sandbox --disable-dev-shm-usage"
 yarn test all --verbose --watch=false --browsers=ChromeHeadless

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
 export CHROME_BIN=/usr/bin/chromium
 export CHROME_FLAGS="--headless --disable-gpu --no-sandbox --disable-dev-shm-usage"
 yarn test all --verbose --watch=false --browsers=ChromeHeadless

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
 export CHROME_BIN=/usr/bin/chromium
 export CHROME_FLAGS="--headless --disable-gpu --no-sandbox --disable-dev-shm-usage"
 yarn test all --verbose --watch=false --browsers=ChromeHeadless

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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:18

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


@Instance.register("angular", "components_20082_to_19526")
class COMPONENTS_20082_TO_19526(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        # Pattern for passed tests: captures test name before (cached) and PASSED
        passed_pattern = re.compile(r'^(\S+)\s+(?:\(cached\)\s+)?PASSED', re.MULTILINE)
        passed_tests.update(passed_pattern.findall(log))
        # Pattern for failed tests: captures test name after FAIL:
        failed_pattern = re.compile(r'^FAIL:\s+(\S+)', re.MULTILINE)
        failed_tests.update(failed_pattern.findall(log))
        # Check for skipped tests (patterns based on common conventions)
        skipped_pattern = re.compile(r'^(\S+)\s+(?:\(cached\)\s+)?SKIPPED', re.MULTILINE)
        skipped_tests.update(skipped_pattern.findall(log))
        skipped_pattern2 = re.compile(r'^SKIPPED:\s+(\S+)', re.MULTILINE)
        skipped_tests.update(skipped_pattern2.findall(log))
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
