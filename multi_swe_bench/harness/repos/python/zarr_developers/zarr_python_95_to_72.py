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
                """git submodule status
###ACTION_DELIMITER###
ls -l tox.ini
###ACTION_DELIMITER###
git submodule update --init
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
pip install -r requirements_test.txt
###ACTION_DELIMITER###
pip install pytest pytest-cov
###ACTION_DELIMITER###
echo -e 'python setup.py build_ext --inplace
pytest -v --cov=zarr --cov-fail-under=100 --doctest-modules zarr
python -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from collections import MutableMapping/from collections.abc import MutableMapping/' zarr/storage.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/np.PINF/np.inf/g; s/np.NINF/-np.inf/g' zarr/meta.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from collections import MutableMapping/from collections.abc import MutableMapping/' zarr/attrs.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from collections import MutableMapping/from collections.abc import MutableMapping/' zarr/hierarchy.py
###ACTION_DELIMITER###
sed -i 's/python -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs\/tutorial.rst docs\/spec\/v2.rst/python -c "import zarr; import doctest; doctest.testfile(\"docs/tutorial.rst\", optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS); doctest.testfile(\"docs/spec/v2.rst\", optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)"/' test_commands.sh
###ACTION_DELIMITER###
sed -i 's|python -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst|python -c "import zarr; import doctest; doctest.testfile(\"docs/tutorial.rst\", optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS); doctest.testfile(\"docs/spec/v2.rst\", optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)"|' test_commands.sh
###ACTION_DELIMITER###
sed -i 's#python -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst#python -c "import zarr; import doctest; doctest.testfile(\"docs/tutorial.rst\", optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS); doctest.testfile(\"docs/spec/v2.rst\", optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)"#g' test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
sed -i 's/"docs\/tutorial.rst"/\\"docs\/tutorial.rst\\"/g; s/"docs\/spec\/v2.rst"/\\"docs\/spec\/v2.rst\\"/g' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from collections import MutableMapping/from collections.abc import MutableMapping/' zarr/tests/test_core.py
###ACTION_DELIMITER###
sed -i 's/np.product/np.prod/g' zarr/util.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y liblzma-dev"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python setup.py build_ext --inplace
pytest -v --cov=zarr --cov-fail-under=100 --doctest-modules zarr
python -c "import zarr; import doctest; doctest.testfile(\"docs/tutorial.rst\", optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS); doctest.testfile(\"docs/spec/v2.rst\", optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)"

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
python setup.py build_ext --inplace
pytest -v --cov=zarr --cov-fail-under=100 --doctest-modules zarr
python -c "import zarr; import doctest; doctest.testfile(\"docs/tutorial.rst\", optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS); doctest.testfile(\"docs/spec/v2.rst\", optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)"

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
python setup.py build_ext --inplace
pytest -v --cov=zarr --cov-fail-under=100 --doctest-modules zarr
python -c "import zarr; import doctest; doctest.testfile(\"docs/tutorial.rst\", optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS); doctest.testfile(\"docs/spec/v2.rst\", optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)"

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
RUN git clone https://github.com/zarr-developers/zarr-python.git /home/zarr-python

WORKDIR /home/zarr-python
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("zarr-developers", "zarr_python_95_to_72")
class ZARR_PYTHON_95_TO_72(Instance):
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
        # Regex patterns to match test lines
        # Pattern 1: Test name followed by status and percentage (e.g., "module::test PASSED [  0%]")
        pattern1 = re.compile(r'^([\w/.:]+)\s+(PASSED|FAILED|SKIPPED)\s+\[\s*\d+%\s*\]$')
        # Pattern 2: Status followed by test name (e.g., "FAILED module::test")
        pattern2 = re.compile(r'^(PASSED|FAILED|SKIPPED)\s+([\w/.:]+)$')
        for line in log.splitlines():
            line = line.strip()
            # Check for pattern 1 match
            match = pattern1.match(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
            else:
                # Check for pattern 2 match
                match = pattern2.match(line)
                if match:
                    status = match.group(1)
                    test_name = match.group(2)
                else:
                    continue  # No match, skip the line
            # Categorize the test based on status
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
