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
        return "python:3.9-slim"

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
                """ls -la
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip install numpy==1.24.4
###ACTION_DELIMITER###
pip install ".[dev]"
###ACTION_DELIMITER###
echo -e 'python3 -m pytest -v -c pytest.python3.ini
cram -v --shell=/bin/bash tests/' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y iqtree
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y muscle
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y mafft
###ACTION_DELIMITER###
cram -v tests/builds/zika_compressed.t
###ACTION_DELIMITER###
pip install -e ".[dev]"
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y vcftools
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
python3 -m pytest -v -c pytest.python3.ini
cram -v --shell=/bin/bash tests/

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
python3 -m pytest -v -c pytest.python3.ini
cram -v --shell=/bin/bash tests/

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
python3 -m pytest -v -c pytest.python3.ini
cram -v --shell=/bin/bash tests/

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.9-slim

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
RUN git clone https://github.com/nextstrain/augur.git /home/augur

WORKDIR /home/augur
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("nextstrain", "augur_1119_to_1088")
class AUGUR_1119_TO_1088(Instance):
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

        current_test = None
        lines = log.split("\n")
        for line in lines:
            line_stripped = line.strip()
            # Handle inline status (e.g., 'test_name PASSED' or 'test_name: passed')
            if line_stripped.endswith(("PASSED", "passed")):
                status_len = (
                    len("PASSED") if line_stripped.endswith("PASSED") else len("passed")
                )
                test_name = line_stripped[:-status_len].strip().rstrip(":")
                passed_tests.add(test_name)
            elif line_stripped.endswith(("FAILED", "failed")):
                status_len = (
                    len("FAILED") if line_stripped.endswith("FAILED") else len("failed")
                )
                test_name = line_stripped[:-status_len].strip().rstrip(":")
                failed_tests.add(test_name)
            elif line_stripped.endswith(("SKIPPED", "skipped")):
                status_len = (
                    len("SKIPPED")
                    if line_stripped.endswith("SKIPPED")
                    else len("skipped")
                )
                test_name = line_stripped[:-status_len].strip().rstrip(":")
                skipped_tests.add(test_name)
            # Capture test name for standalone status (e.g., 'test_name' followed by 'PASSED')
            elif "::" in line_stripped or (
                line_stripped.endswith(".t")
                and not line_stripped.endswith(
                    ("PASSED", "passed", "FAILED", "failed", "SKIPPED", "skipped")
                )
            ):
                test_name = line_stripped.split(" ", 1)[
                    0
                ]  # Split on first space to ignore extra info
                current_test = test_name
            # Handle standalone status lines (e.g., 'PASSED' on its own line)
            elif line_stripped in ("PASSED", "FAILED", "SKIPPED"):
                if current_test:
                    if line_stripped == "PASSED":
                        passed_tests.add(current_test)
                    elif line_stripped == "FAILED":
                        failed_tests.add(current_test)
                    elif line_stripped == "SKIPPED":
                        skipped_tests.add(current_test)
                    current_test = None  # Reset after processing
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
