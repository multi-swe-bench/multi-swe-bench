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
        return "openjdk:17-jdk-slim"
    
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
                """ls -la /home/comixed
###ACTION_DELIMITER###
mvn --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y maven
###ACTION_DELIMITER###
mvn --version
###ACTION_DELIMITER###
mvn clean install -DskipTests
###ACTION_DELIMITER###
mvn clean test -Dstyle.color=never
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs && npm install -g yarn
###ACTION_DELIMITER###
yarn --version
###ACTION_DELIMITER###
mvn clean test -Dstyle.color=never
###ACTION_DELIMITER###
ls -la comixed-webui
###ACTION_DELIMITER###
cat comixed-webui/package.json
###ACTION_DELIMITER###
cd comixed-webui && yarn test
###ACTION_DELIMITER###
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && apt-get update && apt-get install -y google-chrome-stable
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg && sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && apt-get update && apt-get install -y google-chrome-stable
###ACTION_DELIMITER###
yarn test
###ACTION_DELIMITER###
sed -i '/browsers: \['\''ChromeHeadless'\''\]/i \    customLaunchers: {\n      ChromeHeadlessNoSandbox: {\n        base: \'\'ChromeHeadless\'\',\n        flags: [ \'\'--no-sandbox\'\', \'\'--disable-gpu\'\', \'\'--remote-debugging-port=9222\'\' ]\n      }\n    },\n' karma.conf.js && sed -i 's/browsers: \['\''ChromeHeadless'\''\]/browsers: \['\''ChromeHeadlessNoSandbox'\''\]/' karma.conf.js
###ACTION_DELIMITER###
sed -i '/browsers: \[\'ChromeHeadless\'\]/i \    customLaunchers: {\n      ChromeHeadlessNoSandbox: {\n        base: \'ChromeHeadless\',\n        flags: [\'--no-sandbox\', \'--disable-gpu\', \'--remote-debugging-port=9222\']\n      }\n    },\n' karma.conf.js && sed -i 's/browsers: \[\'ChromeHeadless\'\]/browsers: \[\'ChromeHeadlessNoSandbox\'\]/' karma.conf.js
###ACTION_DELIMITER###
sed -i "/browsers: \['ChromeHeadless'\]/i \    customLaunchers: {\n      ChromeHeadlessNoSandbox: {\n        base: 'ChromeHeadless',\n        flags: ['--no-sandbox', '--disable-gpu', '--remote-debugging-port=9222']\n      }\n    },\n" karma.conf.js && sed -i "s/browsers: \['ChromeHeadless'\]/browsers: \['ChromeHeadlessNoSandbox'\]/g" karma.conf.js
###ACTION_DELIMITER###
yarn test
###ACTION_DELIMITER###
echo -e '#!/bin/bash
mvn clean test -Dstyle.color=never -Dkarma.browsers=ChromeHeadlessNoSandbox -Dwatch=false' > /home/comixed/test_commands.sh && chmod +x /home/comixed/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
mvn clean test -Dstyle.color=never -Dkarma.browsers=ChromeHeadlessNoSandbox -Dwatch=false

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
mvn clean test -Dstyle.color=never -Dkarma.browsers=ChromeHeadlessNoSandbox -Dwatch=false

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
mvn clean test -Dstyle.color=never -Dkarma.browsers=ChromeHeadlessNoSandbox -Dwatch=false

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

# Choose an appropriate base image based on the project's requirements - replace openjdk:17-jdk-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM openjdk:17-jdk-slim

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


@Instance.register("comixed", "comixed_2291_to_unknown")
class COMIXED_2291_TO_UNKNOWN(Instance):
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
        passed_tests = set[str]()
        failed_tests = set[str]()
        skipped_tests = set[str]()
        import re
        # Regex pattern to match test module statuses (SUCCESS, FAILURE, SKIPPED)
        pattern = r"\[INFO\]\s+([\w-]+)\s+[\.\s]+\s(SUCCESS|FAILURE|SKIPPED)\b"
        matches = re.findall(pattern, log)
        for test_name, status in matches:
            if status == "SUCCESS":
                passed_tests.add(test_name)
            elif status == "FAILURE":
                failed_tests.add(test_name)
            elif status == "SKIPPED":
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
