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
python3 -m pip install -e .
###ACTION_DELIMITER###
echo -e 'python3 -m coverage run tests/aggregate_tests.py -v
python3 -m coverage report -m --fail-under 97' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
python3 -m pip install -r requirements-test.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'pytest --verbose --tb=short tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
python3 -m pip install pytest
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
python3 tests/simple_server.py
###ACTION_DELIMITER###
timeout 10s python3 tests/simple_server.py > server_output.log 2>&1
###ACTION_DELIMITER###
cat server_output.log
###ACTION_DELIMITER###
ls -la tests/simple_server.py
###ACTION_DELIMITER###
sed -i 's/print(port_message)/print(port_message, flush=True)/' tests/simple_server.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'cd tests
python3 -m coverage run aggregate_tests.py -v
python3 -m coverage report -m --fail-under 97' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'python3 -m coverage run tests/aggregate_tests.py -v
python3 -m coverage report -m --fail-under 97' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'pytest -s -v tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i '59i\    try:\n' tests/simple_server.py && sed -i '60s/^/        /' tests/simple_server.py && sed -i '61s/^/        /' tests/simple_server.py && sed -i '62s/^/        /' tests/simple_server.py && sed -i '63s/^/        /' tests/simple_server.py && sed -i '64i\    except Exception as e:\n        print("Server startup error:", e, flush=True)\n        exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
python3 tests/simple_server.py
###ACTION_DELIMITER###
sed -i '59s/^    //' tests/simple_server.py && sed -i '60,63s/^/    /' tests/simple_server.py && sed -i '64s/^    //' tests/simple_server.py
###ACTION_DELIMITER###
python3 tests/simple_server.py
###ACTION_DELIMITER###
sed -i '60i\    try:' tests/simple_server.py && sed -i '60,63s/^/        /' tests/simple_server.py && sed -i '64i\    except Exception as e:\n        print("Server startup error:", e, flush=True)\n        exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
sed -i '60s/^/try:\n    /' tests/simple_server.py && sed -i '61s/^/    /' tests/simple_server.py && sed -i '62s/^/    /' tests/simple_server.py && sed -i '63s/^/    /' tests/simple_server.py && sed -i '64i\except Exception as e:\n    print("Server startup error:", e, flush=True)\n    exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
sed -i '60i try:' tests/simple_server.py && sed -i '61,64s/^/    /' tests/simple_server.py && sed -i '65i except Exception as e:\n    print("Server startup error:", e, flush=True)\n    exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
sed -i '60i try:' tests/simple_server.py && sed -i '61,64s/^/    /' tests/simple_server.py && sed -i '65i except Exception as e:\n    print("Server startup error:", e, flush=True)\n    exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
sed -i '60i try:\n    ' tests/simple_server.py && sed -i '61,64s/^/    /' tests/simple_server.py && sed -i '65i except Exception as e:\n    print("Server startup error:", e, flush=True)\n    exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
sed -i '60i try:' tests/simple_server.py && sed -i '61,64s/^/    /' tests/simple_server.py && sed -i '65i except Exception as e:\n    print("Server startup error:", e, flush=True)\n    exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
sed -i '59i try:' tests/simple_server.py && sed -i '60,63s/^/    /' tests/simple_server.py && sed -i '64i except Exception as e:\n    print("Server startup error:", e, flush=True)\n    exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
sed -i '60i try:' tests/simple_server.py && sed -i '61,64s/^/    /' tests/simple_server.py && sed -i '65i except Exception as e:\n    print("Server startup error:", e, flush=True)\n    exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
sed -i '60i try:' tests/simple_server.py && sed -i '61,64s/^/    /' tests/simple_server.py && sed -i '65i except Exception as e:\n    print("Server startup error:", e, flush=True)\n    exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
sed -i '/^httpd = socketserver.TCPServer/i\try:' tests/simple_server.py && sed -i '/^httpd = socketserver.TCPServer/,/^httpd.serve_forever()/s/^/    /' tests/simple_server.py && sed -i '/^httpd.serve_forever()/a\except Exception as e:\n    print("Server startup error:", e, flush=True)\n    exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
python3 tests/simple_server.py
###ACTION_DELIMITER###
sed -i '/^httpd = socketserver.TCPServer/i\try:' tests/simple_server.py && sed -i '/^httpd = socketserver.TCPServer/,/^httpd.serve_forever()/s/^/    /' tests/simple_server.py && sed -i '/^    httpd.serve_forever()/a\except Exception as e:\n    print("Server startup error:", e, flush=True)\n    exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
sed -i '/^httpd = socketserver.TCPServer/i\try:' tests/simple_server.py && sed -i '/^httpd = socketserver.TCPServer/s/^/    /' tests/simple_server.py && sed -i '/^port_message = /s/^/    /' tests/simple_server.py && sed -i '/^print(port_message/s/^/    /' tests/simple_server.py && sed -i '/^httpd.serve_forever()/s/^/    /' tests/simple_server.py && sed -i '/^    httpd.serve_forever()/a\except Exception as e:\n    print("Server startup error:", e, flush=True)\n    exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
sed -i '60,63s/^/    /' tests/simple_server.py
###ACTION_DELIMITER###
python3 tests/simple_server.py
###ACTION_DELIMITER###
sed -i '/^httpd = socketserver.TCPServer/i\try:' tests/simple_server.py && sed -i '/^httpd = socketserver.TCPServer/,/^httpd.serve_forever()/s/^/    /' tests/simple_server.py && sed -i '/^    httpd.serve_forever()/a\except Exception as e:\n    print("Server startup error:", e, flush=True)\n    exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
sed -i '/^httpd = socketserver.TCPServer/i\try:' tests/simple_server.py && sed -i '/^httpd = socketserver.TCPServer/,/^httpd.serve_forever()/s/^/    /' tests/simple_server.py && sed -i '/^    httpd.serve_forever()/a\except Exception as e:\n    print("Server startup error:", e, flush=True)\n    exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
sed -i '/^httpd = socketserver.TCPServer/i\try:' tests/simple_server.py && sed -i '/^httpd = socketserver.TCPServer/,/^httpd.serve_forever()/s/^/    /' tests/simple_server.py && sed -i '/^    httpd.serve_forever()/a\except Exception as e:\n    print("Server startup error:", e, flush=True)\n    exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
sed -i '/^httpd = socketserver.TCPServer/i\try:' tests/simple_server.py && sed -i '/^httpd = socketserver.TCPServer/,/^httpd.serve_forever()/s/^/    /' tests/simple_server.py && sed -i '/^    httpd.serve_forever()/a\except Exception as e:\n    print("Server startup error:", e, flush=True)\n    exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
sed -i '/^httpd = socketserver.TCPServer/i\try:' tests/simple_server.py && sed -i 's/^httpd = socketserver.TCPServer/    &/' tests/simple_server.py && sed -i 's/^port_message = /    &/' tests/simple_server.py && sed -i 's/^print(port_message/    &/' tests/simple_server.py && sed -i 's/^httpd.serve_forever()/    &/' tests/simple_server.py && sed -i '/^    httpd.serve_forever()/a\except Exception as e:\n    print("Server startup error:", e, flush=True)\n    exit(1)' tests/simple_server.py
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -s -v tests/

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
pytest -s -v tests/

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
pytest -s -v tests/

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
RUN git clone https://github.com/theupdateframework/python-tuf.git /home/python-tuf

WORKDIR /home/python-tuf
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("theupdateframework", "python_tuf_1446_to_1340")
class PYTHON_TUF_1446_TO_1340(Instance):
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
        passed_tests: set[str] = set() # Tests that passed successfully
        failed_tests: set[str] = set() # Tests that failed
        skipped_tests: set[str] = set() # Tests that were skipped
        import re
        import json
        # Use regex to find all test cases and their statuses
        # Handle both 'test_name STATUS' and 'STATUS test_name' formats
        # Process each line to capture test cases and statuses
        for line in log.split('\n'):
            # Check for 'test... STATUS' pattern
            match = re.search(r'(tests/[\w/.:]+)\s+(PASSED|FAILED|ERROR|SKIPPED)', line)
            if match:
                test_name, status = match.groups()
            else:
                # Check for 'STATUS test...' pattern
                match = re.search(r'(PASSED|FAILED|ERROR|SKIPPED)\s+(tests/[\w/.:]+)', line)
                if match:
                    status, test_name = match.groups()
                else:
                    continue
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ('FAILED', 'ERROR'):
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
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
