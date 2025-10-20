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
                """ls -la
###ACTION_DELIMITER###
cat install.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
###ACTION_DELIMITER###
bash Miniconda3-latest-Linux-x86_64.sh -b
###ACTION_DELIMITER###
source /root/miniconda3/bin/activate
###ACTION_DELIMITER###
source install.sh
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
###ACTION_DELIMITER###
source install.sh
###ACTION_DELIMITER###
pytest --version
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
echo -e '#!/bin/bash
python -m pytest --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
/root/miniconda3/envs/mantidimaging/bin/python -m pytest --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
conda activate mantidimaging && pytest -v
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgl1-mesa-glx
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
source /root/miniconda3/etc/profile.d/conda.sh
conda activate mantidimaging
python -m pytest --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y xvfb
###ACTION_DELIMITER###
echo -e '#!/bin/bash
source /root/miniconda3/etc/profile.d/conda.sh
conda activate mantidimaging
xvfb-run -a python -m pytest --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
conda run -n mantidimaging xvfb-run -a python -m pytest --collect-only -v
###ACTION_DELIMITER###
cat environment-dev.yml
###ACTION_DELIMITER###
conda env create -f environment-dev.yml
###ACTION_DELIMITER###
conda activate mantidimaging && pip install pytest==6.2.1 pytest-cov==2.10.1 coveralls==2.2.0 yapf==0.30.0 mypy==0.790 flake8==3.8.4 testfixtures==6.17.0 coverage==5.3 gitpython==3.1.11 pylint==2.6.0 sphinx==3.3.1 'git+https://github.com/samtygier-stfc/sphinx-multiversion.git@prebuild_command' pytest-randomly==3.5.0 pytest-xdist==2.2.0 pytest-repeat==0.9.1 isort==5.6.4 'eyes-images==4.20.*' parameterized==0.8.1 pre-commit pyqt5==5.15 'pyqtgraph>=0.12.1,<0.13' jenkspy==0.2.0
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
conda activate mantidimaging && pip install pytest==6.2.1 pytest-cov==2.10.1 coveralls==2.2.0 yapf==0.30.0 mypy==0.790 flake8==3.8.4 testfixtures==6.17.0 coverage==5.3 gitpython==3.1.11 pylint==2.6.0 sphinx==3.3.1 'git+https://github.com/samtygier-stfc/sphinx-multiversion.git@prebuild_command' pytest-randomly==3.5.0 pytest-xdist==2.2.0 pytest-repeat==0.9.1 isort==5.6.4 'eyes-images==4.20.*' parameterized==0.8.1 pre-commit pyqt5==5.15 'pyqtgraph>=0.12.1,<0.13' jenkspy==0.2.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
conda activate mantidimaging && pip install pytest-randomly==3.4.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
source /root/miniconda3/etc/profile.d/conda.sh
conda activate mantidimaging
xvfb-run -a python -m pytest --no-header -rA --tb=no -p no:cacheprovider -p no:randomly' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
source /root/miniconda3/etc/profile.d/conda.sh
conda activate mantidimaging
export QT_QPA_PLATFORM=offscreen
xvfb-run -a python -m pytest -v --tb=short -rA -p no:cacheprovider -p no:randomly' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libglib2.0-0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-xinerama0 libxcb-xkb1
###ACTION_DELIMITER###
bash test_commands.sh -v --debug
###ACTION_DELIMITER###
conda activate mantidimaging && conda install -c conda-forge -y cil
###ACTION_DELIMITER###
conda activate mantidimaging && pip install cil
###ACTION_DELIMITER###
conda activate mantidimaging && conda install -c ccpi -y cil
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
source /root/miniconda3/etc/profile.d/conda.sh
conda activate mantidimaging
export QT_QPA_PLATFORM=offscreen
xvfb-run -a python -m pytest -v --tb=short -rA -p no:cacheprovider -p no:randomly

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
source /root/miniconda3/etc/profile.d/conda.sh
conda activate mantidimaging
export QT_QPA_PLATFORM=offscreen
xvfb-run -a python -m pytest -v --tb=short -rA -p no:cacheprovider -p no:randomly

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
source /root/miniconda3/etc/profile.d/conda.sh
conda activate mantidimaging
export QT_QPA_PLATFORM=offscreen
xvfb-run -a python -m pytest -v --tb=short -rA -p no:cacheprovider -p no:randomly

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
RUN git clone https://github.com/mantidproject/mantidimaging.git /home/mantidimaging

WORKDIR /home/mantidimaging
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("mantidproject", "mantidimaging_1096_to_1033")
class MANTIDIMAGING_1096_TO_1033(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re
        # Regex patterns to match test names and statuses
        # Regex patterns to match valid test names (mantidimaging/...::TestClass::test_method)
        test_name_pattern = r'mantidimaging/.*?::.*?::.*?'
        passed_pattern1 = re.compile(r'^(' + test_name_pattern + ') PASSED')  # Test name before PASSED
        passed_pattern2 = re.compile(r'PASSED (' + test_name_pattern + ')$')  # Test name after PASSED
        failed_pattern = re.compile(r'FAILED (' + test_name_pattern + ')$')    # Test name after FAILED
        # Skipped tests: capture test name from file path and line (fallback)
        skipped_pattern = re.compile(r'SKIPPED \[\d+\] (.*?\.py(?::\d+)?):')  # File path with optional line number for skipped tests
        for line in log.split('\n'):
            line = line.strip()
            # Extract PASSED tests
            if 'PASSED' in line:
                match1 = passed_pattern1.search(line)
                if match1:
                    test_name = match1.group(1).strip()
                    if test_name:
                        passed_tests.add(test_name)
                else:
                    match2 = passed_pattern2.search(line)
                    if match2:
                        test_name = match2.group(1).strip()
                        if test_name:
                            passed_tests.add(test_name)
            # Extract FAILED tests
            elif 'FAILED' in line:
                match = failed_pattern.search(line)
                if match:
                    test_name = match.group(1).strip()
                    if test_name:
                        failed_tests.add(test_name)
            # Extract SKIPPED tests
            elif 'SKIPPED' in line:
                match = skipped_pattern.search(line)
                if match:
                    test_name = match.group(1).strip()
                    if test_name:
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
