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
        return "node:lts-alpine"
    
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
npm install
###ACTION_DELIMITER###
apk update && apk add --no-cache python3 make g++ libc6-compat
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
apk add vips-dev
###ACTION_DELIMITER###
export CXXFLAGS="-std=c++17" && npm install
###ACTION_DELIMITER###
export CXXFLAGS="-std=c++17 -D_FILE_OFFSET_BITS=64" && npm install
###ACTION_DELIMITER###
cd src/frontend && npm install sharp@latest && cd ../../ && npm install
###ACTION_DELIMITER###
cd src/frontend && npm install sharp@latest && npm config set sharp_binary_host 'https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/' && npm config set sharp_libvips_binary_host 'https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/' && cd ../../ && npm install
###ACTION_DELIMITER###
npm config set sharp_binary_host 'https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/' && npm config set sharp_libvips_binary_host 'https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/' && npm install sharp@latest && cd ../../ && npm install
###ACTION_DELIMITER###
SHARP_BINARY_HOST=https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/ SHARP_LIBVIPS_BINARY_HOST=https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/ npm install sharp@latest && cd ../../ && npm install
###ACTION_DELIMITER###
echo '{"overrides": {"sharp": "latest"}}' >> package.json && SHARP_IGNORE_GLOBAL_LIBVIPS=1 SHARP_BINARY_SITE=https://github.com/lovell/sharp/releases/download/ npm install sharp@latest && cd ../../ && npm install
###ACTION_DELIMITER###
jq '.overrides = {"sharp": "latest"}' package.json > temp.json && mv temp.json package.json && SHARP_IGNORE_GLOBAL_LIBVIPS=1 SHARP_BINARY_SITE=https://github.com/lovell/sharp/releases/download/ npm install sharp@latest && cd ../../ && npm install
###ACTION_DELIMITER###
apk add --no-cache jq && jq '.overrides = {"sharp": "latest"}' package.json > temp.json && mv temp.json package.json && SHARP_IGNORE_GLOBAL_LIBVIPS=1 SHARP_BINARY_HOST="https://github.com/lovell/sharp/releases/download/" npm install sharp@latest && cd ../../ && npm install
###ACTION_DELIMITER###
git checkout package.json && jq '.overrides = {"sharp": "latest"}' package.json > temp.json && mv temp.json package.json && SHARP_IGNORE_GLOBAL_LIBVIPS=1 SHARP_BINARY_HOST="https://github.com/lovell/sharp/releases/download/" npm install sharp@latest && cd ../../ && npm install
###ACTION_DELIMITER###
npm config set sharp_binary_host 'https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/' && npm config set sharp_libvips_binary_host 'https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/' && npm install sharp@$(node -p "require('./package.json').dependencies.sharp") && cd ../../ && npm install
###ACTION_DELIMITER###
apk add --no-cache vips && SHARP_BINARY_HOST='https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/' SHARP_LIBVIPS_BINARY_HOST='https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/' npm install sharp@$(node -p "require('./package.json').dependencies.sharp") && cd ../../ && npm install
###ACTION_DELIMITER###
apk add --no-cache vips && SHARP_BINARY_HOST='https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/' SHARP_LIBVIPS_BINARY_HOST='https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/' npm install sharp@latest && cd ../../ && npm install
###ACTION_DELIMITER###
jq 'del(.overrides)' package.json > temp.json && mv temp.json package.json && SHARP_BINARY_SITE='https://github.com/lovell/sharp/releases/download/' SHARP_LIBVIPS_BINARY_SITE='https://github.com/lovell/sharp-libvips/releases/download/' npm install sharp@$(node -p "require('./package.json').dependencies.sharp || require('./package.json').devDependencies.sharp") && cd ../../ && npm install
###ACTION_DELIMITER###
git checkout package.json && SHARP_BINARY_SITE='https://github.com/lovell/sharp/releases/download/' SHARP_LIBVIPS_BINARY_SITE='https://github.com/lovell/sharp-libvips/releases/download/' npm install sharp && cd ../../ && npm install
###ACTION_DELIMITER###
export CXXFLAGS="-std=c++17 -D_FILE_OFFSET_BITS=64" && export CPPFLAGS="-D_FILE_OFFSET_BITS=64" && npm install sharp && cd ../../ && npm install
###ACTION_DELIMITER###
rm -rf node_modules package-lock.json && apk add --no-cache vips && SHARP_BINARY_SITE="https://github.com/lovell/sharp/releases/download/" SHARP_LIBVIPS_BINARY_SITE="https://github.com/lovell/sharp-libvips/releases/download/" npm install sharp@latest && cd ../../ && npm install
###ACTION_DELIMITER###
apk add --no-cache vips-dev python3 make g++ && rm -rf node_modules package-lock.json && SHARP_IGNORE_GLOBAL_LIBVIPS=1 SHARP_BINARY_SITE='https://github.com/lovell/sharp/releases/download/' SHARP_LIBVIPS_BINARY_SITE='https://github.com/lovell/sharp-libvips/releases/download/' npm install && cd ../../ && npm install
###ACTION_DELIMITER###
export SHARP_BINARY_HOST='https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/' && export SHARP_LIBVIPS_BINARY_HOST='https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/' && rm -rf node_modules package-lock.json && npm cache clean --force && npm install sharp@0.32.6 && cd ../../ && npm install
###ACTION_DELIMITER###
export SHARP_BINARY_HOST='https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/' && export SHARP_LIBVIPS_BINARY_HOST='https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/' && rm -rf node_modules package-lock.json && npm cache clean --force && npm install sharp@0.33.5 && cd ../../ && npm install
###ACTION_DELIMITER###
export npm_config_cxxflags="-std=c++17 -D_FILE_OFFSET_BITS=64" && export npm_config_cppflags="-D_FILE_OFFSET_BITS=64" && apk add --no-cache vips-dev && rm -rf node_modules package-lock.json && SHARP_BINARY_HOST="https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/" SHARP_LIBVIPS_BINARY_HOST="https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/" npm install sharp@latest && cd ../../ && npm install
###ACTION_DELIMITER###
echo '{"overrides": {"sharp": "0.33.5"}}' >> package.json && export CXXFLAGS="-std=c++17 -D_FILE_OFFSET_BITS=64" && export CPPFLAGS="-D_FILE_OFFSET_BITS=64" && SHARP_BINARY_HOST="https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/" SHARP_LIBVIPS_BINARY_HOST="https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/" npm install && cd ../../ && npm install
###ACTION_DELIMITER###
jq '.overrides = {"sharp": "0.33.5"}' package.json > temp.json && mv temp.json package.json && export SHARP_BINARY_HOST="https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/" && export SHARP_LIBVIPS_BINARY_HOST="https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/" && rm -rf node_modules package-lock.json && npm install && cd ../../ && npm install
###ACTION_DELIMITER###
jq '.overrides = {"sharp": "0.33.5"}' package.json > temp.json && mv temp.json package.json && export SHARP_BINARY_HOST="https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/" && export SHARP_LIBVIPS_BINARY_HOST="https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/" && rm -rf node_modules package-lock.json && npm install && cd ../../ && npm install
###ACTION_DELIMITER###
jq -s '.[0] * .[1]' package.json <(echo '{"overrides": {"sharp": "0.33.5"}}') > temp.json && mv temp.json package.json && export SHARP_BINARY_HOST="https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/" && export SHARP_LIBVIPS_BINARY_HOST="https://github.com/lovell/sharp-libvips/releases/download/v8.15.2/" && rm -rf node_modules package-lock.json && npm install && cd ../../ && npm install
###ACTION_DELIMITER###
echo 'npm test -- --verbose' > /home/telescope/test_commands.sh && chmod +x /home/telescope/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npm test -- --verbose

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
npm test -- --verbose

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
npm test -- --verbose

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
FROM node:lts-alpine

## Set noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Install basic requirements
# For example: RUN apt-get update && apt-get install -y git
# For example: RUN yum install -y git
# For example: RUN apk add --no-cache git
RUN apk add --no-cache git

# Ensure bash is available
RUN if [ ! -f /bin/bash ]; then         if command -v apk >/dev/null 2>&1; then             apk add --no-cache bash;         elif command -v apt-get >/dev/null 2>&1; then             apt-get update && apt-get install -y bash;         elif command -v yum >/dev/null 2>&1; then             yum install -y bash;         else             exit 1;         fi     fi

WORKDIR /home/
COPY fix.patch /home/
COPY test.patch /home/
RUN git clone https://github.com/Seneca-CDOT/telescope.git /home/telescope

WORKDIR /home/telescope
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Seneca-CDOT", "telescope_905_to_345")
class TELESCOPE_905_TO_345(Instance):
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
        passed_tests = set[str]()
        failed_tests = set[str]()
        skipped_tests = set[str]()
        import re
        # Parse test results using regex
        pattern = re.compile(r'^(PASS|FAIL|SKIPPED)\s+([^\s]+)$', re.MULTILINE)
        for match in pattern.finditer(log):
            status, test_name = match.groups()
            if status == 'PASS':
                passed_tests.add(test_name)
            elif status == 'FAIL':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
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
