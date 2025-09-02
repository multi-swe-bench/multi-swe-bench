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
        return "ubuntu:20.04"
    
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
ls -F ci
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y rustc cargo build-essential pkg-config curl tar gzip strip
###ACTION_DELIMITER###
apt-get install -y rustc cargo build-essential pkg-config curl tar gzip binutils
###ACTION_DELIMITER###
cargo test
###ACTION_DELIMITER###
cargo update
###ACTION_DELIMITER###

###ACTION_DELIMITER###
cargo test
###ACTION_DELIMITER###
RUST_BACKTRACE=1 cargo test
###ACTION_DELIMITER###
apt-get remove -y rustc cargo
###ACTION_DELIMITER###
curl https://sh.rustup.rs -sSf | sh -s -- -y
###ACTION_DELIMITER###

###ACTION_DELIMITER###
export PATH="$HOME/.cargo/bin:$PATH" && cargo test
###ACTION_DELIMITER###
export PATH="$HOME/.cargo/bin:$PATH" && rustup install 1.27.0
###ACTION_DELIMITER###
export PATH="$HOME/.cargo/bin:$PATH" && rustup default 1.27.0
###ACTION_DELIMITER###
export PATH="$HOME/.cargo/bin:$PATH" && cargo test
###ACTION_DELIMITER###
rm Cargo.lock
###ACTION_DELIMITER###
export PATH="$HOME/.cargo/bin:$PATH" && cargo test
###ACTION_DELIMITER###
git checkout -- Cargo.lock
###ACTION_DELIMITER###
export PATH="$HOME/.cargo/bin:$PATH" && cargo build
###ACTION_DELIMITER###
export PATH="$HOME/.cargo/bin:$PATH" && cargo test
###ACTION_DELIMITER###
echo 'export PATH="$HOME/.cargo/bin:$PATH" && cargo test' > /home/fd/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
export PATH="$HOME/.cargo/bin:$PATH" && cargo test

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
export PATH="$HOME/.cargo/bin:$PATH" && cargo test

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
export PATH="$HOME/.cargo/bin:$PATH" && cargo test

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
FROM ubuntu:20.04

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
RUN git clone https://github.com/sharkdp/fd.git /home/fd

WORKDIR /home/fd
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("sharkdp", "fd_233_to_58")
class FD_233_TO_58(Instance):
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
        # TODO: Implement the parse_log function
        # Implement the log parsing logic here
        for line in log.splitlines():
            passed_match = re.match(r"test (.*) \.\.\. ok", line)
            if passed_match:
                passed_tests.add(passed_match.group(1).strip())
            failed_match = re.match(r"test (.*) \.\.\. FAILED", line)
            if failed_match:
                failed_tests.add(failed_match.group(1).strip())
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
