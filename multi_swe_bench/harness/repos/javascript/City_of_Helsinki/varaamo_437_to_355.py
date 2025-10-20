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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y libfontconfig1 libfreetype6 libssl-dev libpng-dev libicu-dev
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
###ACTION_DELIMITER###
nvm install 6
###ACTION_DELIMITER###
sed -i 's/git:\/\/github.com\/City-of-Helsinki\/passport-helsinki.git/https:\/\/github.com\/City-of-Helsinki\/passport-helsinki.git/' package.json && sed -i 's/git:\/\/github.com\/tomatau\/redux-devtools.git/https:\/\/github.com\/tomatau\/redux-devtools.git/' package.json
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
curl -L https://github.com/Medium/phantomjs/releases/download/v2.1.1/phantomjs-2.1.1-linux-x86_64.tar.bz2 -o phantomjs.tar.bz2 && tar xjf phantomjs.tar.bz2 && cp phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/ && chmod +x /usr/local/bin/phantomjs
###ACTION_DELIMITER###
apt-get install -y bzip2
###ACTION_DELIMITER###
curl -L https://github.com/Medium/phantomjs/releases/download/v2.1.1/phantomjs-2.1.1-linux-x86_64.tar.bz2 -o phantomjs.tar.bz2 && tar xjf phantomjs.tar.bz2 && cp phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/ && chmod +x /usr/local/bin/phantomjs
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
curl -O http://security.ubuntu.com/ubuntu/pool/main/i/icu/libicu52_52.1-3ubuntu0.8_amd64.deb && dpkg -i libicu52_52.1-3ubuntu0.8_amd64.deb
###ACTION_DELIMITER###
apt-get install -y multiarch-support
###ACTION_DELIMITER###
ldd /usr/local/bin/phantomjs | grep 'not found'
###ACTION_DELIMITER###
export OPENSSL_CONF=/dev/null
###ACTION_DELIMITER###
echo 'npm test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo './node_modules/karma/bin/karma start config/karma.conf.js --single-run --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
./node_modules/karma/bin/karma start config/karma.conf.js --single-run --verbose

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
./node_modules/karma/bin/karma start config/karma.conf.js --single-run --verbose

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
./node_modules/karma/bin/karma start config/karma.conf.js --single-run --verbose

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
RUN git clone https://github.com/City-of-Helsinki/varaamo.git /home/varaamo

WORKDIR /home/varaamo
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("City-of-Helsinki", "varaamo_437_to_355")
class VARAAMO_437_TO_355(Instance):
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
        # Remove ANSI escape codes
        log_clean = re.sub(r'\x1B\[[0-9;]*[mK]', '', log)
        status_re = re.compile(r'^(✔|✖|SKIPPED)\s*(.*)$')
        lines = log_clean.split('\n')
        current_groups = []
        indent_levels = []
        for line in lines:
            leading_spaces = len(line) - len(line.lstrip(' '))
            content = line.lstrip(' ')
            if leading_spaces > 0:
                match = status_re.match(content)
            else:
                match = None
            if match:
                status, test_case = match.groups()
                full_test = ' '.join(current_groups + [test_case.strip()])
                if status == '✔':
                    passed_tests.add(full_test)
                elif status == '✖':
                    failed_tests.add(full_test)
                elif status == 'SKIPPED':
                    skipped_tests.add(full_test)
            else:
                current_level = leading_spaces // 2
                while indent_levels and current_level <= indent_levels[-1]:
                    indent_levels.pop()
                    current_groups.pop()
                # Filter out non-test lines (log messages, etc.)
                if leading_spaces > 0 and content and not (content.startswith(('INFO', 'webpack', 'Time:', 'Child', 'START:', 'Connected'))):
                    current_groups.append(content)
                    indent_levels.append(current_level)
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
