import re
import sys

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
        return "ubuntu:18.04"
    
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
ls -F .github/workflows/
###ACTION_DELIMITER###
apt-get update && apt-get install -y libxcb-composite0-dev pkg-config libssl-dev curl ca-certificates
###ACTION_DELIMITER###
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
###ACTION_DELIMITER###
source "$HOME/.cargo/env" && cargo build --workspace --features=stable
###ACTION_DELIMITER###
ls -aF
###ACTION_DELIMITER###
ls -aF
###ACTION_DELIMITER###

###ACTION_DELIMITER###
ls -F docker/
###ACTION_DELIMITER###
source "$HOME/.cargo/env" && rustup install 1.43.0 && rustup default 1.43.0
###ACTION_DELIMITER###
source "$HOME/.cargo/env" && cargo build --workspace --features=stable
###ACTION_DELIMITER###
apt-get update && apt-get install -y libxcb-composite0-dev pkg-config libssl-dev curl ca-certificates libx11-dev
###ACTION_DELIMITER###
source "$HOME/.cargo/env" && cargo build --workspace --features=stable
###ACTION_DELIMITER###
source "$HOME/.cargo/env" && rustup install 1.41.0 && rustup default 1.41.0
###ACTION_DELIMITER###
source "$HOME/.cargo/env" && cargo build --workspace --features=stable
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3
###ACTION_DELIMITER###
source "$HOME/.cargo/env" && cargo build --workspace --features=stable
###ACTION_DELIMITER###
source "$HOME/.cargo/env" && rustup install 1.69.0 && rustup default 1.69.0
###ACTION_DELIMITER###
source "$HOME/.cargo/env" && rustup install 1.47.0 && rustup default 1.47.0
###ACTION_DELIMITER###
ls -aF
###ACTION_DELIMITER###
source "$HOME/.cargo/env" && cargo build --workspace --features=stable
###ACTION_DELIMITER###
echo 'source "$HOME/.cargo/env" && cargo test --workspace --features=stable -- --nocapture' > /home/nushell/test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
source "$HOME/.cargo/env" && cargo test --workspace --features=stable -- --nocapture

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
source "$HOME/.cargo/env" && cargo test --workspace --features=stable -- --nocapture

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
source "$HOME/.cargo/env" && cargo test --workspace --features=stable -- --nocapture

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
FROM ubuntu:18.04

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
RUN git clone https://github.com/nushell/nushell.git /home/nushell

WORKDIR /home/nushell
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("nushell", "nushell_2082_to_1739")
class NUSHELL_2082_TO_1739(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        test_result_pattern = re.compile(r"test (.*) \.\.\. (ok|FAILED|ignored)")
        in_failures_block = False
        for line in log.splitlines():
            if line.strip() == "failures:":
                in_failures_block = True
                continue
            if in_failures_block:
                if line.strip() and not line.strip().startswith("====") and not line.strip().startswith("failures"):
                    failed_tests.add(line.strip().split(" ")[0])
                else:
                    in_failures_block = False
            match = test_result_pattern.search(line)
            if match:
                test_name = match.group(1).strip()
                status = match.group(2)
                if status == "ok":
                    passed_tests.add(test_name)
                elif status == "FAILED":
                    failed_tests.add(test_name)
                elif status == "ignored":
                    skipped_tests.add(test_name)
        passed_tests -= failed_tests
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
