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
                """apt-get update && apt-get install -y libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 libxtst6 xauth xvfb
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
npm install --ignore-scripts
###ACTION_DELIMITER###
ls node_modules/.bin
###ACTION_DELIMITER###
cat package.json
###ACTION_DELIMITER###
echo -e '#!/bin/bash
./node_modules/.bin/ng test igniteui-angular --watch=false --no-progress --code-coverage --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
./node_modules/.bin/ng test --help
###ACTION_DELIMITER###
echo -e '#!/bin/bash
./node_modules/.bin/ng test igniteui-angular --watch=false --no-progress --code-coverage --reporters spec' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
./node_modules/.bin/ng test igniteui-angular --watch=false --no-progress --code-coverage --reporters spec --browsers ChromeHeadless' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cat > karma.temp.conf.js << EOF
const defaultConfig = require(\'./projects/igniteui-angular/karma.conf.js\');
module.exports = function(config) {
  defaultConfig(config);
  config.set({
    customLaunchers: {
      ChromeHeadlessNoSandbox: {
        base: \'ChromeHeadless\',
        flags: [\'--no-sandbox\', \'--disable-gpu\']
      }
    }
  });
};
EOF
./node_modules/.bin/ng test igniteui-angular --watch=false --no-progress --code-coverage --reporters spec --browsers ChromeHeadlessNoSandbox --karma-config karma.temp.conf.js' > test_commands.sh
###ACTION_DELIMITER###
cat << 'EOF' > karma.temp.conf.js
const defaultConfig = require('./projects/igniteui-angular/karma.conf.js');
module.exports = function(config) {
  defaultConfig(config);
  config.set({
    browsers: ['ChromeHeadlessNoSandbox'],
    customLaunchers: {
      ChromeHeadlessNoSandbox: {
        base: 'ChromeHeadless',
        flags: ['--no-sandbox', '--disable-gpu']
      }
    }
  });
};
EOF
###ACTION_DELIMITER###
echo -e '#!/bin/bash
./node_modules/.bin/ng test igniteui-angular --watch=false --no-progress --code-coverage --reporters spec --karma-config=karma.temp.conf.js' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
./node_modules/.bin/ng test igniteui-angular --watch=false --no-progress --code-coverage --reporters spec --karma-config=karma.temp.conf.js

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
./node_modules/.bin/ng test igniteui-angular --watch=false --no-progress --code-coverage --reporters spec --karma-config=karma.temp.conf.js

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
./node_modules/.bin/ng test igniteui-angular --watch=false --no-progress --code-coverage --reporters spec --karma-config=karma.temp.conf.js

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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
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
RUN git clone https://github.com/IgniteUI/igniteui-angular.git /home/igniteui-angular

WORKDIR /home/igniteui-angular
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("IgniteUI", "igniteui_angular_13922_to_13914")
class IGNITEUI_ANGULAR_13922_TO_13914(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re

        # Track final status to avoid overlaps (a test can only have one status)
        test_status = {}
        # Refined regex patterns (stop at ANSI codes or line end)
        passed_pattern = re.compile(
            r".*?\x1b\[\d*;?32m✓ \x1b\[39m(.*?)(?:\x1b|$)"
        )  # Green checkmark (handle optional ANSI styles)
        failed_pattern = re.compile(
            r".*?\x1b\[.*?31m\d+\)\s*(.*?)(?:\x1b|$)"
        )  # Red failed (permissive test name capture)
        skipped_pattern = re.compile(
            r"\x1b\[33m(.*?) \(skipped\)"
        )  # Assume skipped is yellow (adjust if needed)
        for line in log.split("\n"):
            line = line.strip()
            # Prioritize failed > passed > skipped (adjust if logs use different priority)
            failed_match = failed_pattern.search(line)
            if failed_match:
                test_name = failed_match.group(1).strip()
                # Remove any remaining ANSI codes from the test name
                test_name = re.sub(r"\x1b\[\d*;?\d*m", "", test_name)
                if test_name not in test_status:
                    test_status[test_name] = "failed"
                continue
            passed_match = passed_pattern.search(line)
            if passed_match:
                test_name = passed_match.group(1).strip()
                if test_name not in test_status:
                    test_status[test_name] = "passed"
                continue
            skipped_match = skipped_pattern.search(line)
            if skipped_match:
                test_name = skipped_match.group(1).strip()
                if test_name not in test_status:
                    test_status[test_name] = "skipped"
                continue
        # Populate sets from final statuses
        for test, status in test_status.items():
            if status == "passed":
                passed_tests.add(test)
            elif status == "failed":
                failed_tests.add(test)
            elif status == "skipped":
                skipped_tests.add(test)
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
