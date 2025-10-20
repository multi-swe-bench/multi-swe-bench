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
apt-get update && apt-get install -y build-essential python3-dev
###ACTION_DELIMITER###
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
###ACTION_DELIMITER###
source $HOME/.cargo/env
###ACTION_DELIMITER###
echo -e '#!/bin/bash
./pants test :: --verbose
./cargo test --all --tests -- --nocapture' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
rustup install 1.55.0 && rustup default 1.55.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pystache==0.5.4/pystache==0.6.0/' 3rdparty/python/requirements.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libyaml-dev libssl-dev liblmdb-dev
###ACTION_DELIMITER###
cargo build --verbose
###ACTION_DELIMITER###
find . -name Cargo.toml
###ACTION_DELIMITER###
sed -i 's|./cargo test --all --tests -- --nocapture|cargo test --manifest-path src/rust/engine/Cargo.toml --all --tests -- --nocapture|' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/requests\[security\]>=2.25.1/requests[security]==2.26.0/' 3rdparty/python/requirements.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y libfuse-dev
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y pkg-config
###ACTION_DELIMITER###
sed -i 's|./pants test :: --verbose|./pants test --verbose ::|' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
./pants help test
###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i 's|--verbose|--test-output=all|' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 524288 > /proc/sys/fs/inotify/max_user_watches
###ACTION_DELIMITER###
sed -i 's|./pants test --test-output=all ::|./pants test --no-pantsd --test-output=all ::|' test_commands.sh
###ACTION_DELIMITER###
sed -i 's|./pants test --no-pantsd --test-output=all ::|./pants test --no-pantsd --no-watch-filesystem --test-output=all ::|' test_commands.sh && sed -i 's|cargo test --manifest-path src/rust/engine/Cargo.toml --all --tests -- --nocapture|cargo test --manifest-path src/rust/engine/Cargo.toml --all --tests -- --nocapture --skip brfs|' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|./pants test --no-pantsd --no-watch-filesystem --test-output=all ::|./pants --no-pantsd --no-watch-filesystem test --test-output=all ::|' test_commands.sh && sed -i 's|cargo test --manifest-path src/rust/engine/Cargo.toml --all --tests -- --nocapture --skip brfs|cargo test --manifest-path src/rust/engine/Cargo.toml --all --tests --exclude brfs -- --nocapture|' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|--test-output=all ::|--test-output=all :: --no-watch-filesystem|' test_commands.sh && sed -i 's|--exclude brfs|--exclude brfs --exclude watch|' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|--test-output=all :: --no-watch-filesystem|--test-output=all ::|' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
./pants --no-pantsd --no-watch-filesystem test --test-output=all ::
cargo test --manifest-path src/rust/engine/Cargo.toml --all --tests --exclude brfs --exclude watch -- --nocapture

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
#!/bin/bash
./pants --no-pantsd --no-watch-filesystem test --test-output=all ::
cargo test --manifest-path src/rust/engine/Cargo.toml --all --tests --exclude brfs --exclude watch -- --nocapture

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
#!/bin/bash
./pants --no-pantsd --no-watch-filesystem test --test-output=all ::
cargo test --manifest-path src/rust/engine/Cargo.toml --all --tests --exclude brfs --exclude watch -- --nocapture

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
RUN git clone https://github.com/pantsbuild/pants.git /home/pants

WORKDIR /home/pants
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pantsbuild", "pants_12976_to_12398")
class PANTS_12976_TO_12398(Instance):
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
        # Implement the log parsing logic here
        # Regex pattern to match test lines with name and status
        pattern = re.compile(r'test (.*?) \.\.\. (\w+)')
        matches = pattern.findall(log)
        for test_name, status in matches:
            if status == 'ok':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            # Add handling for other statuses (e.g., 'skipped') if present in logs
            # elif status == 'skipped':
            #     skipped_tests.add(test_name)
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
