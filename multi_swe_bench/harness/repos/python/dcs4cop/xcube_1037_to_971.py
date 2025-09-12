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
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
###ACTION_DELIMITER###
bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda
###ACTION_DELIMITER###
source /opt/miniconda/etc/profile.d/conda.sh
###ACTION_DELIMITER###
conda env create -f environment.yml
###ACTION_DELIMITER###
conda install -n base -c conda-forge mamba --yes
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main --channel https://repo.anaconda.com/pkgs/r
###ACTION_DELIMITER###
conda install -n base -c conda-forge mamba --yes
###ACTION_DELIMITER###
mamba env create -f environment.yml
###ACTION_DELIMITER###
apt-get update && apt-get install -y gdal-bin libgdal-dev python3-dev build-essential
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install -e . GDAL==3.8.4
###ACTION_DELIMITER###
pip install flake8 moto pytest pytest-cov requests-mock werkzeug
###ACTION_DELIMITER###
pip install botocore==1.39.8
###ACTION_DELIMITER###
pip install boto3==1.39.8
###ACTION_DELIMITER###
echo -e '#!/bin/bash
source venv/bin/activate
pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install zarr==2.16.1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install 'moto[server]'
###ACTION_DELIMITER###
source venv/bin/activate && pip install pytest==7.4.0 tornado==6.3.3
###ACTION_DELIMITER###
source venv/bin/activate && pip freeze
###ACTION_DELIMITER###
echo -e '#!/bin/bash
source venv/bin/activate
pytest -v --no-header -rA -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pytest -v test/cli/test_benchmark.py --tb=long
###ACTION_DELIMITER###
source venv/bin/activate && pip install numcodecs==0.15.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install click==7.1.2
###ACTION_DELIMITER###
echo -e 'import pytest
from click.testing import CliRunner

class PatchedCliRunner(CliRunner):
    def __init__(self, *args, **kwargs):
        kwargs.pop("mix_stderr", None)
        super().__init__(*args, **kwargs)

@pytest.fixture(autouse=True)
def patch_cli_runner(monkeypatch):
    monkeypatch.setattr("click.testing.CliRunner", PatchedCliRunner)' > test/conftest.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install click==8.2.1
###ACTION_DELIMITER###
source venv/bin/activate && pip install --force-reinstall flask==3.1.1 moto[server]==5.1.9
###ACTION_DELIMITER###
source venv/bin/activate && pip install botocore==1.39.8 boto3==1.39.8
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
source venv/bin/activate
pytest -v --no-header -rA -p no:cacheprovider

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
source venv/bin/activate
pytest -v --no-header -rA -p no:cacheprovider

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
source venv/bin/activate
pytest -v --no-header -rA -p no:cacheprovider

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
RUN git clone https://github.com/dcs4cop/xcube.git /home/xcube

WORKDIR /home/xcube
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("dcs4cop", "xcube_1037_to_971")
class XCUBE_1037_TO_971(Instance):
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
        # Compile regex patterns to match test cases and their statuses
        # Adjusted patterns to account for leading line numbers in brackets
        # Adjusted patterns to match actual log content (excluding sample line numbers)
        passed_pattern = re.compile(r'(test/[^\s]+)\s+PASSED')
        failed_pattern = re.compile(r'FAILED\s+(test/[^\s]+)')
        skipped_pattern1 = re.compile(r'(test/[^\s]+)\s+SKIPPED')
        skipped_pattern2 = re.compile(r'SKIPPED\s+\[\d+\]\s+(test/[^\s]+)')
        for line in log.splitlines():
            line = line.strip()
            # Check for PASSED tests
            match = passed_pattern.search(line)
            if match:
                test_name = match.group(1).strip()
                passed_tests.add(test_name)
                continue
            # Check for FAILED tests
            match = failed_pattern.search(line)
            if match:
                test_name = match.group(1).strip()
                failed_tests.add(test_name)
                continue
            # Check for SKIPPED tests (format 1: test name first)
            match = skipped_pattern1.search(line)
            if match:
                test_name = match.group(1).strip()
                skipped_tests.add(test_name)
                continue
            # Check for SKIPPED tests (format 2: status first with [num])
            match = skipped_pattern2.search(line)
            if match:
                test_name = match.group(1).strip()
                skipped_tests.add(test_name)
                continue
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
