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
        return "ubuntu:16.04"
    
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
apt-get install -y libssl-dev
###ACTION_DELIMITER###
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
###ACTION_DELIMITER###
source $HOME/.cargo/env
###ACTION_DELIMITER###
rustup default nightly
###ACTION_DELIMITER###
cargo install --path . --features rawkey,clipboard
###ACTION_DELIMITER###
cargo update
###ACTION_DELIMITER###
sed 's/heim = "0.0.6"/heim = "0.0.9"/' Cargo.toml > Cargo.toml.new && mv Cargo.toml.new Cargo.toml
###ACTION_DELIMITER###
cargo install --path . --features rawkey,clipboard
###ACTION_DELIMITER###
cargo search heim
###ACTION_DELIMITER###
sed 's/heim = "..*"/heim = "0.1.0-rc.1"/' Cargo.toml > Cargo.toml.new && mv Cargo.toml.new Cargo.toml
###ACTION_DELIMITER###
cargo install --path . --features rawkey,clipboard
###ACTION_DELIMITER###
cargo update
###ACTION_DELIMITER###
cargo install --path . --features rawkey,clipboard
###ACTION_DELIMITER###
rustup install 1.70.0
###ACTION_DELIMITER###

###ACTION_DELIMITER###
rustup default 1.70.0
###ACTION_DELIMITER###
cargo install --path . --features rawkey,clipboard
###ACTION_DELIMITER###
rustup install nightly-2019-08-22
###ACTION_DELIMITER###
rustup default nightly-2019-08-22
###ACTION_DELIMITER###
sed 's/heim = ".*"/heim = "0.0.6"/' Cargo.toml > Cargo.toml.new && mv Cargo.toml.new Cargo.toml
###ACTION_DELIMITER###

###ACTION_DELIMITER###
cargo install --path . --features rawkey,clipboard
###ACTION_DELIMITER###
cargo build --features rawkey,clipboard
###ACTION_DELIMITER###
cargo build --locked --features rawkey,clipboard
###ACTION_DELIMITER###
rm Cargo.lock
###ACTION_DELIMITER###
ls -aF
###ACTION_DELIMITER###
cargo test
###ACTION_DELIMITER###
git checkout v0.2.0
###ACTION_DELIMITER###
git tag
###ACTION_DELIMITER###
git checkout 0.2.0
###ACTION_DELIMITER###
cargo install --path . --features rawkey,clipboard
###ACTION_DELIMITER###
git checkout 1b863cbb2bee233c4092fb68e08f134780292ba3
###ACTION_DELIMITER###
cargo test --locked --all --verbose
###ACTION_DELIMITER###
apt-get install -y build-essential
###ACTION_DELIMITER###

###ACTION_DELIMITER###
cargo test --locked --all --verbose
###ACTION_DELIMITER###
apt-get install -y pkg-config
###ACTION_DELIMITER###
cargo test --locked --all --verbose
###ACTION_DELIMITER###

###ACTION_DELIMITER###
cargo test --locked --all --verbose
###ACTION_DELIMITER###
echo 'cargo test --locked --all --verbose' > /home/nushell/test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
cargo test --locked --all --verbose

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
cargo test --locked --all --verbose

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
cargo test --locked --all --verbose

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
FROM ubuntu:16.04

## Set noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Install basic requirements
# For example: RUN apt-get update && apt-get install -y git
# For example: RUN yum install -y git
# For example: RUN apk add --no-cache git
RUN apt-get update && apt-get install -y git curl

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


@Instance.register("nushell", "nushell_399_to_206")
class NUSHELL_399_TO_206(Instance):
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
          if line.startswith("test "):
            parts = line.split(" ... ")
            test_name = parts[0].replace("test ", "").strip()
            if len(parts) > 1:
              status = parts[1].strip()
              if status == "ok":
                passed_tests.add(test_name)
              elif status == "FAILED":
                failed_tests.add(test_name)
              else:
                # Handle other statuses if needed
                pass
        # Look for the failures block
        in_failures_block = False
        for line in log.splitlines():
          if line.strip() == "failures:":
            in_failures_block = True
            continue
          if in_failures_block and line.strip().startswith("----"):
              # Ignore the stdout block for failures
              in_failures_block = False
              continue
          if in_failures_block and line.strip() and line.startswith("    ") and not line.strip().startswith("----"):
            failed_tests.add(line.strip())
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
