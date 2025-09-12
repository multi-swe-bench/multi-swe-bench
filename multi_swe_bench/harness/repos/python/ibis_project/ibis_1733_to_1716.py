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
                """cat README.md
###ACTION_DELIMITER###
ls
###ACTION_DELIMITER###
cat Makefile
###ACTION_DELIMITER###
cat requirements.txt
###ACTION_DELIMITER###
make develop
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make develop
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip python3-dev python-is-python3
###ACTION_DELIMITER###
make develop
###ACTION_DELIMITER###
sed -i 's/SafeConfigParser/ConfigParser/g' versioneer.py
###ACTION_DELIMITER###
make develop
###ACTION_DELIMITER###
sed -i 's/readfp/read_file/g' versioneer.py
###ACTION_DELIMITER###
make develop
###ACTION_DELIMITER###
pip install pre-commit
###ACTION_DELIMITER###
pip install pre-commit --break-system-packages
###ACTION_DELIMITER###
make develop
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
cat ci/test.sh
###ACTION_DELIMITER###
pip install pytest --break-system-packages && pytest -v --doctest-modules --doctest-ignore-import-errors
###ACTION_DELIMITER###
find ibis/ -type f -name '*.py' -exec sed -i 's/from collections import Iterable/from collections.abc import Iterable/g' {} +
###ACTION_DELIMITER###
pytest -v --doctest-modules --doctest-ignore-import-errors
###ACTION_DELIMITER###
grep -r 'from collections import.*Iterable' ibis/
###ACTION_DELIMITER###
sed -i 's/from collections import deque, Iterable/from collections import deque; from collections.abc import Iterable/' ibis/expr/lineage.py
###ACTION_DELIMITER###
pytest -v --doctest-modules --doctest-ignore-import-errors
###ACTION_DELIMITER###
sed -i 's/from pandas.core.tools.datetimes import to_time, to_datetime/from pandas.core.tools.datetimes import to_datetime/' ibis/compat.py && sed -i 's/from pandas.tseries.tools import to_time, to_datetime/from pandas.core.tools.datetimes import to_datetime/' ibis/compat.py
###ACTION_DELIMITER###
pytest -v --doctest-modules --doctest-ignore-import-errors
###ACTION_DELIMITER###
sed -i 's/from ibis.compat import to_time, to_date/from ibis.compat import to_date/' ibis/expr/api.py
###ACTION_DELIMITER###
pytest -v --doctest-modules --doctest-ignore-import-errors
###ACTION_DELIMITER###
grep -r 'collections.Mapping' ibis/ && grep -r 'from collections import Mapping' ibis/
###ACTION_DELIMITER###
find ibis/ -type f -name '*.py' -exec sed -i 's/collections.Mapping/collections.abc.Mapping/g' {} +
###ACTION_DELIMITER###
pytest -v --doctest-modules --doctest-ignore-import-errors
###ACTION_DELIMITER###
grep -r 'import pandas.util.testing' ibis/
###ACTION_DELIMITER###
find ibis/ -type f -name '*.py' -exec sed -i 's/pandas.util.testing/pandas.testing/g' {} +
###ACTION_DELIMITER###
pytest -v --doctest-modules --doctest-ignore-import-errors
###ACTION_DELIMITER###
find ibis/ -type f -name '*.py' -exec sed -i 's/from pandas.util import testing as tm/import pandas.testing as tm/g' {} +
###ACTION_DELIMITER###
find ibis/ -type f -name '*.py' -exec sed -i 's/collections.Sequence/collections.abc.Sequence/g' {} +
###ACTION_DELIMITER###
pytest -v --doctest-modules --doctest-ignore-import-errors
###ACTION_DELIMITER###
grep -r 'iteritems()' ibis/
###ACTION_DELIMITER###
sed -i 's/iteritems()/items()/g' ibis/pandas/client.py
###ACTION_DELIMITER###
pytest -v --doctest-modules --doctest-ignore-import-errors
###ACTION_DELIMITER###
grep -r 'from collections import.*Iterable' ibis/ && grep -r 'collections.Iterable' ibis/
###ACTION_DELIMITER###
find ibis/ -type f -name '*.py' -exec sed -i 's/collections.Iterable/collections.abc.Iterable/g' {} +
###ACTION_DELIMITER###
pytest -v --doctest-modules --doctest-ignore-import-errors
###ACTION_DELIMITER###
echo 'pytest -v --doctest-modules --doctest-ignore-import-errors' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v --doctest-modules --doctest-ignore-import-errors

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
pytest -v --doctest-modules --doctest-ignore-import-errors

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
pytest -v --doctest-modules --doctest-ignore-import-errors

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
RUN git clone https://github.com/ibis-project/ibis.git /home/ibis

WORKDIR /home/ibis
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ibis-project", "ibis_1733_to_1716")
class IBIS_1733_TO_1716(Instance):
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
        import json
        # Regular expression pattern to match test names and their statuses
        pattern = re.compile(
            r'(ibis/[\w/:.\[\]-]+)\s+(PASSED|FAILED|SKIPPED)|'
            r'(PASSED|FAILED|SKIPPED)\s+(ibis/[\w/:.\[\]-]+)'
        )
        # Find all matches in the log content
        matches = pattern.findall(log)
        for match in matches:
            # Check if the first part of the pattern matched (test name followed by status)
            if match[0] and match[1]:
                test_name = match[0]
                status = match[1]
            # Check if the second part of the pattern matched (status followed by test name)
            elif match[2] and match[3]:
                test_name = match[3]
                status = match[2]
            else:
                continue  # skip invalid matches
            # Add the test name to the appropriate set
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
