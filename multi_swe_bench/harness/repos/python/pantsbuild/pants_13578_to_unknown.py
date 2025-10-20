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
                """ls
###ACTION_DELIMITER###
./pants --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y gcc
###ACTION_DELIMITER###
./pants --version
###ACTION_DELIMITER###
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && source $HOME/.cargo/env
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && source $HOME/.cargo/env
###ACTION_DELIMITER###
source $HOME/.cargo/env && rustc --version
###ACTION_DELIMITER###
./pants --version
###ACTION_DELIMITER###
sed -i '21s/requests\[security\]>=2.25.1/requests\[security\]==2.26.0/' 3rdparty/python/requirements.txt
###ACTION_DELIMITER###
pip install -r 3rdparty/python/requirements.txt
###ACTION_DELIMITER###
./pants --version
###ACTION_DELIMITER###
echo -e '#!/bin/bash
./pants test --test-output=all ::' > /home/pants/test_commands.sh && chmod +x /home/pants/test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sysctl -w fs.inotify.max_user_watches=524288
###ACTION_DELIMITER###
apt-get update && apt-get install -y procps
###ACTION_DELIMITER###
sysctl -w fs.inotify.max_user_watches=524288
###ACTION_DELIMITER###
echo 524288 > /proc/sys/fs/inotify/max_user_watches
###ACTION_DELIMITER###
sed -i 's|./pants test --test-output=all ::|PANTS_FILESYSTEM_WATCHER=none ./pants test --test-output=all ::|' /home/pants/test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's|./pants test --test-output=all ::|./pants test --no-filesystem-watcher --test-output=all ::|' /home/pants/test_commands.sh
###ACTION_DELIMITER###
sed -i 's|--no-filesystem-watcher|--filesystem-watcher=none|' /home/pants/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PANTS_FILESYSTEM_WATCHER=none
./pants --filesystem-watcher=none test --test-output=all ::' > /home/pants/test_commands.sh && chmod +x /home/pants/test_commands.sh
###ACTION_DELIMITER###
echo -e '[GLOBAL]
filesystem_watcher = "none"' >> /home/pants/pants.toml
###ACTION_DELIMITER###
./pants killall && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/\[GLOBAL\]/a filesystem_watcher = "none"' /home/pants/pants.toml
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i '0,/\[GLOBAL\]/!{/\[GLOBAL\]/d}' /home/pants/pants.toml
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/\[GLOBAL\]/,/^\[/ s/filesystem_watcher = .*//' /home/pants/pants.toml && sed -i '/\[GLOBAL\]/a filesystem_watcher = "none"' /home/pants/pants.toml
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cat pants.toml
###ACTION_DELIMITER###
sed -i '0,/filesystem_watcher = "none"/!{/filesystem_watcher = "none"/d}' /home/pants/pants.toml
###ACTION_DELIMITER###
cat pants.toml
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i 's/--filesystem-watcher=none/--no-watch-filesystem/' /home/pants/test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/--no-watch-filesystem/--no-pantsd/' /home/pants/test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/\[GLOBAL\]/,/^\[/ s/filesystem_watcher = "none"//' /home/pants/pants.toml
###ACTION_DELIMITER###
echo -e '#!/bin/bash
./pants --no-pantsd --no-watch-filesystem test --test-output=all ::' > /home/pants/test_commands.sh && chmod +x /home/pants/test_commands.sh
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


@Instance.register("pantsbuild", "pants_13578_to_unknown")
class PANTS_13578_TO_UNKNOWN(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        # Parse passed tests using regex
        passed_pattern = re.compile(r"Completed: Run Pytest - (.*?)(?::tests)? succeeded\.?")
        passed_tests.update(passed_pattern.findall(log))
        # Parse failed tests using regex
        failed_pattern = re.compile(r"𐄂 (.*?) failed\.")
        failed_tests.update(failed_pattern.findall(log))
        # TODO: Add parsing for skipped tests if applicable
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
