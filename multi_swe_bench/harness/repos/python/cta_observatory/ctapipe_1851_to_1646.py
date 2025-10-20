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
                """ls
###ACTION_DELIMITER###
cat Makefile
###ACTION_DELIMITER###
conda env create -f environment.yml
###ACTION_DELIMITER###
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
###ACTION_DELIMITER###
bash Miniconda3-latest-Linux-x86_64.sh -b
###ACTION_DELIMITER###
export PATH=/root/miniconda3/bin:$PATH
###ACTION_DELIMITER###
conda env create -f environment.yml
###ACTION_DELIMITER###
conda install -n base -c conda-forge mamba -y
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
###ACTION_DELIMITER###
conda install -n base -c conda-forge mamba -y
###ACTION_DELIMITER###
mamba env create -f environment.yml
###ACTION_DELIMITER###
mamba create -n cta-dev python=3.7 -y
###ACTION_DELIMITER###
mamba activate cta-dev
###ACTION_DELIMITER###
eval "$(mamba shell hook --shell bash)"
###ACTION_DELIMITER###
mamba activate cta-dev
###ACTION_DELIMITER###
mamba env update -f environment.yml
###ACTION_DELIMITER###
mamba install -c defaults -c cta-observatory python=3.7 pip astropy black bokeh=1 conda-forge::nbsphinx cython graphviz h5py iminuit>=2 ipython ipywidgets joblib jupyter matplotlib numba numpy>=1.17 numpydoc pandas pre-commit psutil pytables pytest pytest-cov pytest-runner pyyaml scikit-learn scipy setuptools sphinx=3.5 sphinx-automodapi sphinx_rtd_theme tqdm traitlets vitables wheel xz zlib zstandard conda-forge::eventio>=1.5.0 conda-forge::corsikaio -y
###ACTION_DELIMITER###
pip install -e .[tests]
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install jinja2==2.11.3
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install markupsafe==1.1.1
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
echo 'pytest -v' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v

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
pytest -v

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
pytest -v

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
RUN git clone https://github.com/cta-observatory/ctapipe.git /home/ctapipe

WORKDIR /home/ctapipe
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("cta-observatory", "ctapipe_1851_to_1646")
class CTAPIPE_1851_TO_1646(Instance):
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
        passed_tests = set[str]() # Tests that passed successfully
        failed_tests = set[str]() # Tests that failed
        skipped_tests = set[str]() # Tests that were skipped
        import re
        # Regex patterns to match test cases and their statuses
        test_line_pattern = re.compile(
        r'((?:\w+/)*tests/[\w/]+\.py::\w+(?:\[\w+\])?) '
        r'(PASSED|FAILED|SKIPPED|XFAIL) '
        r'\[\s*\d+%\]'
    )
        summary_pattern = re.compile(
        r'(PASSED|FAILED|SKIPPED|XFAIL) '
        r'((?:\w+/)*tests/[\w/]+\.py::\w+(?:\[\w+\])?)'
    )
        # Parse individual test lines
        for match in test_line_pattern.finditer(log):
            test_name = match.group(1).strip()
            status = match.group(2)
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
            elif status == 'XFAIL':
                skipped_tests.add(test_name)
        # Parse summary lines (e.g., 'FAILED test_name')
        for match in summary_pattern.finditer(log):
            status = match.group(1)
            test_name = match.group(2).strip()
            if status == 'PASSED' and test_name not in passed_tests:
                passed_tests.add(test_name)
            elif status == 'FAILED' and test_name not in failed_tests:
                failed_tests.add(test_name)
            elif status == 'SKIPPED' and test_name not in skipped_tests:
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
