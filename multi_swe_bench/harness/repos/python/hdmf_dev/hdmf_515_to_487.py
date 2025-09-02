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
cat README.rst
###ACTION_DELIMITER###
cat Makefile
###ACTION_DELIMITER###
make init
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make init
###ACTION_DELIMITER###
sed -i 's/codecov==2.1.10/codecov==2.1.13/' requirements-dev.txt
###ACTION_DELIMITER###
make init
###ACTION_DELIMITER###
apt-get update && apt-get install -y libhdf5-dev
###ACTION_DELIMITER###
make init
###ACTION_DELIMITER###
ldconfig -p | grep hdf5; ls /usr/lib/x86_64-linux-gnu/libhdf5.so*
###ACTION_DELIMITER###
ln -s /lib/x86_64-linux-gnu/libhdf5_serial.so /lib/x86_64-linux-gnu/libhdf5.so && ldconfig
###ACTION_DELIMITER###
make init
###ACTION_DELIMITER###
apt-get update && apt-get install -y pkg-config
###ACTION_DELIMITER###
ls /usr/lib/x86_64-linux-gnu/pkgconfig | grep hdf5; ln -s /usr/lib/x86_64-linux-gnu/pkgconfig/hdf5-serial.pc /usr/lib/x86_64-linux-gnu/pkgconfig/hdf5.pc
###ACTION_DELIMITER###
pip install h5py==2.10.0 --no-binary h5py --hdf5=/usr/lib/x86_64-linux-gnu/
###ACTION_DELIMITER###
HDF5_DIR=/usr/lib/x86_64-linux-gnu/ pip install h5py==2.10.0 --no-binary h5py
###ACTION_DELIMITER###
pip install Cython==0.29.21
###ACTION_DELIMITER###
HDF5_DIR=/usr/lib/x86_64-linux-gnu/ pip install h5py==2.10.0
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
HDF5_DIR=/usr/lib/x86_64-linux-gnu/ pip install h5py==2.10.0
###ACTION_DELIMITER###
CFLAGS="-I/usr/include/hdf5/serial/" HDF5_DIR=/usr/lib/x86_64-linux-gnu/ pip install h5py==2.10.0
###ACTION_DELIMITER###
ln -s /usr/lib/x86_64-linux-gnu/libhdf5_serial_hl.so /usr/lib/x86_64-linux-gnu/libhdf5_hl.so
###ACTION_DELIMITER###
ldconfig && CFLAGS="-I/usr/include/hdf5/serial/" HDF5_DIR=/usr/lib/x86_64-linux-gnu/ pip install h5py==2.10.0
###ACTION_DELIMITER###
make init
###ACTION_DELIMITER###
echo 'tox -e py39 -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cat MANIFEST.in
###ACTION_DELIMITER###
ls -R src/hdmf
###ACTION_DELIMITER###
python setup.py build
###ACTION_DELIMITER###
cat setup.py
###ACTION_DELIMITER###
cat .gitmodules
###ACTION_DELIMITER###
git submodule init && git submodule update
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/importlib-metadata<2/importlib-metadata>=3.6.0/' requirements-dev.txt
###ACTION_DELIMITER###
make init
###ACTION_DELIMITER###
rm -rf .tox && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
tox -e py39 -v

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
tox -e py39 -v

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
tox -e py39 -v

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
RUN git clone https://github.com/hdmf-dev/hdmf.git /home/hdmf

WORKDIR /home/hdmf
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("hdmf-dev", "hdmf_515_to_487")
class HDMF_515_TO_487(Instance):
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
        import json
        # Pattern to match test rows in log tables
        test_row_pattern = re.compile(r'\|\s*(.*?)\s*\|\s*.*?\s*\|\s*(.*?)\s*\|')
        # Remove ANSI color codes
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        for line in log.split('\n'):
            match = test_row_pattern.search(line)
            if match:
                test_name_part = match.group(1)
                status_part = match.group(2)
                # Clean test name (remove trailing colon and whitespace)
                test_name = test_name_part.split(':', 1)[0].strip()
                if not test_name:
                    continue
                # Clean status (remove ANSI codes and normalize)
                cleaned_status = ansi_escape.sub('', status_part).strip().lower()
                # Categorize tests
                if cleaned_status == 'pass':
                    passed_tests.add(test_name)
                elif cleaned_status in ['fail', 'error']:
                    failed_tests.add(test_name)
                elif cleaned_status in ['skip', 'skipped']:
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
