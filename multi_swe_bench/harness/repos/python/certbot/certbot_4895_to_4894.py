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
                """ls
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
apt-get install -y libffi-dev libssl-dev ca-certificates binutils build-essential linux-headers-generic
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install -e .[dev]
###ACTION_DELIMITER###
pip install -e ./acme
###ACTION_DELIMITER###
pip install ConfigArgParse>=0.9.3 configobj parsedatetime>=1.3 zope.component zope.interface
###ACTION_DELIMITER###
echo -e '#!/bin/bash
nosetests -v --processes=-1 --process-timeout=100' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install nose
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pytest -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y python2 python2-dev
###ACTION_DELIMITER###
apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl
###ACTION_DELIMITER###
wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz
###ACTION_DELIMITER###
tar xzf Python-2.7.18.tgz
###ACTION_DELIMITER###
cd Python-2.7.18
###ACTION_DELIMITER###
./configure --prefix=/usr/local --enable-shared
###ACTION_DELIMITER###
make -j$(nproc)
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
wget https://bootstrap.pypa.io/pip/2.7/get-pip.py
###ACTION_DELIMITER###
python2.7 get-pip.py
###ACTION_DELIMITER###
LD_LIBRARY_PATH=/usr/local/lib python2.7 get-pip.py
###ACTION_DELIMITER###
cd /home/certbot
###ACTION_DELIMITER###
pip2.7 install -e .[dev]
###ACTION_DELIMITER###
echo "/usr/local/lib" > /etc/ld.so.conf.d/python27.conf && ldconfig
###ACTION_DELIMITER###
pip2.7 install -e .[dev]
###ACTION_DELIMITER###
pip2.7 install -e ./acme
###ACTION_DELIMITER###
pip2.7 install ConfigArgParse>=0.9.3 configobj parsedatetime>=1.3 zope.component zope.interface
###ACTION_DELIMITER###
pip2.7 install 'ConfigArgParse>=0.9.3' configobj 'parsedatetime>=1.3' zope.component zope.interface && pip2.7 freeze | grep -E 'ConfigArgParse|configobj|parsedatetime|zope.component|zope.interface'
###ACTION_DELIMITER###
echo -e '#!/bin/bash
nosetests -v --processes=-1 --process-timeout=100' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
deactivate && pip2.7 install nose && echo -e '#!/bin/bash
nosetests -v --processes=-1 --process-timeout=100' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip2.7 uninstall -y pyrfc3339 && pip2.7 install pyrfc3339==1.1 && bash test_commands.sh
###ACTION_DELIMITER###
pip2.7 install pyicu && bash test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
nosetests -v --processes=-1 --process-timeout=100

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
#!/bin/bash
nosetests -v --processes=-1 --process-timeout=100

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
#!/bin/bash
nosetests -v --processes=-1 --process-timeout=100

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
RUN git clone https://github.com/certbot/certbot.git /home/certbot

WORKDIR /home/certbot
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("certbot", "certbot_4895_to_4894")
class CERTBOT_4895_TO_4894(Instance):
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
        # Extract total tests from summary (e.g., 'Ran 158 tests')
        total_tests = 0
        summary_match = re.search(r'Ran (\d+) tests', log)
        if summary_match:
            total_tests = int(summary_match.group(1))
        # Extract all test names (test_* pattern)
        all_tests = set(re.findall(r'test_\w+', log))
        # Extract failed tests (FAIL:, ERROR: lines, or tracebacks)
        failed_pattern = re.compile(r'(?:FAIL|ERROR):\s*(test_\w+)|line \d+, in (test_\w+)', re.IGNORECASE)
        failed_tests = set(match for group in failed_pattern.findall(log) for match in group if match)
        # Extract skipped tests (SKIP: or SKIPPED: lines)
        skipped_pattern = re.compile(r'(?:SKIP|SKIPPED):\s*(test_\w+)', re.IGNORECASE)
        skipped_tests = set(skipped_pattern.findall(log))
        # Calculate passed tests (all tests not failed/skipped)
        passed_tests = all_tests - failed_tests - skipped_tests
        # Validate against total tests (if available)
        if total_tests > 0:
            actual_total = len(passed_tests) + len(failed_tests) + len(skipped_tests)
            if actual_total != total_tests:
                # Log a warning if test counts mismatch (optional)
                pass
        # Note: Adjust regex patterns based on actual log formats for skipped tests
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
