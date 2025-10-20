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
        return "node:20-bullseye"
    
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
                """vue-cli-service test:unit --help
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2.7 python2.7-dev build-essential
###ACTION_DELIMITER###
npm install --legacy-peer-deps
###ACTION_DELIMITER###
export PYTHON=python2.7 && npm install --legacy-peer-deps
###ACTION_DELIMITER###
npm uninstall node-sass && npm install sass --legacy-peer-deps
###ACTION_DELIMITER###
npm run test:unit -- --verbose
###ACTION_DELIMITER###
npm run test:unit
###ACTION_DELIMITER###
NODE_OPTIONS=--openssl-legacy-provider npm run test:unit
###ACTION_DELIMITER###
NODE_OPTIONS=--openssl-legacy-provider npm run test:unit -- --verbose
###ACTION_DELIMITER###
echo -e '#!/bin/bash
NODE_OPTIONS=--openssl-legacy-provider npm run test:unit
NODE_OPTIONS=--openssl-legacy-provider npm run test:e2e' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y xvfb
###ACTION_DELIMITER###
echo -e '#!/bin/bash
NODE_OPTIONS=--openssl-legacy-provider npm run test:unit
xvfb-run NODE_OPTIONS=--openssl-legacy-provider npm run test:e2e' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
NODE_OPTIONS=--openssl-legacy-provider npm run test:unit
NODE_OPTIONS=--openssl-legacy-provider xvfb-run npm run test:e2e' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 libxtst6
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y ffmpeg
###ACTION_DELIMITER###
apt-get install -y apt-file && apt-file update && apt-file search libffmpeg.so
###ACTION_DELIMITER###
apt-get install -y qmmp
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
dpkg -L qmmp | grep libffmpeg.so && ln -s $(dpkg -L qmmp | grep libffmpeg.so) /usr/lib/x86_64-linux-gnu/libffmpeg.so
###ACTION_DELIMITER###
ldconfig && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libicu67 && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/NODE_OPTIONS=--openssl-legacy-provider xvfb-run npm run test:e2e/NODE_OPTIONS=--openssl-legacy-provider ICU_DATA=/usr/lib/x86_64-linux-gnu/ xvfb-run npm run test:e2e/' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|NODE_OPTIONS=--openssl-legacy-provider xvfb-run npm run test:e2e|NODE_OPTIONS=--openssl-legacy-provider ICU_DATA=/usr/lib/x86_64-linux-gnu xvfb-run npm run test:e2e|' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y icu-devtools && find / -name 'icudt*.dat' && sed -i 's|xvfb-run npm run test:e2e|ICU_DATA=$(find / -name 'icudt*.dat' | head -n1 | xargs dirname) xvfb-run npm run test:e2e|' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
ICU_DIR=$(find / -name 'icudt*.dat' 2>/dev/null | head -n1 | xargs dirname) && sed -i 's|xvfb-run npm run test:e2e|ICU_DATA='$ICU_DIR' xvfb-run npm run test:e2e|' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|xvfb-run npm run test:e2e|ICU_DATA=/usr/lib/x86_64-linux-gnu/icu/67.1/ xvfb-run npm run test:e2e|' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|xvfb-run npm run test:e2e|ICU_DATA=/usr/lib/x86_64-linux-gnu/ xvfb-run npm run test:e2e|' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
ICU_DATA_DIR=$(find / -name 'icudt*.dat' 2>/dev/null | head -n1 | xargs dirname) && sed -i 's|xvfb-run npm run test:e2e|ICU_DATA='$ICU_DATA_DIR' xvfb-run npm run test:e2e|' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|xvfb-run npm run test:e2e|ICU_DATA=/usr/lib/x86_64-linux-gnu/icu/67.1/ xvfb-run npm run test:e2e|' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
ICU_DATA_DIR=$(dpkg -L libicu67 | grep 'icudt.*\.dat' | xargs dirname) && sed -i 's|xvfb-run npm run test:e2e|ICU_DATA='$ICU_DATA_DIR' xvfb-run npm run test:e2e|' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|xvfb-run npm run test:e2e|ICU_DATA=/usr/lib/x86_64-linux-gnu/ xvfb-run npm run test:e2e|' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
ICU_DIR=$(dpkg -L libicu67 | grep 'icudt' | head -n1 | xargs dirname) && sed -i 's|xvfb-run npm run test:e2e|ICU_DATA='$ICU_DIR' xvfb-run npm run test:e2e|' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|NODE_OPTIONS=--openssl-legacy-provider xvfb-run|NODE_OPTIONS=--openssl-legacy-provider ICU_DATA=/usr/lib/x86_64-linux-gnu/ xvfb-run|' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|xvfb-run|ICU_DATA=/usr/lib/x86_64-linux-gnu/ xvfb-run|' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
dpkg -L libicu67 | grep 'icudt' && sed -i 's|NODE_OPTIONS=--openssl-legacy-provider xvfb-run|NODE_OPTIONS=--openssl-legacy-provider ICU_DATA=/usr/lib/x86_64-linux-gnu/ xvfb-run|' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
npm uninstall cypress && npm install cypress@3.4.1 --legacy-peer-deps && sed -i 's|xvfb-run|ICU_DATA=/usr/lib/x86_64-linux-gnu/ xvfb-run|' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
npm install cypress@3.4.1 --legacy-peer-deps && sed -i 's|xvfb-run|ICU_DATA=/usr/lib/x86_64-linux-gnu/ xvfb-run|' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
export ICU_DATA=/usr/lib/x86_64-linux-gnu/ && ls /usr/lib/x86_64-linux-gnu/icudt* && bash test_commands.sh
###ACTION_DELIMITER###
ICU_DATA=$(dpkg -L libicu67 | grep 'icudt.*\.dat' | head -n1 | xargs dirname) && export ICU_DATA && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install --reinstall libicu67 && find / -name 'icudt*.dat' 2>/dev/null && ICU_DATA=$(find / -name 'icudt*.dat' 2>/dev/null | head -n1 | xargs dirname) && export ICU_DATA && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
NODE_OPTIONS=--openssl-legacy-provider npm run test:unit
ICU_DATA=/usr/lib/x86_64-linux-gnu/ NODE_OPTIONS=--openssl-legacy-provider xvfb-run npm run test:e2e -- --config baseUrl=http://localhost:8080 --headless' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
npm uninstall cypress && npm install cypress@10.0.0 --legacy-peer-deps && echo -e '#!/bin/bash
NODE_OPTIONS=--openssl-legacy-provider npm run test:unit
NODE_OPTIONS=--openssl-legacy-provider xvfb-run npx cypress run --config baseUrl=http://localhost:8080' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
npm install cypress@10.0.0 --legacy-peer-deps && echo -e '#!/bin/bash
NODE_OPTIONS=--openssl-legacy-provider npm run test:unit
ICU_DATA=/usr/lib/x86_64-linux-gnu/ NODE_OPTIONS=--openssl-legacy-provider xvfb-run npx cypress run --config baseUrl=http://localhost:8080' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
npx cypress open --migrate-config && echo -e '#!/bin/bash
NODE_OPTIONS=--openssl-legacy-provider npm run test:unit
NODE_OPTIONS=--openssl-legacy-provider xvfb-run npx cypress run --config baseUrl=http://localhost:8080' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'const { defineConfig } = require("cypress");
module.exports = defineConfig({ e2e: { baseUrl: "http://localhost:8080" } });' > cypress.config.js && echo -e '#!/bin/bash
NODE_OPTIONS=--openssl-legacy-provider npm run test:unit
NODE_OPTIONS=--openssl-legacy-provider xvfb-run npx cypress run' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
rm -f cypress.json && bash test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
NODE_OPTIONS=--openssl-legacy-provider npm run test:unit
NODE_OPTIONS=--openssl-legacy-provider xvfb-run npx cypress run

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
NODE_OPTIONS=--openssl-legacy-provider npm run test:unit
NODE_OPTIONS=--openssl-legacy-provider xvfb-run npx cypress run

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
NODE_OPTIONS=--openssl-legacy-provider npm run test:unit
NODE_OPTIONS=--openssl-legacy-provider xvfb-run npx cypress run

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
FROM node:20-bullseye

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
RUN git clone https://github.com/cylc/cylc-ui.git /home/cylc-ui

WORKDIR /home/cylc-ui
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("cylc", "cylc_ui_249_to_72")
class CYLC_UI_249_TO_72(Instance):
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
        # Parse passed tests using regex
        passed_matches = re.findall(r'^\s*✓\s+(.*)$', log, re.MULTILINE)
        passed_tests.update(passed_matches)
        # Parse failed tests using regex
        failed_matches = re.findall(r'^\s{6,}\d+\)\s+(.*)$', log, re.MULTILINE)
        failed_tests.update(failed_matches)
        # Parse skipped tests (adjust pattern based on log format)
        skipped_matches = re.findall(r'^\s*-\s+(.*?)\s+\(skipped\)$', log, re.MULTILINE)
        skipped_tests.update(skipped_matches)
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
