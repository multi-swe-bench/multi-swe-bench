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
                """ls
###ACTION_DELIMITER###
cat install-requiremets.txt
###ACTION_DELIMITER###
sed -i 's/skimage/scikit-image/' install-requiremets.txt
###ACTION_DELIMITER###
pip install -r setup-requirements.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libhdf5-serial-dev libfftw3-dev libopenblas-dev
###ACTION_DELIMITER###
pip install -r install-requiremets.txt
###ACTION_DELIMITER###
pip install git+https://github.com/tomopy/tomopy.git
###ACTION_DELIMITER###
pip install -r test-requirements.txt
###ACTION_DELIMITER###
echo 'nosetests -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip list | grep numpy
###ACTION_DELIMITER###
pip install numpy
###ACTION_DELIMITER###
pip install -r install-requiremets.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install numexpr
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
find / -name 'libtomo-recon.so' 2>/dev/null
###ACTION_DELIMITER###
git clone https://github.com/tomopy/tomopy.git && cd tomopy && git submodule update --init --recursive && pip install --no-binary :all: -v .
###ACTION_DELIMITER###
find . -name 'libtomo-recon.so'
###ACTION_DELIMITER###
mkdir -p build && cd build && cmake -DCMAKE_VERBOSE_MAKEFILE=ON .. && make
###ACTION_DELIMITER###
apt-get update && apt-get install -y cmake
###ACTION_DELIMITER###
cmake -DCMAKE_VERBOSE_MAKEFILE=ON .. && make
###ACTION_DELIMITER###
cmake -DCMAKE_VERBOSE_MAKEFILE=ON -DUSE_MKL=OFF -DBLA_VENDOR=OpenBLAS .. && make
###ACTION_DELIMITER###
cmake -DCMAKE_VERBOSE_MAKEFILE=ON -DUSE_MKL=OFF -DBLA_VENDOR=OpenBLAS -DBUILD_GRIDREC=OFF .. && make
###ACTION_DELIMITER###
apt-get update && apt-get install -y libmkl-dev
###ACTION_DELIMITER###
cmake -DCMAKE_VERBOSE_MAKEFILE=ON -DUSE_MKL=OFF -DBUILD_GRIDREC=OFF -DBLAS_LIBRARIES=/usr/lib/x86_64-linux-gnu/libopenblas.so -DLAPACK_LIBRARIES=/usr/lib/x86_64-linux-gnu/liblapack.so .. && make
###ACTION_DELIMITER###
rm -rf build && mkdir -p build && cd build && cmake -DCMAKE_VERBOSE_MAKEFILE=ON -DUSE_MKL=OFF -DBLA_VENDOR=OpenBLAS -DBUILD_GRIDREC=OFF .. && make
###ACTION_DELIMITER###
sed -i 's/find_package(MKL REQUIRED)/# find_package(MKL REQUIRED)/' ../source/libtomo/gridrec/CMakeLists.txt && cmake -DCMAKE_VERBOSE_MAKEFILE=ON -DUSE_MKL=OFF -DBLA_VENDOR=OpenBLAS -DBUILD_GRIDREC=OFF .. && make
###ACTION_DELIMITER###
cd ../../ && rm -rf build && mkdir -p build && cd build && sed -i 's/find_package(MKL REQUIRED)/# find_package(MKL REQUIRED)/' ../source/libtomo/gridrec/CMakeLists.txt && cmake -DCMAKE_VERBOSE_MAKEFILE=ON -DUSE_MKL=OFF -DBLA_VENDOR=OpenBLAS -DBUILD_GRIDREC=OFF .. && make
###ACTION_DELIMITER###
cmake -DCMAKE_VERBOSE_MAKEFILE=ON -DUSE_MKL=OFF -DBLA_VENDOR=OpenBLAS -DBUILD_GRIDREC=OFF .. && make tomo-recon
###ACTION_DELIMITER###
find . -name 'libtomo-recon.so' && cp $(find . -name 'libtomo-recon.so') /usr/local/lib && ldconfig
###ACTION_DELIMITER###
ldconfig -p | grep tomo-recon && python -c 'import tomopy; print("TomoPy imported successfully")'
###ACTION_DELIMITER###
cmake -DCMAKE_VERBOSE_MAKEFILE=ON -DTOMOPY_USE_MKL=OFF -DBLA_VENDOR=OpenBLAS -DBUILD_GRIDREC=ON .. && make tomo-gridrec && find . -name 'libtomo-gridrec.so' && cp $(find . -name 'libtomo-gridrec.so') /usr/local/lib && ldconfig
###ACTION_DELIMITER###
apt-get update && apt-get install -y pkg-config && cmake -DCMAKE_VERBOSE_MAKEFILE=ON -DTOMOPY_USE_MKL=OFF -DBLA_VENDOR=OpenBLAS -DBUILD_GRIDREC=ON .. && make tomo-gridrec && find . -name 'libtomo-gridrec.so' && cp $(find . -name 'libtomo-gridrec.so') /usr/local/lib && ldconfig
###ACTION_DELIMITER###
python -c 'import tomopy; print("TomoPy imported successfully")'
###ACTION_DELIMITER###
cmake -DCMAKE_VERBOSE_MAKEFILE=ON -DTOMOPY_USE_MKL=OFF -DBLA_VENDOR=OpenBLAS .. && make tomo-prep && find . -name 'libtomo-prep.so' && cp $(find . -name 'libtomo-prep.so') /usr/local/lib && ldconfig
###ACTION_DELIMITER###
ldconfig -p | grep tomo && export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH && python -c 'import tomopy; print("TomoPy imported successfully")' && cd /home/mantidimaging && bash test_commands.sh
###ACTION_DELIMITER###
cmake -DCMAKE_VERBOSE_MAKEFILE=ON -DTOMOPY_USE_MKL=OFF -DBLA_VENDOR=OpenBLAS .. && make tomo-misc && find . -name 'libtomo-misc.so' && cp $(find . -name 'libtomo-misc.so') /usr/local/lib && ldconfig
###ACTION_DELIMITER###
ldconfig -p | grep tomo && export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH && python -c 'import tomopy; print("TomoPy imported successfully")' && cd /home/mantidimaging && bash test_commands.sh
###ACTION_DELIMITER###
pip install pywavelets && python -c 'import tomopy; print("TomoPy imported successfully")' && cd /home/mantidimaging && bash test_commands.sh
###ACTION_DELIMITER###
pip install PyQt5 && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgl1-mesa-glx && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libglib2.0-0 && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y tomopy && git clone https://github.com/tomopy/tomopy.git && cd tomopy && git submodule update --init --recursive && pip install --no-binary :all: -v . && cd .. && python -c 'import tomopy.io; print("tomopy.io imported successfully")' && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf tomopy && git clone https://github.com/tomopy/tomopy.git && cd tomopy && git submodule update --init --recursive && pip install --no-binary :all: -v . && cd .. && python -c 'import tomopy.io; print("tomopy.io imported successfully")' && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y tomopy && pip install git+https://github.com/tomopy/tomopy.git@main && python -c 'import tomopy.io; print("tomopy.io imported successfully")' && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y tomopy && rm -rf tomopy && git clone https://github.com/tomopy/tomopy.git && cd tomopy && git checkout master && git submodule update --init --recursive && pip install --no-binary :all: -v . && cd .. && python -c 'import tomopy.io; print("tomopy.io imported successfully")' && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y tomopy && pip install tomopy==1.4.0 && python -c 'import tomopy.io; print("tomopy.io imported successfully")' && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y tomopy && rm -rf tomopy && git clone https://github.com/tomopy/tomopy.git && cd tomopy && git checkout 2c94ed18a06f7908b018c6f8e43d320f8a8488f2 && git submodule update --init --recursive && pip install --no-binary :all: -v . && cd .. && python -c 'import tomopy.io; print("tomopy.io imported successfully")' && bash test_commands.sh
###ACTION_DELIMITER###
""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
nosetests -v

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
nosetests -v

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
nosetests -v

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


@Instance.register("mantidproject", "mantidimaging_69_to_69")
class MANTIDIMAGING_69_TO_69(Instance):
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

        # Use regex to match test result lines and extract test name and status
        pattern = re.compile(
            r"^(test_\w+)\s*\([^)]+\)\s*\.+\s*(ok|passed|error|fail|failed|skipped)$",
            re.IGNORECASE | re.MULTILINE,
        )
        for match in pattern.finditer(log):
            test_name = match.group(1).strip()
            status = match.group(2).strip().lower()
            if status in ("ok", "passed"):
                passed_tests.add(test_name)
            elif status in ("error", "fail"):
                failed_tests.add(test_name)
            # Add handling for SKIPPED if present in logs
            elif status == "skipped":
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
