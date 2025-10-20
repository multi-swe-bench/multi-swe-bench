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
                """apt-get update && apt-get install -y libssl-dev libffi-dev python3-dev
###ACTION_DELIMITER###
python scripts/eachdist.py develop
###ACTION_DELIMITER###
apt-get install -y build-essential
###ACTION_DELIMITER###
python scripts/eachdist.py develop
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
python scripts/eachdist.py test -- -v' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
python scripts/eachdist.py test -- -vv' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
python scripts/eachdist.py test -- -vv -s' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
python scripts/eachdist.py test -- -vv -s --full-trace' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
pytest opentelemetry-api/tests -vv -s --full-trace
pytest opentelemetry-sdk/tests -vv -s --full-trace' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
pytest opentelemetry-api/tests -vv -s --full-trace
pytest opentelemetry-sdk/tests -vv -s --full-trace --showlocals --lf' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
python scripts/eachdist.py test -- -vv -s --full-trace' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
pytest opentelemetry-sdk/tests -vv -s --full-trace --debug' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
pip install -e opentelemetry-sdk[test]
pytest opentelemetry-sdk/tests -vv -s --full-trace --pdb' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
rm -rf .pytest_cache
pytest opentelemetry-sdk/tests -vv -s --full-trace' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
pip list
printenv
pytest opentelemetry-sdk/tests -vv -s --full-trace' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
pip install -e opentelemetry-sdk[test]
pytest opentelemetry-sdk/tests -vv -s --full-trace --showlocals' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
export PYTHONPATH=".:$PYTHONPATH"
python scripts/eachdist.py test -- -vv -s --full-trace' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
export PYTHONPATH=".:$PYTHONPATH"
pip install -e opentelemetry-sdk[test]
pytest opentelemetry-sdk/tests -vv -s --full-trace --showlocals' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
export PYTHONPATH=".:$PYTHONPATH"
pip install -e opentelemetry-sdk[test]
pytest opentelemetry-sdk/tests -vv -s --full-trace --showlocals' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
export PYTHONPATH=".:$PYTHONPATH"
python scripts/eachdist.py test -- -vv -s --full-trace' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
export PYTHONPATH=".:$PYTHONPATH"
python scripts/eachdist.py test -- -vv -s --full-trace

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
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
export PYTHONPATH=".:$PYTHONPATH"
python scripts/eachdist.py test -- -vv -s --full-trace

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
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
export PYTHONPATH=".:$PYTHONPATH"
python scripts/eachdist.py test -- -vv -s --full-trace

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
RUN git clone https://github.com/open-telemetry/opentelemetry-python.git /home/opentelemetry-python

WORKDIR /home/opentelemetry-python
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("open-telemetry", "opentelemetry_python_1656_to_1516")
class OPENTELEMETRY_PYTHON_1656_TO_1516(Instance):
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
        current_test = None
        # Regex patterns to match test names and statuses
        test_pattern = re.compile(r'([\w\/\.:-]+\.py::[\w:]+)')
        status_pattern = re.compile(r'(PASSED|FAILED|SKIPPED)')
        for line in log.split('\n'):
            # Capture test name if present
            test_match = test_pattern.search(line)
            if test_match:
                current_test = test_match.group(1)
            # Capture status if present and associate with current test
            status_match = status_pattern.search(line)
            if status_match and current_test:
                status = status_match.group(1)
                if status == 'PASSED':
                    passed_tests.add(current_test)
                elif status == 'FAILED':
                    failed_tests.add(current_test)
                elif status == 'SKIPPED':
                    skipped_tests.add(current_test)
                current_test = None  # Reset after associating status
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
