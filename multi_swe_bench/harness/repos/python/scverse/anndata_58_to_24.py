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
        repo_name = self.pr.repo
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
                """ls -l
###ACTION_DELIMITER###
cat requires.txt
###ACTION_DELIMITER###
cat requires_tests.txt
###ACTION_DELIMITER###
cat pytest.ini
###ACTION_DELIMITER###
ls anndata
###ACTION_DELIMITER###
ls anndata/tests
###ACTION_DELIMITER###
cat anndata/tests/base.py
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
sed -i 's/sklearn/scikit-learn/' requires_tests.txt
###ACTION_DELIMITER###
pip install -r requires_tests.txt
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/--tb=no//' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y pandas && pip install pandas==0.21.0
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip install pandas==0.21.0
###ACTION_DELIMITER###
apt-get install -y libopenblas-dev liblapack-dev && pip install numpy==1.19.5 && pip install pandas==0.21.0
###ACTION_DELIMITER###
CFLAGS="-Wno-stringop-overflow" pip install numpy==1.19.5 && pip install pandas==0.21.0
###ACTION_DELIMITER###
sed -i 's/from pandas.core.index import RangeIndex/from pandas import RangeIndex/' anndata/base.py
###ACTION_DELIMITER###

###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from pandas import RangeIndex/from pandas.core.indexes.range import RangeIndex/' anndata/base.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y pandas && pip install pandas==0.23.4
###ACTION_DELIMITER###
pip install Cython && pip install pandas==0.23.4
###ACTION_DELIMITER###
pip install pandas==1.1.5 && sed -i 's/from pandas.core.index import RangeIndex/from pandas.core.indexes.range import RangeIndex/' anndata/base.py && bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.22.4 pandas==1.1.5 && sed -i 's/from pandas.core.index import RangeIndex/from pandas.core.indexes.range import RangeIndex/' anndata/base.py && bash test_commands.sh
###ACTION_DELIMITER###
pip install scipy==1.2.3 && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y gfortran && pip install scipy==1.2.3 && bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.19.5 pandas==1.1.5 scipy==1.5.4 && sed -i 's/from pandas.core.index import RangeIndex/from pandas.core.indexes.range import RangeIndex/' anndata/base.py && bash test_commands.sh
###ACTION_DELIMITER###
pip install scipy==1.2.3 && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from scipy.sparse.sputils import IndexMixin/from scipy.sparse.base import IndexMixin/' anndata/base.py && pip install scipy==1.5.4 && bash test_commands.sh
###ACTION_DELIMITER###
pip install scipy==1.2.3 && grep -r 'class IndexMixin' /usr/local/lib/python3.9/site-packages/scipy/sparse/ && sed -i 's/from scipy.sparse.base import IndexMixin/from scipy.sparse.sputils import IndexMixin/' anndata/base.py && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libopenblas-dev liblapack-dev && pip install scipy==1.2.3 && sed -i 's/from scipy.sparse.base import IndexMixin/from scipy.sparse.sputils import IndexMixin/' anndata/base.py && bash test_commands.sh
###ACTION_DELIMITER###
grep -r 'class IndexMixin' /usr/local/lib/python3.9/site-packages/scipy/sparse/ && sed -i 's/from scipy.sparse.base import IndexMixin/from scipy.sparse._sputils import IndexMixin/' anndata/base.py && pip install scipy==1.5.4 && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from scipy.sparse._sputils import IndexMixin/from scipy.sparse._index import IndexMixin/' anndata/base.py && bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.20.0 && sed -i 's/from scipy.sparse.sputils import IndexMixin/from scipy.sparse._index import IndexMixin/' anndata/h5py/h5sparse.py && bash test_commands.sh
###ACTION_DELIMITER###
pip install numba==0.55.1 scipy==1.7.3 && bash test_commands.sh
###ACTION_DELIMITER###
pip install pandas==0.23.4 h5py==2.10.0 && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libhdf5-dev && pip install h5py==3.1.0 && bash test_commands.sh
###ACTION_DELIMITER###
pip install pandas==0.25.3 numpy==1.16.4 h5py==2.9.0 scipy==1.2.3 && bash test_commands.sh
###ACTION_DELIMITER###
pip install pandas==1.1.5 numpy==1.20.0 scipy==1.5.4 h5py==3.1.0 numba==0.55.1 && sed -i 's/from pandas.core.index import RangeIndex/from pandas.core.indexes.range import RangeIndex/' anndata/base.py && sed -i 's/from scipy.sparse.sputils import IndexMixin/from scipy.sparse._index import IndexMixin/' anndata/h5py/h5sparse.py && bash test_commands.sh
###ACTION_DELIMITER###
pip install pandas==1.0.5 h5py==2.10.0 && bash test_commands.sh
###ACTION_DELIMITER###
pip install cython==0.29.21 && pip install pandas==1.0.5 numpy==1.16.4 scipy==1.2.3 h5py==2.10.0 numba==0.55.1 && sed -i 's/from pandas.core.index import RangeIndex/from pandas.core.indexes.range import RangeIndex/' anndata/base.py && sed -i 's/from scipy.sparse.sputils import IndexMixin/from scipy.sparse._index import IndexMixin/' anndata/h5py/h5sparse.py && bash test_commands.sh
###ACTION_DELIMITER###
pip install setuptools==58.0.0 && pip install cython==0.29.21 pandas==0.25.3 numpy==1.16.4 scipy==1.2.3 h5py==2.10.0 numba==0.55.1 && sed -i 's/from pandas.core.index import RangeIndex/from pandas.core.indexes.range import RangeIndex/' anndata/base.py && sed -i 's/from scipy.sparse.sputils import IndexMixin/from scipy.sparse.sputils import IndexMixin/' anndata/h5py/h5sparse.py && echo 'pytest -v -rA --tb=short anndata/tests' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip install setuptools==58.0.0 && pip install cython==0.29.21 pandas==0.25.3 numpy==1.18.5 scipy==1.2.3 h5py==2.10.0 numba==0.55.1 && sed -i 's/from pandas.core.index import RangeIndex/from pandas.core.indexes.range import RangeIndex/' anndata/base.py && sed -i 's/from scipy.sparse.sputils import IndexMixin/from scipy.sparse.sputils import IndexMixin/' anndata/h5py/h5sparse.py && echo 'pytest -v -rA --tb=short anndata/tests' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential && pip install setuptools==59.0.1 && pip install cython==0.29.21 pandas==0.25.3 numpy==1.18.5 scipy==1.2.3 h5py==2.10.0 numba==0.55.1 && sed -i 's/from pandas.core.index import RangeIndex/from pandas.core.indexes.range import RangeIndex/' anndata/base.py && sed -i 's/from scipy.sparse.sputils import IndexMixin/from scipy.sparse.sputils import IndexMixin/' anndata/h5py/h5sparse.py && echo 'pytest -v -rA --tb=short anndata/tests' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential python3-dev python3-distutils && pip install --upgrade pip && pip install setuptools==59.0.1 cython==0.29.21 pandas==0.25.3 numpy==1.21.6 scipy==1.2.3 h5py==2.10.0 numba==0.55.1 && sed -i 's/from pandas.core.index import RangeIndex/from pandas.core.indexes.range import RangeIndex/' anndata/base.py && sed -i 's/from scipy.sparse.sputils import IndexMixin/from scipy.sparse.sputils import IndexMixin/' anndata/h5py/h5sparse.py && echo 'pytest -v -rA --tb=short anndata/tests' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v --no-header -rA  -p no:cacheprovider

""".replace("[[REPO_NAME]]", repo_name),
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
pytest -v --no-header -rA  -p no:cacheprovider

""".replace("[[REPO_NAME]]", repo_name),
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
pytest -v --no-header -rA  -p no:cacheprovider

""".replace("[[REPO_NAME]]", repo_name),
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
RUN git clone https://github.com/scverse/anndata.git /home/anndata

WORKDIR /home/anndata
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("scverse", "anndata_58_to_24")
class ANNDATA_58_TO_24(Instance):
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

        return "bash /home/run.sh"

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

        # Regex patterns to match test results
        pattern1 = re.compile(
            r"^\s*(.+?)\s+(PASSED|FAILED|SKIPPED|√|✗|OK|ERROR)(?::?\s+\[\s*\d+%\s*\])?$",
            re.MULTILINE | re.IGNORECASE,
        )  # Handles symbols, case, and colons
        pattern2 = re.compile(
            r"^\s*(FAILED|PASSED|SKIPPED|√|✗|OK|ERROR):?\s+(.+?)(?:\s+-\s.*)?$",
            re.MULTILINE | re.IGNORECASE,
        )  # Handles symbols, case, and colons
        # Process pattern1 matches (test name followed by status)
        for test_name, status in pattern1.findall(log):
            status_lower = status.lower()
            if status_lower in [
                "passed",
                "ok",
                "√",
            ]:  # Handle symbols and alternative keywords
                passed_tests.add(test_name)
            elif status_lower in ["failed", "error", "✗"]:
                failed_tests.add(test_name)
            elif status_lower == "skipped":
                skipped_tests.add(test_name)
        # Process pattern2 matches (status followed by test name)
        for status, test_name in pattern2.findall(log):
            status_lower = status.lower()
            if status_lower in [
                "passed",
                "ok",
                "√",
            ]:  # Handle symbols and alternative keywords
                passed_tests.add(test_name)
            elif status_lower in ["failed", "error", "✗"]:
                failed_tests.add(test_name)
            elif status_lower == "skipped":
                skipped_tests.add(test_name)
        parsed_results = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
        }

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
