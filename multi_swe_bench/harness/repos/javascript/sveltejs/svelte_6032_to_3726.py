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
        return "node:16-bullseye"
    
    def image_prefix(self) -> str:
        return "envagent"
       
    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:
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
                """ls -F
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
npm test
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y libx11-xcb1
###ACTION_DELIMITER###
npm test
###ACTION_DELIMITER###
apt-get install -y libxcomposite1
###ACTION_DELIMITER###
apt-get install -y libxdamage1 libxext6 libxfixes3 libxrandr2 libxtst6 libnss3 libcups2 libatk1.0-0 libatk-bridge2.0-0 libasound2 libdrm2 libgbm1 libgtk-3-0 libxcb-dri3-0 libxss1 libappindicator3-1 libindicator3-7 libnotify4 libpango-1.0-0 libcairo2
###ACTION_DELIMITER###
apt-get install -y libxdamage1 libxext6 libxfixes3 libxrandr2 libxtst6 libnss3 libcups2 libatk1.0-0 libatk-bridge2.0-0 libasound2 libdrm2 libgbm1 libgtk-3-0 libxcb-dri3-0 libxss1 libayatana-appindicator3-1 libnotify4 libpango-1.0-0 libcairo2
###ACTION_DELIMITER###
npm test
###ACTION_DELIMITER###
sed -i "s/browser = await puppeteer.launch();/browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });/" test/custom-elements/index.ts
###ACTION_DELIMITER###

###ACTION_DELIMITER###
npm test
###ACTION_DELIMITER###
echo "npm test" > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
npm test

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
npm test

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn  /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
npm test

""".format(
                    pr=self.pr
                ),
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
FROM node:16-bullseye

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
RUN git clone https://github.com/sveltejs/svelte.git /home/svelte

WORKDIR /home/svelte
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("sveltejs", "svelte_6032_to_3726")
class SVELTE_6032_TO_3726(Instance):
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
        passed_tests = set() 
        failed_tests = set() 
        skipped_tests = set() 
        import re
        lines = log.splitlines()
        for i, line in enumerate(lines):
            if line.strip().startswith('✓'):
                test_name = line.strip().lstrip('✓').strip()
                passed_tests.add(test_name)
            elif 'pending' in line:
                # The log format doesn't provide individual skipped test names,
                # so we'll capture the line indicating pending tests.
                # Or, if there's a number, we can create placeholder names.
                match = re.search(r'(\d+)\s+pending', line)
                if match:
                    num_pending = int(match.group(1))
                    for i in range(num_pending):
                        skipped_tests.add(f"pending_test_{i+1}")
            elif 'AssertionError' in line:
                # Look for a preceding line that might contain the test name
                for j in range(i - 1, -1, -1):
                    prev_line = lines[j].strip()
                    if prev_line.endswith(':'):
                        test_name = prev_line.rstrip(':')
                        # Avoid adding overly broad or generic names
                        if 'expected' not in test_name.lower() and 'actual' not in test_name.lower():
                            failed_tests.add(test_name)
                            break
            elif 'cmd-click:' in line:
              test_path = line.split('cmd-click:')[1].strip()
              test_name = test_path.split('/')[-2]
              failed_tests.add(test_name)
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
