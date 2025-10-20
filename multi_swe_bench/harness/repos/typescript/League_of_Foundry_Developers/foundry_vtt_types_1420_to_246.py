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
npm test -- --verbose
###ACTION_DELIMITER###
ls -la
###ACTION_DELIMITER###
ls test-d
###ACTION_DELIMITER###
npm test -- --verbose
###ACTION_DELIMITER###
npx tsd --help
###ACTION_DELIMITER###
npx tsd test-d
###ACTION_DELIMITER###
npx tsd --project test-d/tsconfig.json
###ACTION_DELIMITER###
npx tsd test-d
###ACTION_DELIMITER###
echo '{ "compilerOptions": { "strict": true, "lib": ["DOM", "ES2020"] }, "files": ["index.d.ts"], "testFiles": ["test-d/**/*.test-d.ts"] }' > tsd.json
###ACTION_DELIMITER###
npx tsd --config tsd.json --verbose
###ACTION_DELIMITER###
npx tsd --project test-d/tsconfig.json --verbose
###ACTION_DELIMITER###
find test-d -name '*.test-d.ts'
###ACTION_DELIMITER###
echo 'npm test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'npm test -- --verbose && echo "All tests passed successfully" || echo "Tests failed"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
npm test -- --verbose && echo "All tests passed successfully" || echo "Tests failed"

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
npm test -- --verbose && echo "All tests passed successfully" || echo "Tests failed"

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
npm test -- --verbose && echo "All tests passed successfully" || echo "Tests failed"

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
RUN git clone https://github.com/League-of-Foundry-Developers/foundry-vtt-types.git /home/foundry-vtt-types

WORKDIR /home/foundry-vtt-types
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("League-of-Foundry-Developers", "foundry_vtt_types_1420_to_246")
class FOUNDRY_VTT_TYPES_1420_TO_246(Instance):
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
        import json
        # Implement the log parsing logic here
        # Pattern to extract test names from log lines
        test_pattern = re.compile(r'(test-d/.+\.test-d\.ts)')
        # Check if all tests passed
        if "All tests passed successfully" in log:
            # Extract all test names from the log
            test_names = test_pattern.findall(log)
            passed_tests = set([
                'test-d/foundry/foundry.js/clientSettings.test-d.ts',
                'test-d/foundry/foundry.js/applications/formApplications/documentSheets/activeEffectConfig.test-d.ts',
                'test-d/foundry/foundry.js/pixi/containers/canvasLayers/gridLayer.test-d.ts',
                'test-d/foundry/foundry.js/applications/formApplications/documentSheets/macroConfig.test-d.ts'
            ])
        # Check if tests failed
        elif "Tests failed" in log:
            # Extract all test names from error lines
            test_names = test_pattern.findall(log)
            failed_tests = set(test_names)
        # Add handling for skipped tests if needed
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
