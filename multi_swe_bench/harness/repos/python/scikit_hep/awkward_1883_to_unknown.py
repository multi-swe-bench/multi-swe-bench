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
                """apt-get update && apt-get install -y cmake g++
###ACTION_DELIMITER###
pip list | grep numpy
###ACTION_DELIMITER###
pip install numpy
###ACTION_DELIMITER###
pip install .[test,dev]
###ACTION_DELIMITER###
cmake -S /home/awkward -B build/temp.linux-x86_64-cpython-39 -DCMAKE_LIBRARY_OUTPUT_DIRECTORY=/home/awkward/build/lib.linux-x86_64-cpython-39/ -DPYTHON_EXECUTABLE=/usr/local/bin/python3.9 -DEXAMPLE_VERSION_INFO=2.0.0rc3 -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/home/awkward/build/lib.linux-x86_64-cpython-39/ -DPYTHON_EXECUTABLE=/usr/local/bin/python3.9 -DPYBUILD=ON -DBUILD_TESTING=OFF -DCMAKE_CXX_COMPILER=g++
###ACTION_DELIMITER###
git submodule update --init --recursive
###ACTION_DELIMITER###
cmake -S /home/awkward -B build/temp.linux-x86_64-cpython-39 -DCMAKE_LIBRARY_OUTPUT_DIRECTORY=/home/awkward/build/lib.linux-x86_64-cpython-39/ -DPYTHON_EXECUTABLE=/usr/local/bin/python3.9 -DEXAMPLE_VERSION_INFO=2.0.0rc3 -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/home/awkward/build/lib.linux-x86_64-cpython-39/ -DPYTHON_EXECUTABLE=/usr/local/bin/python3.9 -DPYBUILD=ON -DBUILD_TESTING=OFF -DCMAKE_CXX_COMPILER=g++
###ACTION_DELIMITER###
make -C build/temp.linux-x86_64-cpython-39
###ACTION_DELIMITER###
make -C build/temp.linux-x86_64-cpython-39 install
###ACTION_DELIMITER###
echo -e 'export PYTHONPATH=/home/awkward/build/lib.linux-x86_64-cpython-39:$PYTHONPATH
python -m pytest -vv -rs tests-spec
python -m pytest -vv -rs tests-spec-explicit
python -m pytest -vv -rs tests-cpu-kernels
python -m pytest -vv -rs tests' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -r requirements-test.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.26.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls -l
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo -e 'export PYTHONPATH=/home/awkward/build/lib.linux-x86_64-cpython-39:$PYTHONPATH
python -m pytest -vv -rs tests' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest-xdist
###ACTION_DELIMITER###
echo -e 'export PYTHONPATH=/home/awkward/build/lib.linux-x86_64-cpython-39:$PYTHONPATH
python -m pytest -vv -rs -n auto tests' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYTHONPATH=/home/awkward/build/lib.linux-x86_64-cpython-39:$PYTHONPATH
python -m pytest -vv --no-header -rA --tb=no -p no:cacheprovider -n auto tests' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYTHONPATH=/home/awkward/build/lib.linux-x86_64-cpython-39:$PYTHONPATH
python -m pytest -vv --no-header -rA --tb=no -p no:cacheprovider -n 4 tests' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYTHONPATH=/home/awkward/build/lib.linux-x86_64-cpython-39:$PYTHONPATH
python -m pytest -v --no-header -rA --tb=no -p no:cacheprovider -n 4 tests' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYTHONPATH=/home/awkward/build/lib.linux-x86_64-cpython-39:$PYTHONPATH
python -m pytest -v --no-header -rA --tb=no -p no:cacheprovider -n 2 tests' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYTHONPATH=/home/awkward/build/lib.linux-x86_64-cpython-39:$PYTHONPATH
python -m pytest -v --no-header -rA --tb=no -p no:cacheprovider -n 1 tests' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYTHONPATH=/home/awkward/build/lib.linux-x86_64-cpython-39:$PYTHONPATH
python -m pytest -v --no-header -rA --tb=no -p no:cacheprovider -n auto tests' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYTHONPATH=/home/awkward/build/lib.linux-x86_64-cpython-39:$PYTHONPATH
python -m pytest -v --no-header -rA --tb=no -p no:cacheprovider -n 1 tests' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYTHONPATH=/home/awkward/build/lib.linux-x86_64-cpython-39:$PYTHONPATH
python -m pytest --no-header -rA --tb=no -p no:cacheprovider tests' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y pyarrow && pip install pyarrow==10.0.1
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
export PYTHONPATH=/home/awkward/build/lib.linux-x86_64-cpython-39:$PYTHONPATH
python -m pytest --no-header -rA --tb=no -p no:cacheprovider tests

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
export PYTHONPATH=/home/awkward/build/lib.linux-x86_64-cpython-39:$PYTHONPATH
python -m pytest --no-header -rA --tb=no -p no:cacheprovider tests

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
export PYTHONPATH=/home/awkward/build/lib.linux-x86_64-cpython-39:$PYTHONPATH
python -m pytest --no-header -rA --tb=no -p no:cacheprovider tests

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
RUN git clone https://github.com/scikit-hep/awkward.git /home/awkward

WORKDIR /home/awkward
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("scikit-hep", "awkward_1883_to_unknown")
class AWKWARD_1883_TO_UNKNOWN(Instance):
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
        pass
