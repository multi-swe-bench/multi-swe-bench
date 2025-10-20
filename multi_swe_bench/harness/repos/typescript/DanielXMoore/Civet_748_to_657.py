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
                """ls -la
###ACTION_DELIMITER###
node -v
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && apt-get install -y nodejs
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo 'yarn test -- --verbose --reporter json' > test_commands.sh
###ACTION_DELIMITER###
yarn build
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'yarn test -- --require @danielx/hera/register --verbose --reporter json' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'yarn test -- --require @danielx/hera/register --require @danielx/civet/register --verbose --reporter json' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn test -- --require @danielx/hera/register --require @danielx/civet/register --verbose --reporter json

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
yarn test -- --require @danielx/hera/register --require @danielx/civet/register --verbose --reporter json

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
yarn test -- --require @danielx/hera/register --require @danielx/civet/register --verbose --reporter json

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
RUN git clone https://github.com/DanielXMoore/Civet.git /home/Civet

WORKDIR /home/Civet
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("DanielXMoore", "Civet_748_to_657")
class CIVET_748_TO_657(Instance):
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
        # Remove line number prefixes from each line
        lines = log.split('\n')
        cleaned_lines = [re.sub(r'^\[\s*\d+\]\s*', '', line) for line in lines]
        cleaned_content = '\n'.join(cleaned_lines)
        # Extract JSON object by excluding coverage report
        coverage_start = re.search(r'File\s+\|\s+% Stmts', cleaned_content)
        if coverage_start:
            json_content = cleaned_content[:coverage_start.start()]
        else:
            json_content = cleaned_content
        # Extract JSON object starting with 'stats' key
        stats_match = re.search(r'"stats"\s*:\s*\{', json_content)
        if not stats_match:
            return {"passed_tests": passed_tests, "failed_tests": failed_tests, "skipped_tests": skipped_tests}
        stats_start = stats_match.start()
        start_idx = json_content.rfind('{', 0, stats_start)
        end_idx = json_content.rfind('}')
        if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
            return {"passed_tests": passed_tests, "failed_tests": failed_tests, "skipped_tests": skipped_tests}
        json_content = json_content[start_idx:end_idx+1]
        # Parse JSON
        try:
            # Remove trailing commas to handle invalid JSON
            json_str = re.sub(r',\s*([\]}])', r'\1', json_content)
            log_data = json.loads(json_str)
        except json.JSONDecodeError:
            return {"passed_tests": passed_tests, "failed_tests": failed_tests, "skipped_tests": skipped_tests}
        # Process tests
        for test in log_data.get("tests", []):
            test_name = test.get("fullTitle", test.get("title", ""))
            if not test_name:
                continue
            pending = test.get("pending", False)
            if pending:
                skipped_tests.add(test_name)
            elif test.get("err") and (test["err"] != {} or (isinstance(test["err"], str) and test["err"].strip() != "")):
                failed_tests.add(test_name)
            else:
                passed_tests.add(test_name)
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
