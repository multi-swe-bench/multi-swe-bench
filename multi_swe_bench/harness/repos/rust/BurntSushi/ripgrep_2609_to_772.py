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
        return "rustembedded/cross:x86_64-unknown-linux-musl"
    
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
cargo test
###ACTION_DELIMITER###
ls -F ci/
###ACTION_DELIMITER###
ci/ubuntu-install-packages
###ACTION_DELIMITER###
cross test --test integration
###ACTION_DELIMITER###
echo $PATH
###ACTION_DELIMITER###
cargo install cross
###ACTION_DELIMITER###
find / -name cargo
###ACTION_DELIMITER###
ls ~/.cargo/bin
###ACTION_DELIMITER###
export PATH=$PATH:/root/.cargo/bin
cargo test
###ACTION_DELIMITER###
export PATH=$PATH:/usr/local/cargo/bin
cross test --test integration
###ACTION_DELIMITER###
find / -name rustc
###ACTION_DELIMITER###
which curl
###ACTION_DELIMITER###
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
###ACTION_DELIMITER###
source "$HOME/.cargo/env"
cargo install cross
###ACTION_DELIMITER###
source "$HOME/.cargo/env"
cross test --test integration
###ACTION_DELIMITER###
source "$HOME/.cargo/env"
cargo test --test integration
###ACTION_DELIMITER###
echo 'source "$HOME/.cargo/env" && cargo test --test integration' > /home/ripgrep/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
source "$HOME/.cargo/env" && cargo test --test integration

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
source "$HOME/.cargo/env" && cargo test --test integration

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
source "$HOME/.cargo/env" && cargo test --test integration

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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM rustembedded/cross:x86_64-unknown-linux-musl

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
RUN git clone https://github.com/BurntSushi/ripgrep.git /home/ripgrep

WORKDIR /home/ripgrep
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("BurntSushi", "ripgrep_2609_to_772")
class RIPGREP_2609_TO_772(Instance):
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
        passed_tests = set() # Tests that passed successfully
        failed_tests = set() # Tests that failed
        skipped_tests = set() # Tests that were skipped
        import re
        # Regex to capture test status
        passed_regex = re.compile(r"^test (.*) ... ok$")
        failed_regex = re.compile(r"^test (.*) ... FAILED$")
        failures_block_regex = re.compile(r"failures:\n((?:    .*\n)+)")
        for line in log.splitlines():
            if passed_match := passed_regex.match(line):
                passed_tests.add(passed_match.group(1).strip())
            elif failed_match := failed_regex.match(line):
                failed_tests.add(failed_match.group(1).strip())
        # Check for failure block
        if failure_block := failures_block_regex.search(log):
            for line in failure_block.group(1).splitlines():
                failed_tests.add(line.strip())
                # Remove from passed if it was already added
                if line.strip() in passed_tests:
                    passed_tests.remove(line.strip())
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
