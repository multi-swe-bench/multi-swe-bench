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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y openjdk-11-jdk
###ACTION_DELIMITER###
apt-get install -y maven
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
###ACTION_DELIMITER###
apt-get install -y nodejs
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
cd comixed-webui && yarn install
###ACTION_DELIMITER###
sed -i '/coverageReporter:/a \  customLaunchers: {\n    ChromeHeadlessNoSandbox: {\n      base: "ChromeHeadless",\n      flags: ["--no-sandbox"]\n    }\n  },' karma.conf.js && sed -i 's/browsers: \[\x27ChromeHeadless\x27\]/browsers: \[\x27ChromeHeadlessNoSandbox\x27\]/' karma.conf.js
###ACTION_DELIMITER###
echo -e '#!/bin/bash
mvn clean test -Dstyle.color=never
cd comixed-webui
yarn test' > ../test_commands.sh && chmod +x ../test_commands.sh
###ACTION_DELIMITER###
cd /home/comixed && bash test_commands.sh
###ACTION_DELIMITER###
cd comixed-webui && yarn add --dev karma-chrome-launcher && sed -i '/browsers:/i \  customLaunchers: {\n    ChromeHeadlessNoSandbox: {\n      base: "ChromeHeadless",\n      flags: ["--no-sandbox"]\n    }\n  },' karma.conf.js && sed -i 's/browsers: \[\x27ChromeHeadless\x27\]/browsers: \[\x27ChromeHeadlessNoSandbox\x27\]/' karma.conf.js
###ACTION_DELIMITER###
apt-get install -y libnss3 libxss1 libasound2 && cd comixed-webui && sed -i 's/coverageReporter:/customLaunchers: {\n    ChromeHeadlessNoSandbox: {\n      base: "ChromeHeadless",\n      flags: ["--no-sandbox"]\n    }\n  },\n  coverageReporter:/' karma.conf.js && sed -i 's/browsers: \[\x27ChromeHeadless\x27\]/browsers: \[\x27ChromeHeadlessNoSandbox\x27\]/' karma.conf.js
###ACTION_DELIMITER###
apt-get install -y libnss3 libxss1 libasound2t64 && cd comixed-webui && sed -i '/module.exports = function(config) {/a \  config.set({\n    customLaunchers: {\n      ChromeHeadlessNoSandbox: {\n        base: "ChromeHeadless",\n        flags: ["--no-sandbox"]\n      }\n    },' karma.conf.js && sed -i 's/browsers: \[\x27ChromeHeadless\x27\]/browsers: \[\x27ChromeHeadlessNoSandbox\x27\]/' karma.conf.js
###ACTION_DELIMITER###
apt-get install -y libnss3 libxss1 libasound2t64 && sed -i '/config.set({/a \    customLaunchers: {\n      ChromeHeadlessNoSandbox: {\n        base: "ChromeHeadless",\n        flags: ["--no-sandbox"]\n      }\n    },' karma.conf.js && sed -i 's/browsers: \[\x27ChromeHeadless\x27\]/browsers: \[\x27ChromeHeadlessNoSandbox\x27\]/' karma.conf.js
###ACTION_DELIMITER###
sed -i '/config.set({/a \    customLaunchers: {\n      ChromeHeadlessNoSandbox: {\n        base: "ChromeHeadless",\n        flags: ["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]\n      }\n    },' karma.conf.js && sed -i 's/browsers: \[\x27ChromeHeadless\x27\]/browsers: \[\x27ChromeHeadlessNoSandbox\x27\]/' karma.conf.js && yarn test
###ACTION_DELIMITER###
apt-get install -y chromium-browser && export CHROME_BIN=/usr/bin/chromium-browser && yarn test
###ACTION_DELIMITER###
apt-get install -y wget && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && dpkg -i google-chrome-stable_current_amd64.deb || apt-get -f install -y && export CHROME_BIN=/usr/bin/google-chrome && yarn test
###ACTION_DELIMITER###
cd /home/comixed && bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
mvn clean test -Dstyle.color=never
cd comixed-webui
yarn test

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
mvn clean test -Dstyle.color=never
cd comixed-webui
yarn test

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
mvn clean test -Dstyle.color=never
cd comixed-webui
yarn test

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
RUN git clone https://github.com/comixed/comixed.git /home/comixed

WORKDIR /home/comixed
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("comixed", "comixed_1432_to_1236")
class COMIXED_1432_TO_1236(Instance):
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

        # Implement the log parsing logic here
        # Regex pattern to match test summary lines
        pattern = r"Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+).* - in (.*)"
        matches = re.findall(pattern, log)
        for match in matches:
            # Extract the counts and test class name
            _, failures, errors, skips, test_class = match
            failures = int(failures)
            errors = int(errors)
            skips = int(skips)
            if failures > 0 or errors > 0:
                failed_tests.add(test_class)
            elif skips > 0:
                skipped_tests.add(test_class)
            else:
                passed_tests.add(test_class)
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
