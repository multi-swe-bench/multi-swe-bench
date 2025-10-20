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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip python3.12-venv libgl1-mesa-glx xvfb libqt5x11extras5 herbstluftwm
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip python3.12-venv libgl1 xvfb libqt5x11extras5 herbstluftwm
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
venv/bin/pip install -r requirements/test.txt
###ACTION_DELIMITER###
venv/bin/pip install -e .
###ACTION_DELIMITER###
echo 'xvfb-run -a venv/bin/pytest -v --no-header -rA --tb=auto -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install PyQt5
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y python3-distutils
###ACTION_DELIMITER###
venv/bin/pip install --upgrade setuptools
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'from six import *' > venv/lib/python3.12/site-packages/vispy/ext/six.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'import builtins
from typing import Optional
original_eval = builtins.eval
def patched_eval(expr, globals=None, locals=None, *args, **kwargs):
    if globals is None:
        globals = {}
    globals.setdefault("Optional", Optional)
    return original_eval(expr, globals, locals, *args, **kwargs)
builtins.eval = patched_eval' > venv/lib/python3.12/site-packages/sitecustomize.py
###ACTION_DELIMITER###
echo -e 'import builtins
from typing import Optional
print("Loaded sitecustomize.py: Patching eval")
original_eval = builtins.eval
def patched_eval(expr, globals=None, locals=None, *args, **kwargs):
    if globals is None:
        globals = {}
    globals.setdefault("Optional", Optional)
    return original_eval(expr, globals, locals, *args, **kwargs)
builtins.eval = patched_eval' > venv/lib/python3.12/site-packages/sitecustomize.py
###ACTION_DELIMITER###
echo -e 'import builtins
from typing import Optional
original_eval = builtins.eval
def patched_eval(expr, globals=None, locals=None, *args, **kwargs):
    if globals is None:
        globals = {}
    globals.setdefault("Optional", Optional)
    return original_eval(expr, globals, locals, *args, **kwargs)
builtins.eval = patched_eval' > conftest.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'import builtins
import sys
from typing import Optional
print("Loaded conftest.py: Patching eval")
original_eval = builtins.eval
def patched_eval(expr, globals=None, locals=None, *args, **kwargs):
    if globals is None:
        frame = sys._getframe(1)
        globals = frame.f_globals.copy()
    globals.setdefault("Optional", Optional)
    return original_eval(expr, globals, locals, *args, **kwargs)
builtins.eval = patched_eval' > conftest.py
###ACTION_DELIMITER###
echo -e 'import builtins
import sys
from typing import Optional
print("Loaded conftest.py: Patching eval")
original_eval = builtins.eval
def patched_eval(expr, globals=None, locals=None, *args, **kwargs):
    if globals is None:
        frame = sys._getframe(1)
        globals = frame.f_globals.copy()
        if locals is None:
            locals = frame.f_locals.copy()
    globals.setdefault("Optional", Optional)
    return original_eval(expr, globals, locals, *args, **kwargs)
builtins.eval = patched_eval' > conftest.py
###ACTION_DELIMITER###
echo -e 'import builtins
from typing import Optional
builtins.Optional = Optional' > venv/lib/python3.12/site-packages/sitecustomize.py
###ACTION_DELIMITER###
rm -f conftest.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'import builtins
from typing import Optional
print("Loaded sitecustomize.py: Added Optional to builtins")
builtins.Optional = Optional' > venv/lib/python3.12/site-packages/sitecustomize.py
###ACTION_DELIMITER###
echo -e 'import builtins
from typing import Optional
builtins.Optional = Optional' > conftest.py
###ACTION_DELIMITER###
echo -e 'import builtins
from typing import Optional
original_eval = builtins.eval
def patched_eval(expr, globals=None, locals=None, *args, **kwargs):
    if globals is None:
        globals = {}
    globals["Optional"] = Optional
    return original_eval(expr, globals, locals, *args, **kwargs)
builtins.eval = patched_eval' > conftest.py
###ACTION_DELIMITER###
echo -e 'import builtins
from typing import Optional
original_eval = builtins.eval
def patched_eval(expr, globals=None, locals=None, *args, **kwargs):
    if globals is None:
        globals = {}
    globals.setdefault("Optional", Optional)
    return original_eval(expr, globals, locals, *args, **kwargs)
builtins.eval = patched_eval' > conftest.py
###ACTION_DELIMITER###
echo -e 'def pytest_sessionstart():
    import napari.view_layers
    from typing import Optional
    napari.view_layers.Optional = Optional' > conftest.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'import builtins\nfrom typing import Optional\nbuiltins.Optional = Optional\nimport pytest\nimport sys\nsys.exit(pytest.main(sys.argv[1:]))' > run_tests.py
###ACTION_DELIMITER###
echo 'xvfb-run -a venv/bin/python run_tests.py -v --no-header -rA --tb=auto -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'def pytest_sessionstart():
    import numpy as np
    np.float = float' > conftest.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install --upgrade tifffile imageio napari-svg zarr
###ACTION_DELIMITER###
venv/bin/pip install --force-reinstall tifffile imageio && venv/bin/pip install zarr==2.16.1 && venv/bin/pip install --upgrade napari-svg
###ACTION_DELIMITER###
venv/bin/pip install --force-reinstall 'imageio[tifffile]'
###ACTION_DELIMITER###
venv/bin/pip install --force-reinstall 'imageio[tifffile]' && apt-get install -y libtiff-dev
###ACTION_DELIMITER###
venv/bin/pip install tifffile==2021.11.2
###ACTION_DELIMITER###
venv/bin/pip install 'tifffile>=2022.8.12' && venv/bin/pip install --force-reinstall 'imageio[tifffile]'
###ACTION_DELIMITER###
echo -e 'def pytest_sessionstart():
    import tifffile
    tifffile.imsave = tifffile.imwrite
    import numpy as np
    np.float = float' > conftest.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install numcodecs==0.15.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install --force-reinstall napari-svg && echo 'import numpy as np
np.int = np.int64' >> conftest.py && venv/bin/pip install scikit-image==0.18.3
###ACTION_DELIMITER###
venv/bin/pip install --upgrade setuptools wheel
###ACTION_DELIMITER###
venv/bin/pip install --force-reinstall napari-svg && venv/bin/pip install scikit-image==0.18.3
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
xvfb-run -a venv/bin/python run_tests.py -v --no-header -rA --tb=auto -p no:cacheprovider

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
xvfb-run -a venv/bin/python run_tests.py -v --no-header -rA --tb=auto -p no:cacheprovider

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
xvfb-run -a venv/bin/python run_tests.py -v --no-header -rA --tb=auto -p no:cacheprovider

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


@Instance.register("napari", "napari_1360_to_1359")
class NAPARI_1360_TO_1359(Instance):
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
        # Parse each line to find test results
        lines = log.split('\n')
        pattern1 = re.compile(r'\[\s*\d+\]\s+(.+?::.+?)\s+(PASSED|FAILED|SKIPPED|SKIP|XFAIL)\s+\[\s*\d+%\]')  # [line] test::name status [percent]
        pattern2 = re.compile(r'\[\s*\d+\]\s+(PASSED|FAILED|SKIPPED|SKIP|XFAIL)\s+(.+?::.+?)(?:\s+[:-].*)?$')  # [line] status test::name
        pattern3 = re.compile(r'^(PASSED|FAILED|SKIPPED|SKIP|XFAIL)\s+(.+?::.+?)(?:\s+[:-].*)?$')  # status test::name
        pattern4 = re.compile(r'\[\s*\d+\]\s+(.+?\.py):\d+:\s+.*')  # Skipped test lines (e.g., [1] test.py:7: ...)
        # Adjust pattern4 to capture test names with optional ::function
        for line in lines:
            match = pattern1.search(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
            else:
                match = pattern2.search(line)
                if match:
                    status = match.group(1)
                    test_name = match.group(2)
                else:
                    match = pattern3.search(line)
                    if match:
                        status = match.group(1)
                        test_name = match.group(2)
                    else:
                        # Check for skipped test lines (e.g., [1] test.py:7: ...)
                        match = pattern4.search(line)
                        if match:
                            test_name = match.group(1)
                            status = 'SKIPPED'
                        else:
                            continue
            # Add to the appropriate set
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status in ('SKIPPED', 'SKIP', 'XFAIL'):
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
