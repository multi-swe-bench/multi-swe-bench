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
        return "node:20-alpine"

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
                """echo -e '#!/bin/bash
set -e
npm run test -- --run --reporter=verbose --reporter=json
npm run test-browser -- --reporter=json --reporter=list' > test_commands.sh
###ACTION_DELIMITER###
apk update
###ACTION_DELIMITER###
apk add firefox
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
npx playwright install
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e
npm run test -- --run --reporter=verbose --reporter=json
npm run test-browser -- --reporter=json --reporter=list

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
set -e
npm run test -- --run --reporter=verbose --reporter=json
npm run test-browser -- --reporter=json --reporter=list

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
set -e
npm run test -- --run --reporter=verbose --reporter=json
npm run test-browser -- --reporter=json --reporter=list

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

# Choose an appropriate base image based on the project's requirements - replace node:20-alpine with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:20-alpine

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
RUN git clone https://github.com/ariakit/ariakit.git /home/ariakit

WORKDIR /home/ariakit
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ariakit", "ariakit_2704_to_2170")
class ARIAKIT_2704_TO_2170(Instance):
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
        import json

        # ---------- Parse Verbose Log Lines ----------
        # Passed tests (match checkmark followed by test name)
        passed_pattern = re.compile(r"✓\s+([^\n]+)", re.MULTILINE)
        passed_tests.update(match.strip() for match in passed_pattern.findall(log))
        # Failed tests (match FAIL followed by test name)
        failed_pattern = re.compile(r"FAIL\s+([^\n]+)", re.MULTILINE)
        failed_tests.update(match.strip() for match in failed_pattern.findall(log))
        # Skipped tests (match SKIP or ✗ followed by test name)
        skipped_pattern = re.compile(r"(SKIP|✗)\s+([^\n]+)", re.MULTILINE)
        skipped_tests.update(match[1].strip() for match in skipped_pattern.findall(log))
        # ---------- Parse JSON Structured Data ----------
        # Extract JSON section (logs often end with a JSON object)
        json_start = log.rfind("{")
        json_end = log.rfind("}") + 1
        if json_start != -1 and json_end != -1:
            try:
                json_data = json.loads(log[json_start:json_end])
                # Traverse JSON to find test results
                for test in json_data.get("testResults", []):
                    for assertion in test.get("assertionResults", [test]):
                        status = assertion.get("status")
                        test_name = assertion.get("fullName") or assertion.get("name")
                        if test_name and status:
                            if status == "passed":
                                passed_tests.add(test_name.strip())
                            elif status == "failed":
                                failed_tests.add(test_name.strip())
                            elif status == "skipped":
                                skipped_tests.add(test_name.strip())
            except json.JSONDecodeError:
                pass  # Ignore invalid JSON
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
