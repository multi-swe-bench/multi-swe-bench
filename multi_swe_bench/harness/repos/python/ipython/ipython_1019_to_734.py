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
                """python3 --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
apt-get install -y python3-pip
###ACTION_DELIMITER###
pip3 install -e .
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
sed -i 's/use_2to3 = True, //' setup3.py
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
find . -name 'requirements*.txt'
###ACTION_DELIMITER###
ls
###ACTION_DELIMITER###
find . -name 'test_*.py'
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
echo 'deb http://archive.ubuntu.com/ubuntu focal main universe' >> /etc/apt/sources.list
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python2.7
###ACTION_DELIMITER###
apt-get install -y python2.7-pip
###ACTION_DELIMITER###
apt-get install -y curl && curl -O https://bootstrap.pypa.io/pip/2.7/get-pip.py && python2.7 get-pip.py
###ACTION_DELIMITER###
pip2.7 install -e .
###ACTION_DELIMITER###
pip2.7 install pytest
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
deactivate
###ACTION_DELIMITER###
python2.7 -m pytest -v
###ACTION_DELIMITER###
sed -i 's/IOStream(sys.stdin)/IOStream(sys.stdin, fallback=sys.stdin)/' /home/ipython/IPython/utils/io.py && sed -i 's/IOStream(sys.stdout)/IOStream(sys.stdout, fallback=sys.stdout)/' /home/ipython/IPython/utils/io.py && sed -i 's/IOStream(sys.stderr)/IOStream(sys.stderr, fallback=sys.stderr)/' /home/ipython/IPython/utils/io.py
###ACTION_DELIMITER###
python2.7 -m pytest -v
###ACTION_DELIMITER###
sed -i 's/stdin = IOStream(sys.stdin, fallback=sys.stdin)/stdin = IOStream(sys.stdin, fallback=sys.stdout)/' /home/ipython/IPython/utils/io.py
###ACTION_DELIMITER###
python2.7 -m pytest -v
###ACTION_DELIMITER###
pip2.7 install nose
###ACTION_DELIMITER###
pip2.7 install pyzmq
###ACTION_DELIMITER###
python2.7 -m pytest -v
###ACTION_DELIMITER###
pip2.7 install twisted pymongo
###ACTION_DELIMITER###
python2.7 -m pytest -v --ignore=IPython/deathrow
###ACTION_DELIMITER###
pip2.7 install tornado pygments pymongo==2.8
###ACTION_DELIMITER###
python2.7 -m pytest -v --ignore=IPython/deathrow --ignore=IPython/frontend/qt --ignore=IPython/frontend/html --ignore=IPython/parallel/tests/test_mongodb.py
###ACTION_DELIMITER###
pip2.7 install matplotlib && python2.7 -m pytest -v --ignore=IPython/deathrow --ignore=IPython/frontend/qt --ignore=IPython/frontend/html --ignore=IPython/parallel/tests/test_mongodb.py --ignore=docs
###ACTION_DELIMITER###
echo 'python2.7 -m pytest -v --ignore=IPython/deathrow --ignore=IPython/frontend/qt --ignore=IPython/frontend/html --ignore=IPython/parallel/tests/test_mongodb.py --ignore=docs' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python2.7 -m pytest -v --ignore=IPython/deathrow --ignore=IPython/frontend/qt --ignore=IPython/frontend/html --ignore=IPython/parallel/tests/test_mongodb.py --ignore=docs

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
python2.7 -m pytest -v --ignore=IPython/deathrow --ignore=IPython/frontend/qt --ignore=IPython/frontend/html --ignore=IPython/parallel/tests/test_mongodb.py --ignore=docs

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
python2.7 -m pytest -v --ignore=IPython/deathrow --ignore=IPython/frontend/qt --ignore=IPython/frontend/html --ignore=IPython/parallel/tests/test_mongodb.py --ignore=docs

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
RUN git clone https://github.com/ipython/ipython.git /home/ipython

WORKDIR /home/ipython
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ipython", "ipython_1019_to_734")
class IPYTHON_1019_TO_734(Instance):
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
        passed_tests = set() # Tests that passed successfully
        failed_tests = set() # Tests that failed
        skipped_tests = set() # Tests that were skipped
        import re
        import json
        # Use regex to extract test names and statuses
        pattern = re.compile(r"^(.*?)\s+(PASSED|FAILED|SKIPPED)\s+\[\s*\d+%\]", re.MULTILINE)
        matches = pattern.findall(log)
        for test_name, status in matches:
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status == "FAILED":
                failed_tests.add(test_name)
            elif status == "SKIPPED":
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
