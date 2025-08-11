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
        return "python:3.9-slim-bullseye"
    
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
cat Makefile
###ACTION_DELIMITER###
cat requirements_test.txt
###ACTION_DELIMITER###
cat requirements.txt
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y libosmesa6-dev
###ACTION_DELIMITER###
pip install vtk && pip install -r requirements.txt && pip install -r requirements_test.txt
###ACTION_DELIMITER###
echo 'pytest -v --doctest-modules pyvista tests --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y vtk && pip install vtk==9.2.6
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libxrender1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'PYVISTA_OFF_SCREEN=True PYVISTA_USE_IPYVTK=False pytest -v --doctest-modules pyvista tests --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libgl1-mesa-glx libglu1-mesa && echo 'MESA_GL_VERSION_OVERRIDE=3.3 PYVISTA_OFF_SCREEN=True PYVISTA_USE_IPYVTK=False pytest -v --doctest-modules pyvista tests --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y vtk && pip install vtk-osmesa==9.2.6 && apt-get install -y libxi6 libxrandr2 libxinerama1 libxcursor1 && echo 'export MESA_GL_VERSION_OVERRIDE=3.3; export PYVISTA_OFF_SCREEN=True; export PYVISTA_USE_IPYVTK=False; pytest -v --doctest-modules pyvista tests --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
pip install vtk==9.2.6 && apt-get install -y libglapi-mesa libgles2-mesa libxext6 && echo 'export MESA_GL_VERSION_OVERRIDE=3.3; export PYVISTA_OFF_SCREEN=True; export PYVISTA_USE_IPYVTK=False; pytest -v --doctest-modules pyvista tests --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libx11-6 libxext6 && echo 'MESA_GL_VERSION_OVERRIDE=3.1 PYVISTA_OFF_SCREEN=True PYVISTA_USE_IPYVTK=False pytest -v --doctest-modules pyvista tests --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y vtk && pip install vtk==9.1.0 && echo 'export MESA_GL_VERSION_OVERRIDE=3.1; export MESA_DEBUG=1; export PYVISTA_OFF_SCREEN=True; export PYVISTA_USE_IPYVTK=False; export PYVISTA_RENDERING_BACKEND=osmesa; pytest -v --doctest-modules pyvista tests --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip install vtk==9.1.0 && apt-get install -y libosmesa6-dev libgl1-mesa-dev && echo 'import pyvista; pl = pyvista.Plotter(off_screen=True); pl.add_mesh(pyvista.Cube()); pl.render(); print("Render successful")' > test_render.py && python test_render.py
###ACTION_DELIMITER###
apt-get install -y xvfb && echo 'xvfb-run -a pytest -v --doctest-modules pyvista tests --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run -a pytest -v -n auto --doctest-modules pyvista tests --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run -a pytest -v --doctest-modules pyvista tests/core/test_dataset.py --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'xvfb-run -a pytest -v -n auto --doctest-modules pyvista tests --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
xvfb-run -a pytest -v -n auto --doctest-modules pyvista tests --no-header -rA --tb=no -p no:cacheprovider

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
xvfb-run -a pytest -v -n auto --doctest-modules pyvista tests --no-header -rA --tb=no -p no:cacheprovider

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
xvfb-run -a pytest -v -n auto --doctest-modules pyvista tests --no-header -rA --tb=no -p no:cacheprovider

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim-bullseye with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.9-slim-bullseye

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
RUN git clone https://github.com/pyvista/pyvista.git /home/pyvista

WORKDIR /home/pyvista
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pyvista", "pyvista_5857_to_unknown")
class PYVISTA_5857_TO_UNKNOWN(Instance):
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
        import json
        # Regex pattern to match test lines
        test_pattern = re.compile(r'^(?:\[\s*\d+\]\s+)?(.*?)\s+(PASSED|FAILED|SKIPPED|ERROR)(?:\s+\[.*?\])?$', re.MULTILINE)
        # Find all matches in the log content
        matches = test_pattern.findall(log)
        for test_name, status in matches:
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ('FAILED', 'ERROR'):
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
