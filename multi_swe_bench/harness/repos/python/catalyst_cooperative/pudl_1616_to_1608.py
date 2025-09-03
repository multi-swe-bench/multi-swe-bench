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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y build-essential libpq-dev python3-dev
###ACTION_DELIMITER###
pip install -e .[test]
###ACTION_DELIMITER###
grep -r '5534788' src/pudl/workspace/
###ACTION_DELIMITER###
sed -i 's/10.5281\/zenodo.5534788/10.5281\/zenodo.764696/' src/pudl/workspace/datastore.py
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider test/unit test/integration test/validate' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip list | grep datasette
###ACTION_DELIMITER###
pip install datasette
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pudl datastore
###ACTION_DELIMITER###
pip list | grep pudl
###ACTION_DELIMITER###
python -m pudl datastore
###ACTION_DELIMITER###
python -m pudl datastore update --settings-file src/pudl/package_data/settings/ferc1_solo_test.yml
###ACTION_DELIMITER###
python -m pudl datastore src/pudl/package_data/settings/ferc1_solo_test.yml
###ACTION_DELIMITER###
python -m pudl --help
###ACTION_DELIMITER###
python -m pudl.setup --help
###ACTION_DELIMITER###
python -m pudl src/pudl/package_data/settings/ferc1_solo_test.yml --clobber
###ACTION_DELIMITER###
mkdir -p pudl_in pudl_out && export PUDL_IN=$(pwd)/pudl_in && export PUDL_OUT=$(pwd)/pudl_out
###ACTION_DELIMITER###
python -m pudl src/pudl/package_data/settings/ferc1_solo_test.yml --clobber
###ACTION_DELIMITER###
mkdir -p $PUDL_OUT/sqlite && echo $PUDL_IN && echo $PUDL_OUT
###ACTION_DELIMITER###
ls -ld $PUDL_OUT $PUDL_OUT/sqlite && echo $PUDL_IN $PUDL_OUT
###ACTION_DELIMITER###
python -m pudl src/pudl/package_data/settings/ferc1_solo_test.yml --clobber --logfile etl_debug.log
###ACTION_DELIMITER###
python -m pudl.datastore update --settings-file src/pudl/package_data/settings/ferc1_solo_test.yml
###ACTION_DELIMITER###
python -m pudl.workspace.datastore update --settings-file src/pudl/package_data/settings/ferc1_solo_test.yml
###ACTION_DELIMITER###
python -m pudl.workspace.datastore --dataset ferc1 --pudl_in $PUDL_IN
###ACTION_DELIMITER###
sed -i 's/10.5281\/zenodo.764696/10.5281\/zenodo.5534788/' src/pudl/workspace/datastore.py
###ACTION_DELIMITER###
sed -i 's/deposit\/depositions/api\/records/' src/pudl/workspace/datastore.py
###ACTION_DELIMITER###
python -m pudl.workspace.datastore --dataset ferc1 --pudl_in $PUDL_IN
###ACTION_DELIMITER###
sed -i 's/api\/api\/records/api\/records/' src/pudl/workspace/datastore.py
###ACTION_DELIMITER###
sed -i 's/deposit\/depositions/records/' src/pudl/workspace/datastore.py
###ACTION_DELIMITER###
sed -i 's/api\/api\/records/api\/records/' src/pudl/workspace/datastore.py
###ACTION_DELIMITER###
sed -i 's/zenodo\.org\/api\/api\/records/zenodo\.org\/api\/records/' src/pudl/workspace/datastore.py
###ACTION_DELIMITER###
python -m pudl.workspace.datastore --dataset ferc1 --pudl_in $PUDL_IN
###ACTION_DELIMITER###
sed -i 's|https://zenodo.org/api/|https://zenodo.org/|g' src/pudl/workspace/datastore.py
###ACTION_DELIMITER###
sed -i 's|api/api/records|api/records|g' src/pudl/workspace/datastore.py
###ACTION_DELIMITER###
sed -i 's|https://zenodo.org/api/api/records|https://zenodo.org/api/records|g' src/pudl/workspace/datastore.py
###ACTION_DELIMITER###
sed -i 's|deposit/depositions|records|g' src/pudl/workspace/datastore.py
###ACTION_DELIMITER###
sed -i 's/10.5281\/zenodo.5534788/10.5281\/zenodo.764696/' src/pudl/workspace/datastore.py
###ACTION_DELIMITER###
sed -i 's|https://zenodo.org/api/api/records|https://zenodo.org/api/records|g' src/pudl/workspace/datastore.py && python -m pudl.workspace.datastore --dataset ferc1 --pudl_in $PUDL_IN
###ACTION_DELIMITER###
sed -i 's|10.5281/zenodo\.|https://zenodo.org/api/records/|g' src/pudl/workspace/datastore.py && python -m pudl.workspace.datastore --dataset ferc1 --pudl_in $PUDL_IN
###ACTION_DELIMITER###
sed -i 's|https://zenodo.org/api/records/764696|10.5281/zenodo.764696|g' src/pudl/workspace/datastore.py && python -m pudl.workspace.datastore --dataset ferc1 --pudl_in $PUDL_IN
###ACTION_DELIMITER###
sed -i 's|10.5281/zenodo.|https://zenodo.org/api/records/|g' src/pudl/workspace/datastore.py && python -m pudl.workspace.datastore --dataset ferc1 --pudl_in $PUDL_IN
###ACTION_DELIMITER###
sed -i 's|https://zenodo.org/api/records/764696|10.5281/zenodo.764696|g' src/pudl/workspace/datastore.py && python -m pudl.workspace.datastore --dataset ferc1 --pudl_in $PUDL_IN
###ACTION_DELIMITER###
sed -i 's|10.5281/zenodo\.|https://zenodo.org/api/records/|g' src/pudl/workspace/datastore.py && python -m pudl.workspace.datastore --dataset ferc1 --pudl_in $PUDL_IN
###ACTION_DELIMITER###
sed -i 's|10.5281/zenodo\.764696|10.5281/zenodo.764696|g' src/pudl/workspace/datastore.py && sed -i 's|deposit/depositions|records|g' src/pudl/workspace/datastore.py && python -m pudl.workspace.datastore --dataset ferc1 --pudl_in $PUDL_IN
###ACTION_DELIMITER###
sed -i 's|https://zenodo.org/api/records/764696|10.5281/zenodo.764696|g' src/pudl/workspace/datastore.py && python -m pudl.workspace.datastore --dataset ferc1 --pudl_in $PUDL_IN
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v --no-header -rA --tb=no -p no:cacheprovider test/unit test/integration test/validate

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider test/unit test/integration test/validate

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider test/unit test/integration test/validate

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
RUN git clone https://github.com/catalyst-cooperative/pudl.git /home/pudl

WORKDIR /home/pudl
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("catalyst-cooperative", "pudl_1616_to_1608")
class PUDL_1616_TO_1608(Instance):
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
        # Regex patterns to match test names and statuses in both orders
        pattern_test_first = re.compile(r'^(?:\[\s*\d+\]\s+)?(?P<test_name>test/[^\s]+)\s+(?P<status>PASSED|FAILED|ERROR|SKIPPED|XFAIL)\b')
        pattern_status_first = re.compile(r'^(?:\[\s*\d+\]\s+)?(?P<status>PASSED|FAILED|ERROR|SKIPPED|XFAIL)\b\s+(?P<test_name>test/[^\s]+)')
        for line in log.splitlines():
            # Check for test name followed by status
            match = pattern_test_first.search(line)
            if match:
                test_name = match.group('test_name').strip()
                status = match.group('status')
            else:
                # Check for status followed by test name
                match = pattern_status_first.search(line)
                if not match:
                    continue
                test_name = match.group('test_name').strip()
                status = match.group('status')
            # Categorize the test based on status
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ('FAILED', 'ERROR'):
                failed_tests.add(test_name)
            elif status in ('SKIPPED', 'XFAIL'):
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
