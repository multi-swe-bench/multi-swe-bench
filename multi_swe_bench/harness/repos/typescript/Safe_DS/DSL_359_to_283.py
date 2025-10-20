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
        return "python:3.10-slim"
    
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
ls -la .github
###ACTION_DELIMITER###
ls -la .github/workflows
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-17-jdk
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y -t bullseye-backports openjdk-17-jdk
###ACTION_DELIMITER###
cat /etc/os-release
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-17-jdk
###ACTION_DELIMITER###
sed -i '/bullseye-backports/d' /etc/apt/sources.list && apt-get update && apt-get install -y openjdk-17-jdk
###ACTION_DELIMITER###
apt-cache search openjdk
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget && wget https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.9%2B9/OpenJDK17U-jdk_x64_linux_hotspot_17.0.9_9.tar.gz && tar -xzf OpenJDK17U-jdk_x64_linux_hotspot_17.0.9_9.tar.gz -C /opt && ln -s /opt/jdk-17.0.9+9 /opt/jdk-17 && export JAVA_HOME=/opt/jdk-17 && export PATH=$JAVA_HOME/bin:$PATH
###ACTION_DELIMITER###
export JAVA_HOME=/opt/jdk-17 && export PATH=$JAVA_HOME/bin:$PATH && java -version
###ACTION_DELIMITER###
ls -la DSL
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH" && poetry --version
###ACTION_DELIMITER###
cd Runtime/safe-ds-runner && poetry install --no-interaction --no-root && poetry install --no-interaction
###ACTION_DELIMITER###
cd ../safe-ds && poetry install --no-interaction --no-root && poetry install --no-interaction
###ACTION_DELIMITER###
bash -c 'echo -e "#!/bin/bash\nset -e\n\n# Test DSL component\ncd /home/DSL/DSL\n./gradlew check -i\n\n# Test Runtime Runner component\ncd /home/DSL/Runtime/safe-ds-runner\npoetry run pytest --doctest-modules --cov=safe_ds_runner --cov-report=xml -v\n\n# Test Runtime Stdlib component\ncd /home/DSL/Runtime/safe-ds\npoetry run pytest -v" > /home/DSL/test_commands.sh && chmod +x /home/DSL/test_commands.sh'
###ACTION_DELIMITER###
bash -c 'echo -e "#!/bin/bash\nset -e\n\n# Test DSL component (parallel execution)\ncd /home/DSL/DSL\n./gradlew check --parallel -i\n\n# Test Runtime Runner component (verbose, no coverage)\ncd /home/DSL/Runtime/safe-ds-runner\npoetry run pytest --doctest-modules -v\n\n# Test Runtime Stdlib component (verbose, no coverage)\ncd /home/DSL/Runtime/safe-ds\npoetry run pytest -v" > /home/DSL/test_commands.sh && chmod +x /home/DSL/test_commands.sh'"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e

# Test DSL component (parallel execution)
cd /home/DSL/DSL
./gradlew check --parallel -i

# Test Runtime Runner component (verbose, no coverage)
cd /home/DSL/Runtime/safe-ds-runner
poetry run pytest --doctest-modules -v

# Test Runtime Stdlib component (verbose, no coverage)
cd /home/DSL/Runtime/safe-ds
poetry run pytest -v

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
set -e

# Test DSL component (parallel execution)
cd /home/DSL/DSL
./gradlew check --parallel -i

# Test Runtime Runner component (verbose, no coverage)
cd /home/DSL/Runtime/safe-ds-runner
poetry run pytest --doctest-modules -v

# Test Runtime Stdlib component (verbose, no coverage)
cd /home/DSL/Runtime/safe-ds
poetry run pytest -v

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
set -e

# Test DSL component (parallel execution)
cd /home/DSL/DSL
./gradlew check --parallel -i

# Test Runtime Runner component (verbose, no coverage)
cd /home/DSL/Runtime/safe-ds-runner
poetry run pytest --doctest-modules -v

# Test Runtime Stdlib component (verbose, no coverage)
cd /home/DSL/Runtime/safe-ds
poetry run pytest -v

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

# Choose an appropriate base image based on the project's requirements - replace python:3.10-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.10-slim

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
RUN git clone https://github.com/Safe-DS/DSL.git /home/DSL

WORKDIR /home/DSL
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Safe-DS", "DSL_359_to_283")
class DSL_359_TO_283(Instance):
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
        # Extract passed tests: pattern matches "tests/.../test.py::test_name PASSED [percentage]"
        passed_pattern = r'(tests/.*?)\s+PASSED'
        passed_tests = set(re.findall(passed_pattern, log))
        # Extract failed tests: pattern matches "FAILED tests/.../test.py::test_name"
        failed_pattern = r'FAILED\s+(tests/.*)'
        failed_tests = set(re.findall(failed_pattern, log))
        # Skipped tests: pattern not identified in provided logs; adjust if necessary
        # skipped_pattern = r'(tests/.*?)\s+SKIPPED'
        # skipped_tests = set(re.findall(skipped_pattern, log))
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
