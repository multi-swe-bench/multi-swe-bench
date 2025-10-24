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
                """ls
###ACTION_DELIMITER###
make init
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make init
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
ln -s /usr/bin/python3 /usr/bin/python
###ACTION_DELIMITER###
make init
###ACTION_DELIMITER###
python -m venv venv
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
make init
###ACTION_DELIMITER###
apt-get update && apt-get install -y ca-certificates curl gnupg && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && apt-get update && apt-get install -y nodejs && npm install -g yarn
###ACTION_DELIMITER###
yarn --version
###ACTION_DELIMITER###
make init
###ACTION_DELIMITER###
corepack enable
###ACTION_DELIMITER###
corepack prepare yarn@4.5.3 --activate
###ACTION_DELIMITER###
make init
###ACTION_DELIMITER###
apt-get update && apt-get install -y protobuf-compiler
###ACTION_DELIMITER###
make init
###ACTION_DELIMITER###
echo -e '#!/bin/bash\n\n# Unit tests\ncd lib && PYTHONPATH=. pytest -v -l tests/ -m "not performance" .\n\n# Integration tests\ncd .. && cd lib && PYTHONPATH=. pytest -v --require-integration -l tests/ .\n\n# Type checking\ncd .. && mypy --config-file=lib/mypy.ini --namespace-packages lib/streamlit/ lib/tests/streamlit/typing/ scripts/\n\n# Bare execution tests\nPYTHONPATH=. python3 scripts/run_bare_execution_tests.py\n\n# CLI smoke tests\npython3 scripts/cli_smoke_tests.py' > test_commands.sh && chmod +x test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash

# Unit tests
cd lib && PYTHONPATH=. pytest -v -l tests/ -m "not performance" .

# Integration tests
cd .. && cd lib && PYTHONPATH=. pytest -v --require-integration -l tests/ .

# Type checking
cd .. && mypy --config-file=lib/mypy.ini --namespace-packages lib/streamlit/ lib/tests/streamlit/typing/ scripts/

# Bare execution tests
PYTHONPATH=. python3 scripts/run_bare_execution_tests.py

# CLI smoke tests
python3 scripts/cli_smoke_tests.py

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
#!/bin/bash

# Unit tests
cd lib && PYTHONPATH=. pytest -v -l tests/ -m "not performance" .

# Integration tests
cd .. && cd lib && PYTHONPATH=. pytest -v --require-integration -l tests/ .

# Type checking
cd .. && mypy --config-file=lib/mypy.ini --namespace-packages lib/streamlit/ lib/tests/streamlit/typing/ scripts/

# Bare execution tests
PYTHONPATH=. python3 scripts/run_bare_execution_tests.py

# CLI smoke tests
python3 scripts/cli_smoke_tests.py

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
#!/bin/bash

# Unit tests
cd lib && PYTHONPATH=. pytest -v -l tests/ -m "not performance" .

# Integration tests
cd .. && cd lib && PYTHONPATH=. pytest -v --require-integration -l tests/ .

# Type checking
cd .. && mypy --config-file=lib/mypy.ini --namespace-packages lib/streamlit/ lib/tests/streamlit/typing/ scripts/

# Bare execution tests
PYTHONPATH=. python3 scripts/run_bare_execution_tests.py

# CLI smoke tests
python3 scripts/cli_smoke_tests.py

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
RUN git clone https://github.com/streamlit/streamlit.git /home/streamlit

WORKDIR /home/streamlit
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("streamlit", "streamlit_10651_to_10642")
class STREAMLIT_10651_TO_10642(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re

        test_pattern = re.compile(r"^(tests/.*?)\s+(PASSED|FAILED|SKIPPED)\s+\[.*\]$")
        for line in log.splitlines():
            line = line.strip()
            match = test_pattern.match(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
                if status == "PASSED":
                    passed_tests.add(test_name)
                elif status == "FAILED":
                    failed_tests.add(test_name)
                elif status == "SKIPPED":
                    skipped_tests.add(test_name)
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
