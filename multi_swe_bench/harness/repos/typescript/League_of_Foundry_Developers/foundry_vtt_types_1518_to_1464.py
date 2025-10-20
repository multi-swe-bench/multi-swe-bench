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
        return "ubuntu:22.04"
    
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
                """cat package.json
###ACTION_DELIMITER###
apt-get update && apt-get install -y nodejs npm
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
echo 'npm test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cat tsd.json
###ACTION_DELIMITER###
ls -la
###ACTION_DELIMITER###
ls -la test-d
###ACTION_DELIMITER###
echo './node_modules/.bin/tsd --verbose test-d/**/*.test-d.ts' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo '{ "compilerOptions": { "module": "commonjs", "target": "es2017" }, "files": ["index.d.ts"], "testFiles": ["test-d/**/*.test-d.ts"] }' > tsd.json
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cat index.d.ts
###ACTION_DELIMITER###
cat tsconfig.json
###ACTION_DELIMITER###
echo '{ "compilerOptions": { "exactOptionalPropertyTypes": true, "importsNotUsedAsValues": "error", "lib": ["DOM", "ES2020"], "moduleResolution": "Node", "noEmit": true, "strict": true, "target": "ES2020" }, "files": ["index.d.ts"], "testFiles": ["test-d/**/*.test-d.ts"] }' > tsd.json
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls -l index.d.ts
###ACTION_DELIMITER###
./node_modules/.bin/tsd --debug --verbose test-d/**/*.test-d.ts
###ACTION_DELIMITER###
echo '{ "files": ["index.d.ts"], "testFiles": ["test-d/**/*.test-d.ts"] }' > tsd.json
###ACTION_DELIMITER###
echo './node_modules/.bin/tsd --files index.d.ts --testFiles test-d/**/*.test-d.ts --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo './node_modules/.bin/tsd --files /home/foundry-vtt-types/index.d.ts --testFiles test-d/**/*.test-d.ts --verbose' > test_commands.sh
###ACTION_DELIMITER###
tsc --noEmit index.d.ts
###ACTION_DELIMITER###
./node_modules/.bin/tsc --noEmit index.d.ts
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
node -v
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && apt-get install -y nodejs
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && apt-get install -y nodejs
###ACTION_DELIMITER###
apt-get remove -y libnode-dev
###ACTION_DELIMITER###
curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && apt-get install -y nodejs
###ACTION_DELIMITER###
apt-get remove -y libnode72
###ACTION_DELIMITER###
apt-get purge -y nodejs libnode72 libnode-dev && apt-get autoremove -y && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && apt-get install -y nodejs
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo './node_modules/.bin/tsd --debug --files /home/foundry-vtt-types/index.d.ts --testFiles test-d/**/*.test-d.ts --verbose' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
npm install tsd@0.18.0 && bash test_commands.sh
###ACTION_DELIMITER###
echo 'npm test -- --verbose' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo '{ "compilerOptions": { "skipLibCheck": true }, "files": ["index.d.ts"], "testFiles": ["test-d/**/*.test-d.ts"] }' > tsd.json && npm test -- --verbose
###ACTION_DELIMITER###
echo 'tsd --project tsconfig.json --clear --verbose' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo './node_modules/.bin/tsd --project tsconfig.json --clear --verbose' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
./node_modules/.bin/tsd --verbose --debug
###ACTION_DELIMITER###
find test-d -name '*.test-d.ts'
###ACTION_DELIMITER###
echo '{ "compilerOptions": { "skipLibCheck": true }, "files": ["index.d.ts"], "testFiles": ["test-d/**/*.test-d.ts"] }' > tsd.json && echo './node_modules/.bin/tsd --verbose' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
npm install && ./node_modules/.bin/tsd --verbose --debug
###ACTION_DELIMITER###
echo '{ "compilerOptions": { "skipLibCheck": true, "exactOptionalPropertyTypes": true, "importsNotUsedAsValues": "error", "lib": ["DOM", "ES2020"], "moduleResolution": "Node", "noEmit": true, "strict": true, "target": "ES2020" }, "files": ["index.d.ts"], "testFiles": ["test-d/**/*.test-d.ts"] }' > tsd.json && ./node_modules/.bin/tsd --project tsconfig.json --verbose
###ACTION_DELIMITER###
./node_modules/.bin/tsd --files index.d.ts --testFiles test-d/foundry/foundry.js/canvasDocumentMixin.test-d.ts --verbose --debug
###ACTION_DELIMITER###
./node_modules/.bin/tsd --version && ./node_modules/.bin/tsd --show-config && echo 'import "../index.d.ts"; type Test = string; const t: Test = "test";' > test-d/minimal.test-d.ts && ./node_modules/.bin/tsd --files index.d.ts --testFiles test-d/minimal.test-d.ts --verbose --debug
###ACTION_DELIMITER###
./node_modules/.bin/tsd --help
###ACTION_DELIMITER###
echo 'npm test && echo "All tests passed successfully"' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npm test && echo "All tests passed successfully"

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
npm test && echo "All tests passed successfully"

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
npm test && echo "All tests passed successfully"

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:22.04 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:22.04

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
RUN git clone https://github.com/League-of-Foundry-Developers/foundry-vtt-types.git /home/foundry-vtt-types

WORKDIR /home/foundry-vtt-types
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("League-of-Foundry-Developers", "foundry_vtt_types_1518_to_1464")
class FOUNDRY_VTT_TYPES_1518_TO_1464(Instance):
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
        # Extract test suite name from log header (e.g., 'foundry-vtt-types' from package line)
        suite_pattern = re.compile(r'@[^/]+/([^@]+)@')  # Matches package name in '@org/name@version'
        suite_match = suite_pattern.search(log)
        test_name = suite_match.group(1) if suite_match else "unknown_test_suite"
        # Determine test status based on log content
        if "All tests passed successfully" in log:
            passed_tests.add(test_name)
        elif "errors" in log or "✖" in log:
            failed_tests.add(test_name)
        # Add skipped logic if needed (no skipped examples in provided logs)
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
