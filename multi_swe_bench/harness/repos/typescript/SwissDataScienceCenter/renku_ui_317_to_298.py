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
                """apt-get update && apt-get install -y python2.7 python2.7-dev && npm uninstall node-sass-chokidar && npm install sass && sed -i 's/node-sass-chokidar/sass/g' package.json && npm install --legacy-peer-deps
###ACTION_DELIMITER###

###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian oldstable main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python2.7 python2.7-dev && pip install pytest && echo '#!/bin/bash
pytest-2.7 --no-header -rA --verbose --tb=no -p no:cacheprovider' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo 'deb http://archive.debian.org/debian stretch main' >> /etc/apt/sources.list && apt-get -o Acquire::Check-Valid-Until=false update && apt-get install -y python2.7 python2.7-dev
###ACTION_DELIMITER###
npm config set python python2.7 && npm uninstall node-sass-chokidar && npm install sass && sed -i 's/node-sass-chokidar/sass/g' package.json && npm install --legacy-peer-deps
###ACTION_DELIMITER###
export PYTHON=python2.7 && npm uninstall node-sass-chokidar && npm install sass && sed -i 's/node-sass-chokidar/sass/g' package.json && npm install --legacy-peer-deps
###ACTION_DELIMITER###
export PYTHON=python2.7 && npm uninstall node-sass-chokidar && npm install sass && sed -i 's/node-sass-chokidar/sass/g' package.json && npm install --legacy-peer-deps --force
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && export PYTHON=python2.7 && npm uninstall node-sass-chokidar && npm install sass && sed -i 's/node-sass-chokidar/sass/g' package.json && npm install --legacy-peer-deps
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && export PYTHON=python2.7 && npm uninstall node-sass-chokidar && npm install sass && sed -i 's/node-sass-chokidar/sass/g' package.json && npm install --legacy-peer-deps --force
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && sed -i '/"dependencies": {/a\  "overrides": { "immutable": "^4.3.7" },' package.json && export PYTHON=python2.7 && npm uninstall node-sass-chokidar && npm install sass && sed -i 's/node-sass-chokidar/sass/g' package.json && npm install --legacy-peer-deps
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && export PYTHON=python2.7 && npm uninstall node-sass-chokidar && npm install sass && sed -i 's/node-sass-chokidar/sass/g' package.json && npm install immutable@^4.3.7 --legacy-peer-deps && npm install --legacy-peer-deps
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && sed -i '/"version":/a\  "overrides": { "@nteract/notebook-preview": { "immutable": "^4.3.7" } },' package.json && export PYTHON=python2.7 && npm uninstall node-sass-chokidar && npm install sass && sed -i 's/node-sass-chokidar/sass/g' package.json && npm install --legacy-peer-deps
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && sed -i 's/"immutable": "^3.8.2"/"immutable": "^4.3.7"/' package.json && export PYTHON=python2.7 && npm uninstall node-sass-chokidar && npm install sass && sed -i 's/node-sass-chokidar/sass/g' package.json && npm install --legacy-peer-deps
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && export PYTHON=python2.7 && npm uninstall node-sass-chokidar && npm install sass && sed -i 's/node-sass-chokidar/sass/g' package.json && npm install --legacy-peer-deps --force
###ACTION_DELIMITER###
git checkout package.json && rm -rf node_modules package-lock.json && export PYTHON=python2.7 && npm uninstall node-sass-chokidar && npm install sass && sed -i 's/node-sass-chokidar/sass/g' package.json && npm install --legacy-peer-deps --force
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && export PYTHON=python2.7 && npm uninstall node-sass-chokidar && npm install sass && sed -i 's/node-sass-chokidar/sass/g' package.json && npm install --force
###ACTION_DELIMITER###
git checkout package.json && sed -i 's/"immutable": "^3.8.2"/"immutable": "^4.3.7"/' package.json && rm -rf node_modules package-lock.json && npm cache clean --force && export PYTHON=python2.7 && npm uninstall node-sass-chokidar && npm install sass && sed -i 's/node-sass-chokidar/sass/g' package.json && npm install --legacy-peer-deps
###ACTION_DELIMITER###
npm install -g npm@6 && rm -rf node_modules package-lock.json && export PYTHON=python2.7 && npm uninstall node-sass-chokidar && npm install sass && sed -i 's/node-sass-chokidar/sass/g' package.json && npm install
###ACTION_DELIMITER###
echo '#!/bin/bash
CI=true npm test -- --verbose --watchAll=false' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
CI=true npm test -- --verbose --watchAll=false --runInBand --maxWorkers=1' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
CI=true npm test -- --verbose --watchAll=false --runInBand' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
CI=true npm test -- --verbose --watchAll=false --runInBand

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
CI=true npm test -- --verbose --watchAll=false --runInBand

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
CI=true npm test -- --verbose --watchAll=false --runInBand

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
RUN git clone https://github.com/SwissDataScienceCenter/renku-ui.git /home/renku-ui

WORKDIR /home/renku-ui
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("SwissDataScienceCenter", "renku_ui_317_to_298")
class RENKU_UI_317_TO_298(Instance):
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
        passed_tests: set[str] = set()
        failed_tests: set[str] = set()
        skipped_tests: set[str] = set()
        import re
        import json
        # Pattern to match passed tests (✓ followed by test name, optional duration)
        passed_pattern = re.compile(r'^\s*✓\s*(.*?)(?:\s*\(\d+ms\))?$', re.MULTILINE)
        for match in passed_pattern.findall(log):
            test_name = match.strip()
            passed_tests.add(test_name)
        # Pattern to match failed tests (✕ followed by test name, optional duration)
        failed_pattern = re.compile(r'^\s*✕\s*(.*?)(?:\s*\(\d+ms\))?$', re.MULTILINE)
        for match in failed_pattern.findall(log):
            test_name = match.strip()
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
