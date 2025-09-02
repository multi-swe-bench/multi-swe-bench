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
                """ls -F
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y rustc cargo
###ACTION_DELIMITER###
cargo test --verbose -- --nocapture
###ACTION_DELIMITER###
ls -F
###ACTION_DELIMITER###
cargo test
###ACTION_DELIMITER###
cargo build --features yaml
###ACTION_DELIMITER###
sed -i '510s/!$ident/!$ident:ident/' src/macros.rs
###ACTION_DELIMITER###
cargo build --features yaml
###ACTION_DELIMITER###
cargo test --features yaml
###ACTION_DELIMITER###
echo 'cargo test --features yaml' > test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
cargo test --features yaml

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
cargo test --features yaml

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn  /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
cargo test --features yaml

""".format(
                    pr=self.pr
                ),
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
RUN git clone https://github.com/clap-rs/clap.git /home/clap

WORKDIR /home/clap
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("clap-rs", "clap_703_to_682")
class CLAP_703_TO_682(Instance):
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
        # Regex patterns
        passed_pattern = re.compile(r"test (.*?) \.\.\. ok")
        failed_pattern = re.compile(r"test (.*?) \.\.\. FAILED")
        failures_section_pattern = re.compile(r"failures:\n\n(.*?)\n\nfailures:", re.DOTALL)
        individual_failure_pattern = re.compile(r"^    (.*?)$", re.MULTILINE)
        ignored_pattern = re.compile(r"test result: .*? (\d+) ignored")
        # Find passed tests
        for match in passed_pattern.finditer(log):
            passed_tests.add(match.group(1).strip())
        # Find failed tests
        for match in failed_pattern.finditer(log):
            failed_tests.add(match.group(1).strip())
        # Find failed tests from the failures section
        failures_section_match = failures_section_pattern.search(log)
        if failures_section_match:
            failures_text = failures_section_match.group(1)
            for failure in individual_failure_pattern.finditer(failures_text):
                failed_tests.add(failure.group(1).strip())
        # Find ignored (skipped) tests from the summary
        ignored_match = ignored_pattern.search(log)
        if ignored_match:
            # Since we don't have the names of ignored tests, we'll have to live with just the count.
            # To make the output consistent, we'll create dummy names.
            num_ignored = int(ignored_match.group(1))
            for i in range(num_ignored):
                skipped_tests.add(f"ignored_test_{i+1}")
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
