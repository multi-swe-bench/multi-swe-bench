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
        return "node:20-bookworm"
    
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
                """yarn install --verbose
###ACTION_DELIMITER###
YARN_LOG_LEVEL=debug yarn install
###ACTION_DELIMITER###
yarn --version
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
node -v
###ACTION_DELIMITER###
yarn set version classic && yarn install
###ACTION_DELIMITER###
ls packages
###ACTION_DELIMITER###
sed -i 's/"ts-ast-serializer": "^1.0.1"/"ts-ast-serializer": "github:HoudiniGraphql/ts-ast-serializer#v1.0.1"/' package.json && yarn install
###ACTION_DELIMITER###
sed -i 's|"ts-ast-serializer": "^1.0.1"|"ts-ast-serializer": "github:HoudiniGraphql/ts-ast-serializer#v1.0.1"|' package.json && yarn install
###ACTION_DELIMITER###
sed -i 's|"ts-ast-serializer": "github:HoudiniGraphql/ts-ast-serializer#v1.0.1"|"ts-ast-serializer": "https://github.com/HoudiniGraphql/ts-ast-serializer.git#v1.0.1"|' package.json && yarn install
###ACTION_DELIMITER###
sed -i 's|"ts-ast-serializer": "https://github.com/HoudiniGraphql/ts-ast-serializer.git#v1.0.1"|"ts-ast-serializer": "1.0.2"|' package.json && yarn install
###ACTION_DELIMITER###
git clone https://github.com/HoudiniGraphql/ts-ast-serializer.git packages/ts-ast-serializer && sed -i 's|"ts-ast-serializer": "1.0.2"|"ts-ast-serializer": "file:./packages/ts-ast-serializer"|' package.json && yarn install
###ACTION_DELIMITER###
git submodule init && git submodule update && sed -i 's|"ts-ast-serializer": "1.0.2"|"ts-ast-serializer": "file:./packages/ts-ast-serializer"|' package.json && yarn install
###ACTION_DELIMITER###
git clone --depth 1 https://github.com/HoudiniGraphql/ts-ast-serializer.git packages/ts-ast-serializer && sed -i 's|"ts-ast-serializer": "1.0.2"|"ts-ast-serializer": "file:./packages/ts-ast-serializer"|' package.json && yarn install
###ACTION_DELIMITER###
curl -L https://github.com/HoudiniGraphql/ts-ast-serializer/archive/refs/tags/v1.0.1.zip -o ts-ast-serializer.zip && unzip -q ts-ast-serializer.zip -d packages && mv packages/ts-ast-serializer-1.0.1 packages/ts-ast-serializer && rm ts-ast-serializer.zip && sed -i 's|"ts-ast-serializer": "^1.0.1"|"ts-ast-serializer": "file:./packages/ts-ast-serializer"|' package.json && yarn install
###ACTION_DELIMITER###
curl -L https://github.com/HoudiniGraphql/ts-ast-serializer/archive/main.zip -o ts-ast-serializer.zip && unzip -q ts-ast-serializer.zip -d packages && mv packages/ts-ast-serializer-main packages/ts-ast-serializer && rm ts-ast-serializer.zip && sed -i 's|"ts-ast-serializer": "1.0.2"|"ts-ast-serializer": "file:./packages/ts-ast-serializer"|' package.json && yarn install
###ACTION_DELIMITER###
npx lerna bootstrap --force-local && yarn install
###ACTION_DELIMITER###
sed -i '/"ts-ast-serializer": "^1.0.1"/d' package.json && yarn install
###ACTION_DELIMITER###
sed -i '/"ts-ast-serializer":/d' package.json && yarn install
###ACTION_DELIMITER###
ls node_modules/.bin/jest
###ACTION_DELIMITER###
echo 'node --experimental-vm-modules node_modules/.bin/jest --verbose' > /home/houdini/test_commands.sh
###ACTION_DELIMITER###
bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
ls -la | grep jest.config
###ACTION_DELIMITER###
sed -i '/snapshotSerializers: \[.*ts-ast-serializer.*\],/d' jest.config.js && sed -i '2i\  rootDir: __dirname,' jest.config.js
###ACTION_DELIMITER###
bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
mv jest.config.js jest.config.cjs && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/export default {/module.exports = {/' jest.config.cjs && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
yarn install && yarn workspaces info
###ACTION_DELIMITER###
yarn workspaces run build
###ACTION_DELIMITER###
sed -i 's/module.exports = {/module.exports = { moduleNameMapper: { "^houdini-common$": "<rootDir>\/packages\/houdini-common\/src" },/' jest.config.cjs && yarn install && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
yarn workspace houdini-common run build && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
sed -i '/"resolutions": {/a\  "tslib": "2.3.1",' package.json && yarn install && yarn workspace houdini-common run build && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/"tslib": "2.3.1"/"tslib": "1.14.1"/' package.json && yarn install && yarn workspace houdini-common run build && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
yarn cache clean && sed -i 's/"tslib": ".*"/"tslib": "1.14.1"/' package.json && yarn install && yarn workspace houdini-common run build && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
rm -rf node_modules yarn.lock && sed -i 's/"resolutions": {/"resolutions": { "tslib": "1.14.1", "rollup-plugin-typescript2": "0.29.0",/' package.json && yarn install && yarn workspace houdini-common run build && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
rm -rf node_modules yarn.lock && sed -i 's/"resolutions": {/"resolutions": { "tslib": "1.14.1", "rollup-plugin-typescript2": "0.29.0",/' package.json && yarn install && yarn workspace houdini-common run build && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
rm -rf node_modules yarn.lock && sed -i 's/"resolutions": {/"resolutions": { "tslib": "1.14.1", "rollup-plugin-typescript2": "0.31.0",/' package.json && yarn install && yarn workspace houdini-common run build && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
rm -rf node_modules yarn.lock && sed -i 's/"resolutions": {/"resolutions": { "tslib": "1.14.1",/' package.json && sed -i 's/rollup-plugin-typescript2/@rollup\/plugin-typescript/' packages/houdini-common/rollup.config.js && yarn add -D @rollup/plugin-typescript && yarn install && yarn workspace houdini-common run build && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
rm -rf node_modules yarn.lock && sed -i 's/"resolutions": {/"resolutions": { "tslib": "1.14.1",/' package.json && yarn workspace houdini-common add -D @rollup/plugin-typescript && sed -i 's/rollup-plugin-typescript2/@rollup\/plugin-typescript/' packages/houdini-common/rollup.config.js && yarn install && yarn workspace houdini-common run build && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
sed -i '/"resolutions": {/a\  "graphql": "15.5.0",' package.json && rm -rf node_modules yarn.lock && yarn install && yarn workspace houdini-common run build && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
yarn workspace houdini run build && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
sed -i '/"resolutions": {/a\  "typescript": "4.2.4", "tslib": "2.3.1",' package.json && rm -rf node_modules yarn.lock && yarn install && yarn workspace houdini-common run build && yarn workspace houdini run build && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/"compilerOptions": {/"compilerOptions": { "skipLibCheck": true,/' packages/houdini-common/tsconfig.json && sed -i 's/"compilerOptions": {/"compilerOptions": { "skipLibCheck": true,/' packages/houdini/tsconfig.json && yarn workspace houdini-common run build && yarn workspace houdini run build && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
sed -i '/"resolutions": {/a\  "typescript": "4.3.5", "tslib": "2.3.1",' package.json && sed -i 's/"compilerOptions": {/"compilerOptions": { "skipLibCheck": true,/' packages/houdini-common/tsconfig.json && sed -i 's/"compilerOptions": {/"compilerOptions": { "skipLibCheck": true,/' packages/houdini/tsconfig.json && rm -rf node_modules yarn.lock && yarn install && yarn workspace houdini-common run build && yarn workspace houdini run build && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/"compilerOptions": {/"compilerOptions": { "skipLibCheck": true,/' packages/houdini/tsconfig.runtime.cjs.json && sed -i 's/"compilerOptions": {/"compilerOptions": { "skipLibCheck": true,/' packages/houdini/tsconfig.runtime.esm.json && yarn workspace houdini run build && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/"compilerOptions": {/"compilerOptions": { "skipLibCheck": true,/' packages/houdini/tsconfig.runtime.cjs.json && sed -i 's/"compilerOptions": {/"compilerOptions": { "skipLibCheck": true,/' packages/houdini/tsconfig.runtime.esm.json && yarn workspace houdini run build && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/"compilerOptions": {/"compilerOptions": { "skipLibCheck": true,/' packages/houdini/tsconfig.json && yarn workspace houdini add -D @types/babel__traverse@7.18.0 && rm -rf node_modules yarn.lock && yarn install && yarn workspace houdini run build && bash /home/houdini/test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
node --experimental-vm-modules node_modules/.bin/jest --verbose

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
node --experimental-vm-modules node_modules/.bin/jest --verbose

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
node --experimental-vm-modules node_modules/.bin/jest --verbose

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
FROM node:20-bookworm

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
RUN git clone https://github.com/HoudiniGraphql/houdini.git /home/houdini

WORKDIR /home/houdini
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("HoudiniGraphql", "houdini_249_to_119")
class HOUDINI_249_TO_119(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        import json
            # Extract passed tests using regex
        passed_pattern = r'^PASS (.*?\.test\.ts)'
        passed_tests = set(re.findall(passed_pattern, log, re.MULTILINE))
        # Extract failed tests using regex
        failed_pattern = r'^FAIL (.*?\.test\.ts)'
        failed_tests = set(re.findall(failed_pattern, log, re.MULTILINE))
        # Skipped tests: no explicit pattern found in logs, leaving as empty set
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
