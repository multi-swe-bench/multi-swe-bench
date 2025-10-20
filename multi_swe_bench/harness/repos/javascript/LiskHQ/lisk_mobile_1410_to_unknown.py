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
                """npm install
###ACTION_DELIMITER###
npm install -g npm@11.6.0
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
###ACTION_DELIMITER###
nvm install 16
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && npm install
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
echo -e '#!/bin/bash
npm test -- --verbose
cd android && ./gradlew --project-cache-dir ../.gradlecache test --continue' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
npm test -- --verbose
cd android && ./gradlew --project-cache-dir ../.gradlecache test --continue

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
npm test -- --verbose
cd android && ./gradlew --project-cache-dir ../.gradlecache test --continue

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
npm test -- --verbose
cd android && ./gradlew --project-cache-dir ../.gradlecache test --continue

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
RUN git clone https://github.com/LiskHQ/lisk-mobile.git /home/lisk-mobile

WORKDIR /home/lisk-mobile
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("LiskHQ", "lisk_mobile_1410_to_unknown")
class LISK_MOBILE_1410_TO_UNKNOWN(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        import json  # Kept as per skeleton, though not used in this implementation
        context = []  # Tracks the current test group hierarchy
        lines = log.split('\n')
        for line in lines:
            leading_spaces = len(line) - len(line.lstrip(' '))
            content = line.strip()
            if not content:
                continue
            # Check if it's a test case line
            if '✓' in content or '✕' in content or '○' in content:
                # Determine status
                if '✓' in content:
                    status = 'passed'
                elif '✕' in content:
                    status = 'failed'
                else:  # '○'
                    status = 'skipped'
                # Extract test description (remove status marker and duration)
                marker = '✓' if status == 'passed' else '✕' if status == 'failed' else '○'
                parts = re.split(re.escape(marker), content, 1)
                if len(parts) < 2:
                    continue  # invalid format, skip
                description_part = parts[1].strip()
                # Remove duration (e.g., (14 ms))
                description = re.sub(r'\(\d+ ms\)$', '', description_part).strip()
                # Combine with context to form full test name
                full_name = ' '.join(context) + ' ' + description if context else description
                # Add to the appropriate set
                if status == 'passed':
                    passed_tests.add(full_name)
                elif status == 'failed':
                    failed_tests.add(full_name)
                else:
                    skipped_tests.add(full_name)
            else:
                # Check if it's a group line (indented, not a test case)
                current_indent_level = leading_spaces // 2
                # Adjust context to match current indent level
                while len(context) >= current_indent_level:
                    if context:
                        context.pop()
                    else:
                        break
                # Add the group name to context
                group_name = content
                context.append(group_name)
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
