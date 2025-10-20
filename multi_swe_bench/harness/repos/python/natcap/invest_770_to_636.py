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
                """wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && bash miniconda.sh -b -p /opt/conda && rm miniconda.sh && echo 'export PATH="/opt/conda/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && bash miniconda.sh -b -p /opt/conda && rm miniconda.sh && echo 'export PATH="/opt/conda/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
###ACTION_DELIMITER###
source ~/.bashrc
###ACTION_DELIMITER###
apt-get install -y zip pandoc
###ACTION_DELIMITER###
apt-get install -y git-lfs
###ACTION_DELIMITER###
make env
###ACTION_DELIMITER###
apt-get install -y make
###ACTION_DELIMITER###
make env
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
###ACTION_DELIMITER###
pip install Cython requests
###ACTION_DELIMITER###
make env
###ACTION_DELIMITER###
pip install numpy
###ACTION_DELIMITER###
make env
###ACTION_DELIMITER###
source ./env/bin/activate
###ACTION_DELIMITER###
ls -l ./env
###ACTION_DELIMITER###
ls -l ./env/bin
###ACTION_DELIMITER###
conda activate ./env
###ACTION_DELIMITER###
conda init && source ~/.bashrc
###ACTION_DELIMITER###
conda activate ./env
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install Cython==0.29.36
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip uninstall -y numpy && conda install -y numpy=1.24.4
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
export CFLAGS="-I$(python -c 'import numpy; print(numpy.get_include())')" && pip install -e .
###ACTION_DELIMITER###
conda activate ./env && conda install -y numpy=1.24.4 && export CFLAGS="-I$(python -c 'import numpy; print(numpy.get_include())')" && pip install -e .
###ACTION_DELIMITER###
conda config --add channels conda-forge && conda config --set channel_priority strict && conda install -y numpy=1.24.4 && export CFLAGS="-I$(python -c 'import numpy; print(numpy.get_include())')" && pip install -e .
###ACTION_DELIMITER###
export CFLAGS="-I$(python -c 'import numpy; print(numpy.get_include())')" && pip install pygeoprocessing>=2.3.2 && pip install -e .
###ACTION_DELIMITER###
export CFLAGS="-I$(python -c 'import numpy; print(numpy.get_include())')" && pip install --no-build-isolation pygeoprocessing==2.4.9 && pip install -e .
###ACTION_DELIMITER###
export CFLAGS="-I$(python -c 'import numpy; print(numpy.get_include())')" && pip install 'pygeoprocessing>=2.3.2' --no-build-isolation
###ACTION_DELIMITER###
conda install -c conda-forge -y 'pygeoprocessing>=2.3.2' && pip install -e .
###ACTION_DELIMITER###
apt-get update && apt-get install -y g++ && pip install -e .
###ACTION_DELIMITER###
conda activate ./env && make test
###ACTION_DELIMITER###
conda install -c conda-forge -y pyside2 && make test
###ACTION_DELIMITER###
conda install -c conda-forge -y qtpy && make test
###ACTION_DELIMITER###
rm -f /home/invest/env/lib/python3.8/site-packages/natcap_invest-3.9.2.post755+g27b302ebf-nspkg.pth && pip install -e . && make test
###ACTION_DELIMITER###
apt-get install -y libgl1-mesa-glx xvfb && xvfb-run make test
###ACTION_DELIMITER###
conda install -c conda-forge -y qtawesome && xvfb-run make test
###ACTION_DELIMITER###
pip install --force-reinstall -e . && xvfb-run make test
###ACTION_DELIMITER###
conda install -c conda-forge -y 'setuptools<70.0.0' && rm -f /home/invest/env/lib/python3.8/site-packages/natcap_invest-3.9.2.post755+g27b302ebf-nspkg.pth && pip install --force-reinstall -e . && xvfb-run make test
###ACTION_DELIMITER###
apt-get install -y libgdal-dev gdal-bin && pip install GDAL==3.6.2 && rm -f /home/invest/env/lib/python3.8/site-packages/natcap_invest-3.9.2.post755+g27b302ebf-nspkg.pth && pip install --force-reinstall --no-deps -e . && xvfb-run make test
###ACTION_DELIMITER###
conda install -c conda-forge -y setuptools-scm && pip install -e . && xvfb-run make test
###ACTION_DELIMITER###
echo -e '#!/bin/bash
xvfb-run make test' > /home/invest/test_commands.sh && chmod +x /home/invest/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
xvfb-run make test

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
#!/bin/bash
xvfb-run make test

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
#!/bin/bash
xvfb-run make test

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
RUN git clone https://github.com/natcap/invest.git /home/invest

WORKDIR /home/invest
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("natcap", "invest_770_to_636")
class INVEST_770_TO_636(Instance):
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
        # Split the log into lines and process each line
        # Regex patterns to match different test result formats
        test_patterns = [
            # Format 1: [line number] STATUS test_name (strict test name format)
            re.compile(r'\[\d+\]\s+(PASSED|PASS|OK|SUCCESS|FAILED|FAIL|ERROR|SKIPPED|SKIP)\W*\s+(tests/[\w/]+\.py::[\w:]+)'),
            # Format 2: STATUS test_name (strict test name format)
            re.compile(r'(PASSED|PASS|OK|SUCCESS|FAILED|FAIL|ERROR|SKIPPED|SKIP)\W*\s+(tests/[\w/]+\.py::[\w:]+)'),
            # Format 3: test_name ... STATUS (strict test name format)
            re.compile(r'(tests/[\w/]+\.py::[\w:]+).*\s+(PASSED|PASS|OK|SUCCESS|FAILED|FAIL|ERROR|SKIPPED|SKIP)\b')
        ]
        for line in log.splitlines():
            line = line.strip()
            for pattern in test_patterns:
                match = pattern.search(line)
                if match:
                    # Extract status and test name based on the matched pattern
                    if pattern == test_patterns[0]:
                        status, test_name = match.group(1), match.group(2)
                    elif pattern == test_patterns[1]:
                        status, test_name = match.group(1), match.group(2)
                    else:
                        test_name, status = match.group(1), match.group(2)
                    # Clean and categorize the test
                    test_name = test_name.strip()
                    status = status.strip().upper()
                    # Map status variations to categories
                    if status in ['PASSED', 'PASS', 'OK', 'SUCCESS']:
                        passed_tests.add(test_name)
                    elif status in ['FAILED', 'FAIL', 'ERROR']:
                        failed_tests.add(test_name)
                    elif status in ['SKIPPED', 'SKIP']:
                        skipped_tests.add(test_name)
                    break  # Stop checking other patterns once matched
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
