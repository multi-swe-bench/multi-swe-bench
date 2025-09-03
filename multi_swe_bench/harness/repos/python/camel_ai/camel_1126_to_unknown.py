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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip python3-venv python3-distutils pandoc
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip python3-venv python3-dev pandoc
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
python3 -m venv camel-venv
###ACTION_DELIMITER###
source camel-venv/bin/activate
###ACTION_DELIMITER###
pip install poetry
###ACTION_DELIMITER###
poetry install --with dev
###ACTION_DELIMITER###
pip install --upgrade virtualenv
###ACTION_DELIMITER###
pip install virtualenv==20.32.0
###ACTION_DELIMITER###
pip install --upgrade packaging
###ACTION_DELIMITER###
poetry install --with dev
###ACTION_DELIMITER###
poetry add --dev virtualenv==20.32.0
###ACTION_DELIMITER###
echo 'pytest -v --strict-markers --tb=short -rA' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y python3-setuptools
###ACTION_DELIMITER###
pip install setuptools
###ACTION_DELIMITER###
export OPENAI_API_KEY='dummy_key_for_testing'
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install slack-sdk
###ACTION_DELIMITER###
pip install asknews-sdk
###ACTION_DELIMITER###
pip install asknews_sdk
###ACTION_DELIMITER###
grep -r 'asknews_sdk' . && cat README.md
###ACTION_DELIMITER###
echo 'pytest -v --strict-markers --tb=short -rA -k "not asknews"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'import sys
from unittest.mock import MagicMock
def pytest_configure():
    sys.modules["asknews_sdk"] = MagicMock()' > conftest.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install requests-oauthlib
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install sentence-transformers transformers torch wikipedia pygithub neo4j nebula3-python
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install unstructured
###ACTION_DELIMITER###
pip install 'unstructured[all]'
###ACTION_DELIMITER###
pip install --force-reinstall unstructured
###ACTION_DELIMITER###
echo -e 'import sys\nfrom unittest.mock import MagicMock\ndef pytest_configure():\n    sys.modules["asknews_sdk"] = MagicMock()\n    sys.modules["unstructured.documents.elements"] = MagicMock()' > conftest.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install openai==0.28.1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'import sys\nfrom unittest.mock import MagicMock, patch\nfrom openai import OpenAI\n\ndef pytest_configure():\n    sys.modules["asknews_sdk"] = MagicMock()\n    sys.modules["unstructured.documents.elements"] = MagicMock()\n    \n    class MockOpenAI(OpenAI):\n        def __init__(self, *args, **kwargs):\n            kwargs.pop("proxies", None)\n            super().__init__(*args, **kwargs)\n    \n    patch("camel.models.openai_model.OpenAI", MockOpenAI).start()' > conftest.py
###ACTION_DELIMITER###
pip install --upgrade openai && bash test_commands.sh
###ACTION_DELIMITER###
pip install datacommons scholarly notion-client duckduckgo-search wolframalpha"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v --strict-markers --tb=short -rA -k "not asknews"

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
pytest -v --strict-markers --tb=short -rA -k "not asknews"

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
pytest -v --strict-markers --tb=short -rA -k "not asknews"

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
RUN git clone https://github.com/camel-ai/camel.git /home/camel

WORKDIR /home/camel
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("camel-ai", "camel_1126_to_unknown")
class CAMEL_1126_TO_UNKNOWN(Instance):
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
        passed_tests: set[str] = set()
        failed_tests: set[str] = set()
        skipped_tests: set[str] = set()
        import re
        # Implement the log parsing logic here
        # Regex pattern to match test names and their statuses
        # Regex matches both 'test_name STATUS [percent]' and 'STATUS test_name [percent]' (percent optional)
        pattern = re.compile(r'^(?:(.+\.py::(?:[\w]+::)*test_[\w:-]+)\s+(PASSED|FAILED|SKIPPED)|(PASSED|FAILED|SKIPPED)\s+(.+\.py::(?:[\w]+::)*test_[\w:-]+))(?:\s+\[\s*\d+%\s*\])?$')
        for line in log.splitlines():
            match = pattern.search(line)
            if match:
                # Extract test name and status from the correct groups
                if match.group(1) and match.group(2):
                    test_name = match.group(1).strip()
                    status = match.group(2).strip()
                elif match.group(3) and match.group(4):
                    test_name = match.group(4).strip()
                    status = match.group(3).strip()
                else:
                    continue  # No valid groups matched
                # Categorize the test based on status
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
