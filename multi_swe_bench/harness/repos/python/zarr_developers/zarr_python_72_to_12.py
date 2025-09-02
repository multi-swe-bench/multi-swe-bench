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
python3 --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
pip3 install --break-system-packages -r requirements.txt -r <(grep -v '^nose$' requirements_test.txt) && pip3 install --break-system-packages pytest pytest-nose
###ACTION_DELIMITER###
pip3 install --break-system-packages -r requirements.txt -r <(grep -v '^nose$' requirements_test.txt) && pip3 install --break-system-packages nose2
###ACTION_DELIMITER###
echo -e 'python3 setup.py build_ext --inplace
nose2 -v --with-doctest --doctest-options=NORMALIZE_WHITESPACE zarr
python3 -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libblosc-dev software-properties-common && add-apt-repository -y ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.9 python3.9-pip python3.9-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.9 python3.9-dev && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.9 get-pip.py
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.9 get-pip.py
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.9-distutils
###ACTION_DELIMITER###
python3.9 get-pip.py
###ACTION_DELIMITER###
python3.9 -m ensurepip --upgrade
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.9-venv
###ACTION_DELIMITER###
python3.9 -m ensurepip --upgrade
###ACTION_DELIMITER###
pip3.9 install --break-system-packages -r requirements.txt -r <(grep -v '^nose$' requirements_test.txt) && pip3.9 install --break-system-packages nose2
###ACTION_DELIMITER###
python3.9 -m pip install --break-system-packages -r requirements.txt -r <(grep -v '^nose$' requirements_test.txt) && python3.9 -m pip install --break-system-packages nose2
###ACTION_DELIMITER###
echo -e 'python3.9 setup.py build_ext --inplace
python3.9 -m nose2 -v --with-doctest --doctest-options=NORMALIZE_WHITESPACE zarr
python3.9 -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'python3.9 setup.py develop
python3.9 -m nose2 -v --plugin=nose2.plugins.doctests --doctest-opt=NORMALIZE_WHITESPACE zarr
python3.9 -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst' > test_commands.sh && python3.9 -m pip install 'numpy<2.0'
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y --reinstall libblosc-dev && python3.9 -m pip install -e .
###ACTION_DELIMITER###
python3.9 -m pip install --upgrade setuptools
###ACTION_DELIMITER###
python3.9 -m pip install -e .
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
python3.9 -m pip install --force-reinstall --no-deps -e . && bash test_commands.sh
###ACTION_DELIMITER###
rm -f zarr/blosc.cpython-39-x86_64-linux-gnu.so && rm -rf build && python3.9 -m pip install -e . && bash test_commands.sh
###ACTION_DELIMITER###
export CFLAGS="-I/usr/include" && export LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lblosc" && rm -rf build zarr/blosc.cpython-39-x86_64-linux-gnu.so && python3.9 -m pip install --force-reinstall --no-deps -e . && bash test_commands.sh
###ACTION_DELIMITER###
python3.9 -m pip install blosc && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export CFLAGS="-I/usr/include"
export LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lblosc"
python3.9 setup.py build_ext --inplace
python3.9 -m nose2 -v --plugin=nose2.plugins.doctests --doctest-opt=NORMALIZE_WHITESPACE zarr
python3.9 -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export BLOSC_DIR=/usr
export CFLAGS="-I/usr/include"
export LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lblosc"
python3.9 setup.py build_ext --inplace --force
python3.9 -m nose2 -v --plugin=nose2.plugins.doctests --doctest-options=NORMALIZE_WHITESPACE zarr
python3.9 -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
git submodule update --init && rm -rf build zarr/blosc.cpython-39-x86_64-linux-gnu.so && python3.9 setup.py build_ext --inplace && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'python3.9 -m nose2 -v --plugin=nose2.plugins.doctests --doctest-opt=NORMALIZE_WHITESPACE zarr
python3.9 -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst' > test_commands.sh && python3.9 setup.py build_ext --inplace && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'python3.9 setup.py build_ext --inplace
python3.9 -m nose2 -v --with-doctest --doctest-options NORMALIZE_WHITESPACE zarr
python3.9 -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'python3.9 setup.py build_ext --inplace
python3.9 -m nose2 -v --plugin=nose2.plugins.doctests --doctest-opt=NORMALIZE_WHITESPACE zarr
python3.9 -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'python3.9 setup.py build_ext --inplace
python3.9 -m nose2 -v --with-doctest --doctest-options=NORMALIZE_WHITESPACE zarr
python3.9 -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'python3.9 setup.py build_ext --inplace
python3.9 -m nose2 -v --plugin=nose2.plugins.doctests --doctest-opt=NORMALIZE_WHITESPACE zarr
python3.9 -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export CFLAGS="-I/usr/include -I/home/zarr-python/c-blosc/blosc"\nexport LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lblosc"\npython3.9 setup.py build_ext --inplace\npython3.9 -m nose2 -v --with-doctest --doctest-options NORMALIZE_WHITESPACE zarr\npython3.9 -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '[doctest]\noptionflags = NORMALIZE_WHITESPACE' > nose2.cfg && echo -e 'python3.9 setup.py build_ext --inplace\npython3.9 -m nose2 -v --with-doctest zarr\npython3.9 -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '[doctest]\noptionflags = NORMALIZE_WHITESPACE' > nose2.cfg && echo -e 'python3.9 setup.py build_ext --inplace\npython3.9 -m nose2 -v --plugin=nose2.plugins.doctests zarr\npython3.9 -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
python3.9 -m pip install nose && echo -e 'python3.9 setup.py build_ext --inplace\nnosetests -v --with-doctest --doctest-options=+NORMALIZE_WHITESPACE zarr\npython3.9 -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst' > test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python3.9 setup.py build_ext --inplace
nosetests -v --with-doctest --doctest-options=+NORMALIZE_WHITESPACE zarr
python3.9 -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst

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
python3.9 setup.py build_ext --inplace
nosetests -v --with-doctest --doctest-options=+NORMALIZE_WHITESPACE zarr
python3.9 -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst

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
python3.9 setup.py build_ext --inplace
nosetests -v --with-doctest --doctest-options=+NORMALIZE_WHITESPACE zarr
python3.9 -m doctest -o NORMALIZE_WHITESPACE -o ELLIPSIS docs/tutorial.rst docs/spec/v2.rst

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
RUN git clone https://github.com/zarr-developers/zarr-python.git /home/zarr-python

WORKDIR /home/zarr-python
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("zarr-developers", "zarr_python_72_to_12")
class ZARR_PYTHON_72_TO_12(Instance):
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
        pattern = re.compile(r'(test_\S+\s*\([^)]+\))\s*\.\.\.\s*(\w+)')
        matches = pattern.findall(log)
        for test_name, status in matches:
            status_lower = status.lower()
            if status_lower == 'ok':
                passed_tests.add(test_name)
            elif status_lower in ('error', 'failed'):
                failed_tests.add(test_name)
            elif status_lower in ('skipped', 'skip'):
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
