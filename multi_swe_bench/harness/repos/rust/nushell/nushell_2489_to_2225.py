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
apt-get update && apt-get install -y libxcb-composite0-dev libx11-dev python3
###ACTION_DELIMITER###
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
###ACTION_DELIMITER###
source /root/.cargo/env && cargo build --workspace --features=extra
###ACTION_DELIMITER###
source /root/.cargo/env && cargo update
###ACTION_DELIMITER###
source /root/.cargo/env && cargo search s3handler
###ACTION_DELIMITER###
sed -i 's/s3handler = "0.5.0"/s3handler = "0.9.0"/' crates/nu_plugin_s3/Cargo.toml
###ACTION_DELIMITER###
source /root/.cargo/env && cargo update
###ACTION_DELIMITER###
source /root/.cargo/env && cargo build --workspace --features=extra
###ACTION_DELIMITER###
git reset --hard
###ACTION_DELIMITER###
apt-get update && apt-get install -y libxcb-composite0-dev libx11-dev python3 curl
###ACTION_DELIMITER###
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
###ACTION_DELIMITER###
source /root/.cargo/env && cargo build --workspace --features=extra
###ACTION_DELIMITER###
source /root/.cargo/env && cargo build --workspace
###ACTION_DELIMITER###
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain 1.41.0
###ACTION_DELIMITER###
source /root/.cargo/env && cargo build --workspace --features=extra
###ACTION_DELIMITER###
apt-get update && apt-get install -y libxcb-composite0-dev libx11-dev python3 curl
###ACTION_DELIMITER###
source /root/.cargo/env && cargo test --workspace --no-run
###ACTION_DELIMITER###
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain 1.42.0
###ACTION_DELIMITER###
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain 1.43.0
###ACTION_DELIMITER###
source /root/.cargo/env && cargo build --workspace --features=extra
###ACTION_DELIMITER###
source /root/.cargo/env && cargo test --workspace --features=extra -- --nocapture
###ACTION_DELIMITER###
echo 'source /root/.cargo/env && cargo test --workspace --features=extra -- --nocapture' > /home/nushell/test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
source /root/.cargo/env && cargo test --workspace --features=extra -- --nocapture

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
source /root/.cargo/env && cargo test --workspace --features=extra -- --nocapture

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
source /root/.cargo/env && cargo test --workspace --features=extra -- --nocapture

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
RUN apt-get update && apt-get install -y git libssl-dev pkg-config

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


@Instance.register("nushell", "nushell_2489_to_2225")
class NUSHELL_2489_TO_2225(Instance):
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
        import json
        passed_pattern = re.compile(r"test (.*) ... ok")
        failed_pattern = re.compile(r"^\s+(.+)$")
        lines = log.splitlines()
        in_failures_section = False
        for line in lines:
            if 'failures:' in line:
                in_failures_section = True
                continue
            if in_failures_section and line.strip() and 'test result:' not in line:
                # Check if the line is not empty and not the summary line
                if line.strip():
                    failed_tests.add(line.strip())
            else:
                match = passed_pattern.search(line)
                if match:
                    passed_tests.add(match.group(1))
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
