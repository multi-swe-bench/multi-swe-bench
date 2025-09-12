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
apt-get update && apt-get install -y wget && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && apt-get update && apt-get install -y google-chrome-stable
###ACTION_DELIMITER###
export PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=1 && yarn && yarn build-all
###ACTION_DELIMITER###
cat << EOF > test_commands.sh
#!/bin/bash

yarn bundlesize
 yarn diff:sample-json
 yarn lint
 yarn unit:cicoverage
 yarn type-check
 yarn smoke:cicoverage
 yarn test-clients
 yarn test-viewer
 yarn test-lantern
 yarn i18n:checks
EOF
###ACTION_DELIMITER###
echo '#!/bin/bash' > test_commands.sh && echo 'yarn bundlesize' >> test_commands.sh && echo 'yarn diff:sample-json' >> test_commands.sh && echo 'yarn lint' >> test_commands.sh && echo 'yarn unit:cicoverage' >> test_commands.sh && echo 'yarn type-check' >> test_commands.sh && echo 'yarn smoke:cicoverage' >> test_commands.sh && echo 'yarn test-clients' >> test_commands.sh && echo 'yarn test-viewer' >> test_commands.sh && echo 'yarn test-lantern' >> test_commands.sh && echo 'yarn i18n:checks' >> test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
yarn bundlesize
yarn diff:sample-json
yarn lint
yarn unit:cicoverage
yarn type-check
yarn smoke:cicoverage
yarn test-clients
yarn test-viewer
yarn test-lantern
yarn i18n:checks

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
yarn bundlesize
yarn diff:sample-json
yarn lint
yarn unit:cicoverage
yarn type-check
yarn smoke:cicoverage
yarn test-clients
yarn test-viewer
yarn test-lantern
yarn i18n:checks

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
yarn bundlesize
yarn diff:sample-json
yarn lint
yarn unit:cicoverage
yarn type-check
yarn smoke:cicoverage
yarn test-clients
yarn test-viewer
yarn test-lantern
yarn i18n:checks

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

# Choose an appropriate base image based on the project's requirements - replace node:20 with actual base image
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
RUN git clone https://github.com/GoogleChrome/lighthouse.git /home/lighthouse

WORKDIR /home/lighthouse
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("GoogleChrome", "lighthouse_9073_to_8340")
class LIGHTHOUSE_9073_TO_8340(Instance):
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
        # Extract test names from PASS/FAIL lines (excluding non-test entries)
        # Regex patterns target test files in specific directories
        passed_pattern = r'PASS\s+(lighthouse-core/test/.*?\.js|clients/test/.*?\.js|lighthouse-viewer/test/.*?\.js)'
        failed_pattern = r'FAIL\s+(lighthouse-core/test/.*?\.js|clients/test/.*?\.js|lighthouse-viewer/test/.*?\.js)'
        skipped_pattern = r'SKIP\s+(lighthouse-core/test/.*?\.js|clients/test/.*?\.js|lighthouse-viewer/test/.*?\.js)'
        # Find all matches and convert to sets
        passed_tests = set(re.findall(passed_pattern, log))
        failed_tests = set(re.findall(failed_pattern, log))
        skipped_tests = set(re.findall(skipped_pattern, log))
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
