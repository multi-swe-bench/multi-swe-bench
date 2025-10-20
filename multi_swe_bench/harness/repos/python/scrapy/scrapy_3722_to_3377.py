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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip python3-venv
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate && pip install -r requirements-py3.txt && pip install pytest
###ACTION_DELIMITER###
echo './venv/bin/pytest tests -v' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.10 python3.10-venv python3.10-pip
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.10 python3.10-venv && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.10 get-pip.py
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl python3.10 python3.10-venv && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.10 get-pip.py
###ACTION_DELIMITER###
python3.10 get-pip.py --force-reinstall
###ACTION_DELIMITER###
python3.10 -m venv venv310 && source venv310/bin/activate && pip install -r requirements-py3.txt && pip install pytest
###ACTION_DELIMITER###
echo './venv310/bin/pytest tests -v' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.8 python3.8-venv python3.8-dev && python3.8 -m venv venv38 && source venv38/bin/activate && pip install -r requirements-py3.txt && pip install 'Twisted<22.0' pytest && echo './venv38/bin/pytest tests -v' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
python3.8 -m venv venv38 && source venv38/bin/activate && pip install -r requirements-py3.txt && pip install 'Twisted<22.0' 'pyOpenSSL==20.0.1' 'cryptography==3.3.2' pytest && echo './venv38/bin/pytest tests -v' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.8-dev libssl-dev libxml2-dev libxslt1-dev zlib1g-dev && python3.8 -m venv venv38 && source venv38/bin/activate && pip install -r requirements-py3.txt && pip install 'Twisted==20.3.0' 'pyOpenSSL==19.1.0' 'cryptography==3.2.1' pytest && echo './venv38/bin/pytest tests -v' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.7 python3.7-venv python3.7-dev libssl1.1 && python3.7 -m venv venv37 && source venv37/bin/activate && pip install 'Twisted==20.3.0' 'pyOpenSSL==19.1.0' 'cryptography==3.2.1' 'lxml==4.6.3' 'parsel==1.6.0' pytest && pip install -r requirements-py3.txt && echo './venv37/bin/pytest tests -v' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'deb http://archive.ubuntu.com/ubuntu focal main universe' >> /etc/apt/sources.list && apt-get update && apt-get install -y libssl1.1 python3.8 python3.8-venv python3.8-dev && python3.8 -m venv venv38 && source venv38/bin/activate && pip install 'Twisted==20.3.0' 'pyOpenSSL==19.1.0' 'cryptography==3.2.1' 'lxml==4.6.3' 'parsel==1.6.0' pytest && pip install -r requirements-py3.txt && echo './venv38/bin/pytest tests -v' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
python3.8 -m venv venv38 && source venv38/bin/activate && pip install -r requirements-py3.txt && pip install 'Twisted==21.7.0' 'pyOpenSSL==21.0.0' 'cryptography==3.4.8' && pip install trial && echo './venv38/bin/trial tests' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
python3.8 -m venv venv38 && source venv38/bin/activate && pip install -r requirements-py3.txt && pip install 'Twisted==21.7.0' 'pyOpenSSL==21.0.0' 'cryptography==3.4.8' && echo 'python -m twisted.trial tests' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
source venv38/bin/activate && pip install testfixtures && bash test_commands.sh
###ACTION_DELIMITER###
source venv38/bin/activate && pip install -e . && pip install -r requirements-py3.txt && bash test_commands.sh
###ACTION_DELIMITER###
source venv38/bin/activate && pip install -r tests/requirements.txt && python setup.py test
###ACTION_DELIMITER###
echo 'source venv38/bin/activate && python -m twisted.trial tests' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
source venv38/bin/activate && pip install pytest-twisted && pytest tests -v
###ACTION_DELIMITER###
source venv38/bin/activate && pip install Pillow testfixtures && echo 'source venv38/bin/activate && pytest tests -v' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
source venv38/bin/activate && pytest tests -v

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
source venv38/bin/activate && pytest tests -v

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
source venv38/bin/activate && pytest tests -v

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
RUN git clone https://github.com/scrapy/scrapy.git /home/scrapy

WORKDIR /home/scrapy
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("scrapy", "scrapy_3722_to_3377")
class SCRAPY_3722_TO_3377(Instance):
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
        # Regex patterns to match test cases and their statuses
        # Pattern for passed tests: e.g., "tests/test_closespider.py::TestCloseSpider::test_closespider_errorcount PASSED [  0%]"
        passed_pattern = re.compile(r'^(tests/.*?)\s+PASSED\s+\[\s*\d+%\s*\]$', re.MULTILINE)
        # Pattern for failed tests: e.g., "FAILED tests/test_squeues.py::ChunkSize2MarshalFifoDiskQueueTest::test_peek_one_element"
        failed_pattern = re.compile(r'^FAILED\s+(tests/.*?)(?:\s+-.*)?$', re.MULTILINE)
        # Pattern for skipped tests: e.g., "tests/test_xyz.py::TestXYZ::test_1 SKIPPED [  0%]" or "SKIPPED tests/test_xyz.py::TestXYZ::test_1"
        skipped_pattern = re.compile(r'^(tests/.*?)\s+SKIPPED\s+\[\s*\d+%\s*\]$|^SKIPPED\s+(tests/.*?)$', re.MULTILINE)
        # Extract passed tests
        passed_tests.update(passed_pattern.findall(log))
        # Extract failed tests
        failed_tests.update(failed_pattern.findall(log))
        # Extract skipped tests
        for match in skipped_pattern.finditer(log):
            test_name = match.group(1) or match.group(2)
            if test_name:
                skipped_tests.add(test_name.strip())
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
