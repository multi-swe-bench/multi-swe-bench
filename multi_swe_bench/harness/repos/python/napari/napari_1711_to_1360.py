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
                """apt-get update && apt-get install -y libglib2.0-0 libgl1-mesa-glx libxcb-xinerama0 libqt5gui5 libqt5widgets5 libqt5core5a libqt5opengl5 python3-pyqt5 python3-pyqt5.qtopengl python3-sip python3-pip python3-venv
###ACTION_DELIMITER###
apt-get update && apt-get install -y libglib2.0-0 libgl1 libxcb-xinerama0 libqt5gui5t64 libqt5widgets5t64 libqt5core5t64 libqt5opengl5t64 python3-pyqt5 python3-pyqt5.qtopengl python3-sip python3-pip python3-venv libqt5opengl5-dev
###ACTION_DELIMITER###
python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && pip install -r requirements/test.txt
###ACTION_DELIMITER###
echo 'CI=1 venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'CI=1 VISPY_BACKEND=pyglet venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y gdb
###ACTION_DELIMITER###
gdb --batch --ex run --ex bt --args venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
gdb --batch --ex run --ex bt --args venv/bin/python3 venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider
###ACTION_DELIMITER###
echo 'CI=1 QT_QPA_PLATFORM=offscreen venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get remove -y python3-pyqt5 python3-pyqt5.qtopengl python3-sip && rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install PyQt5 PyQt5-sip && pip install -r requirements.txt && pip install -r requirements/test.txt && echo 'CI=1 QT_QPA_PLATFORM=offscreen venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.11 python3.11-venv && rm -rf venv && python3.11 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install PyQt5 PyQt5-sip && pip install -r requirements.txt && pip install -r requirements/test.txt && echo 'CI=1 QT_QPA_PLATFORM=offscreen venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository -y ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.11 python3.11-venv && rm -rf venv && python3.11 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install PyQt5 PyQt5-sip && pip install -r requirements.txt && pip install -r requirements/test.txt && echo 'CI=1 QT_QPA_PLATFORM=offscreen venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install 'Jinja2<3.1' && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install six && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && SIX_PATH=$(python -c 'import six; print(six.__file__)') && VISPY_EXT=$(python -c 'import vispy; print(vispy.__path__[0])')/ext && cp $SIX_PATH $VISPY_EXT/ && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install 'numpy<1.20' && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.11-dev && source venv/bin/activate && pip install numpy==1.23.5 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.21.6 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.22.4 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.24.6 zarr==2.16.0 scipy==1.10.1 pandas==1.5.3 scikit-image==0.21.0 xarray==2023.3.0 numcodecs==0.15.3 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.23.5 zarr==2.16.0 scipy==1.10.1 pandas==1.5.3 scikit-image==0.21.0 xarray==2023.3.0 numcodecs==0.15.3 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.23.5 zarr==2.16.0 scipy==1.10.1 pandas==2.0.0 scikit-image==0.21.0 xarray==2023.3.0 numcodecs==0.15.1 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.23.5 zarr==2.16.0 scipy==1.10.1 pandas==1.5.3 scikit-image==0.21.0 xarray==2023.3.0 numcodecs==0.15.2 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.23.5 zarr==2.16.0 scipy==1.10.1 pandas==1.5.3 scikit-image==0.21.0 xarray==2023.3.0 numcodecs==0.15.1 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.23.5 zarr==2.16.0 scipy==1.10.1 pandas==1.5.3 scikit-image==0.21.0 xarray==2023.3.0 numcodecs==0.15.0 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.23.5 zarr==2.16.0 scipy==1.10.1 pandas==1.5.3 scikit-image==0.21.0 xarray==2023.3.0 numcodecs==0.14.1 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.23.5 zarr==2.16.0 scipy==1.10.1 pandas==1.5.3 scikit-image==0.21.0 xarray==2023.3.0 numcodecs==0.13.0 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install tifffile==2023.4.12 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install napari-svg && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip uninstall -y napari-svg && pip install napari-svg==0.1.6 && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y xvfb && source venv/bin/activate && pip uninstall -y napari-svg && pip install napari-svg==0.2.1 && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip uninstall -y napari-svg scipy && pip install napari-svg==0.2.1 scipy==1.7.3 matplotlib && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.10 python3.10-venv && rm -rf venv && python3.10 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && pip install -r requirements/test.txt && pip install napari-svg==0.2.1 scipy==1.8.1 matplotlib && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip uninstall -y Jinja2 && pip install 'Jinja2<3.1' && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && SIX_PATH=$(python -c 'import six; print(six.__file__)') && VISPY_EXT=$(python -c 'import vispy; print(vispy.__path__[0])')/ext && cp $SIX_PATH $VISPY_EXT/ && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.24.4 && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.21.6 && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip uninstall -y pandas scikit-image xarray zarr contourpy matplotlib && pip install pandas==1.3.5 scikit-image==0.19.3 xarray==0.20.2 zarr==2.10.3 contourpy==1.0.5 matplotlib==3.5.3 && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip uninstall -y dask && pip install dask==2021.10.0 && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip uninstall -y numpy && pip install numpy==1.21.6 && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip uninstall -y tifffile napari-svg && pip install tifffile==2021.11.2 napari-svg==0.2.1 && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && apt-get install -y libcairo2-dev && pip install pycairo svgwrite && pip uninstall -y napari-svg && pip install napari-svg==0.1.6 && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.10-dev && source venv/bin/activate && pip install pycairo svgwrite && pip uninstall -y napari-svg && pip install napari-svg==0.1.6 && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip uninstall -y napari-svg vispy && pip install --no-cache-dir napari-svg==0.2.1 vispy==0.14.1 && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libcairo2-dev libgdk-pixbuf2.0-dev && source venv/bin/activate && pip uninstall -y napari-svg vispy && pip install --no-cache-dir napari-svg==0.2.1 vispy==0.15.1 && xvfb-run -a bash test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
CI=1 QT_QPA_PLATFORM=offscreen venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider

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
CI=1 QT_QPA_PLATFORM=offscreen venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider

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
CI=1 QT_QPA_PLATFORM=offscreen venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider

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
RUN git clone https://github.com/napari/napari.git /home/napari

WORKDIR /home/napari
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("napari", "napari_1711_to_1360")
class NAPARI_1711_TO_1360(Instance):
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
        # Define regex pattern to match test results with status (PASSED, FAILED, SKIPPED)
        pattern = re.compile(r'^.*?(?:(napari/[^\s]+::[^\s]+)\s+(PASSED|FAILED|SKIPPED)|(PASSED|FAILED|SKIPPED)\s+(napari/[^\s]+::[^\s]+))', re.MULTILINE | re.IGNORECASE)
        matches = pattern.findall(log)
        for match in matches:
            test_name1, status1, status2, test_name2 = match
            if test_name1 and status1:
                test_name = test_name1
                status = status1
            elif status2 and test_name2:
                test_name = test_name2
                status = status2
            else:
                continue  # Skip invalid matches
            # Ensure the test name contains '::' to confirm it's a test identifier
            if '::' in test_name:
                status = status.upper()
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
