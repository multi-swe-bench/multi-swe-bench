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
                """apt-get update && apt-get install -y build-essential libssl-dev libffi-dev libpq-dev python3-dev
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
grep 'session_secret' config/galaxy.yml
###ACTION_DELIMITER###
cp config/galaxy.yml.sample config/galaxy.yml
###ACTION_DELIMITER###
grep 'session_secret' config/galaxy.yml
###ACTION_DELIMITER###
grep -i 'secret' config/galaxy.yml
###ACTION_DELIMITER###
cp config/auth_conf.xml.sample config/auth_conf.xml
###ACTION_DELIMITER###
./manage_db.sh init
###ACTION_DELIMITER###
grep 'auth_config_file' config/galaxy.yml
###ACTION_DELIMITER###
sed -i 's/^#auth_config_file/auth_config_file/' config/galaxy.yml
###ACTION_DELIMITER###
echo 'GALAXY_CONFIG_FILE=config/galaxy.yml ./run_tests.sh -unit -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls -l tests
###ACTION_DELIMITER###
ls -l
###ACTION_DELIMITER###
ln -s test tests
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls -l test
###ACTION_DELIMITER###
ln -s ../test-data test/data
###ACTION_DELIMITER###
echo 'export PYTHONPATH=. && GALAXY_CONFIG_FILE=config/galaxy.yml ./run_tests.sh -unit -v' > test_commands.sh
###ACTION_DELIMITER###
touch test-data/__init__.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
touch test/__init__.py
###ACTION_DELIMITER###
cat run_tests.sh
###ACTION_DELIMITER###
echo 'GALAXY_CONFIG_FILE=config/galaxy.yml ./run_tests.sh -unit -v -- --rootdir=.' > test_commands.sh
###ACTION_DELIMITER###
echo 'GALAXY_CONFIG_FILE=config/galaxy.yml ./run_tests.sh -unit -v -- --rootdir=. --pythonpath=.' > test_commands.sh
###ACTION_DELIMITER###
echo "/home/galaxy" > .venv/lib/python3.9/site-packages/galaxy.pth
###ACTION_DELIMITER###
bash -c 'source .venv/bin/activate; python -c "import tests.data; print(\"Success\")"'
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget unzip
###ACTION_DELIMITER###
echo 'export PYTHONPATH=. && GALAXY_CONFIG_FILE=config/galaxy.yml ./scripts/update_cwl_conformance_tests.sh && ./run_tests.sh -unit -v -- --rootdir=.' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'export PYTHONPATH=. && pytest -v test/unit --html=run_unit_tests.html --self-contained-html' > test_commands.sh
###ACTION_DELIMITER###
cat pytest.ini
###ACTION_DELIMITER###
sed -i 's/pythonpath = lib/pythonpath = lib ./' pytest.ini
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'source .venv/bin/activate && export PYTHONPATH=. && pytest -v test/unit --html=run_unit_tests.html --self-contained-html' > test_commands.sh
###ACTION_DELIMITER###
echo 'source .venv/bin/activate && pip install pytest && export PYTHONPATH=. && pytest -v test/unit --html=run_unit_tests.html --self-contained-html' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
source .venv/bin/activate && pip install pytest && export PYTHONPATH=. && pytest -v test/unit --html=run_unit_tests.html --self-contained-html

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
source .venv/bin/activate && pip install pytest && export PYTHONPATH=. && pytest -v test/unit --html=run_unit_tests.html --self-contained-html

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
source .venv/bin/activate && pip install pytest && export PYTHONPATH=. && pytest -v test/unit --html=run_unit_tests.html --self-contained-html

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
RUN git clone https://github.com/galaxyproject/galaxy.git /home/galaxy

WORKDIR /home/galaxy
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("galaxyproject", "galaxy_18068_to_17411")
class GALAXY_18068_TO_17411(Instance):
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
        test_pattern = re.compile(r'(?:(test/[^\s]+)\s+(PASSED|FAILED|SKIPPED)|(PASSED|FAILED|SKIPPED)\s+(test/[^\s]+))', re.MULTILINE)
        for match in test_pattern.finditer(log):
            test_name = match.group(1)
            status = match.group(2)
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
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
