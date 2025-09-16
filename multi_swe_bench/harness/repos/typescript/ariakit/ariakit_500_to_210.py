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
        return "node:20"
    
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
yarn install
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2.7
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2
###ACTION_DELIMITER###
PYTHON=python3 yarn install
###ACTION_DELIMITER###
npm config set python python3 && yarn install
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3
###ACTION_DELIMITER###
apt-get update && apt-get install -y libvips-dev
###ACTION_DELIMITER###
PYTHON=python3 yarn install
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential && ln -s /usr/bin/python3 /usr/bin/python && yarn install
###ACTION_DELIMITER###
npm install -g node-gyp && SHARP_USE_SYSTEM_LIBVIPS=1 yarn install
###ACTION_DELIMITER###
rm -rf node_modules yarn.lock && yarn cache clean && SHARP_IGNORE_GLOBAL_LIBVIPS=1 yarn install
###ACTION_DELIMITER###
npm install -g node-gyp@latest && npm cache clean -f && SHARP_IGNORE_GLOBAL_LIBVIPS=1 yarn install
###ACTION_DELIMITER###
echo '#!/bin/bash
apt-get update && apt-get install -y python3.10 python3-pip
pip3 install --upgrade pip
pip3 install -r requirements.txt
pytest --verbose --json-report=report.json'
###ACTION_DELIMITER###
echo -e '#!/bin/bash
 yarn test --verbose --reporters=default --reporters=jest-junit --color=never' > /home/ariakit/test_commands.sh && chmod +x /home/ariakit/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
npm test -- --verbose --color=never' > /home/ariakit/test_commands.sh && chmod +x /home/ariakit/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn test --verbose --color=never' > /home/ariakit/test_commands.sh && chmod +x /home/ariakit/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
yarn test --verbose --color=never

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
yarn test --verbose --color=never

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
yarn test --verbose --color=never

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
FROM node:20

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
RUN git clone https://github.com/ariakit/ariakit.git /home/ariakit

WORKDIR /home/ariakit
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ariakit", "ariakit_500_to_210")
class ARIAKIT_500_TO_210(Instance):
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
        import json
        # Remove ANSI escape codes
        # Fix ANSI escape code removal with correct regex
        log_clean = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', log)
        # Adjust patterns to match log structure (e.g., '  ✓ initial state (70ms)')
        # Capture test name between ✓ and (time), allowing for spaces
        # Make time component optional and capture test names with optional whitespace
        passed_pattern = re.compile(r'^\s*✓\s+(.*?)\s*(?:\(\d+ms\))?$', re.MULTILINE)
        # Failed tests may use '✕' or other markers; adjust pattern for optional time
        failed_pattern = re.compile(r'^\s*✕\s+(.*?)\s*(?:\(\d+ms\))?$', re.MULTILINE)
        # Skipped tests pattern (update marker if log uses different symbol)
        skipped_pattern = re.compile(r'^\s*○\s+(.*?)\s*(?:\(\d+ms\))?$', re.MULTILINE)
        # Extract test names
        passed_tests = set(passed_pattern.findall(log_clean))
        failed_tests = set(failed_pattern.findall(log_clean))
        skipped_tests = set(skipped_pattern.findall(log_clean))
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
