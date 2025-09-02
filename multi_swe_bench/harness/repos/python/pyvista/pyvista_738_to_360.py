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
                """apt-get update && apt-get install -y libgl1-mesa-glx libxrender1 libxt6 libxext6
###ACTION_DELIMITER###
pip install vtk
###ACTION_DELIMITER###
sed -i 's/PyQt5==5.11.3/PyQt5==5.15.6/' requirements_test.txt
###ACTION_DELIMITER###
pip install -r requirements_test.txt
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
python -m pytest -v --cov pyvista
python -m pytest -v --doctest-modules pyvista' > /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
chmod +x /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
bash /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libglib2.0-0
###ACTION_DELIMITER###
bash /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y vtk && pip install vtk==9.2.0
###ACTION_DELIMITER###
pip uninstall -y vtk && pip install vtk==9.2.2
###ACTION_DELIMITER###
bash /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install numpy==1.26.0
###ACTION_DELIMITER###
bash /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install numpy==1.19.5
###ACTION_DELIMITER###
pip uninstall -y matplotlib contourpy && pip install matplotlib==3.5.3 contourpy==1.0.5
###ACTION_DELIMITER###
bash /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y xvfb && sed -i 's/python -m pytest/xvfb-run -a python -m pytest/' /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
bash /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/^set -e/set -e\nexport DISPLAY=:99\nexport HYPOTHESIS_DEADLINE=60000/' /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
bash /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/^export DISPLAY=:99/export DISPLAY=:99\nXvfb :99 -screen 0 1024x768x16 &\nsleep 2/' /home/pyvista/test_commands.sh && echo 'export HYPOTHESIS_IGNORE_HEALTH_CHECKS=yes' >> /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
bash /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
sed -i '/^export DISPLAY=:99/a Xvfb :99 -screen 0 1024x768x16 &\nsleep 2' /home/pyvista/test_commands.sh && sed -i 's/^Xvfb :99 -screen 0 1024x768x16 &//' /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
export HYPOTHESIS_DEADLINE=60000
export HYPOTHESIS_IGNORE_HEALTH_CHECKS=yes
xvfb-run -a python -m pytest -v --cov pyvista
xvfb-run -a python -m pytest -v --doctest-modules pyvista' > /home/pyvista/test_commands.sh && chmod +x /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
bash /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y vtk && pip install vtk==9.0.3
###ACTION_DELIMITER###
bash /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
export HYPOTHESIS_DEADLINE=60000
export HYPOTHESIS_IGNORE_HEALTH_CHECKS=yes
xvfb-run -a python -m pytest -v --doctest-modules pyvista tests' > /home/pyvista/test_commands.sh && chmod +x /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y pytest && pip install pytest==6.2.5
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
export HYPOTHESIS_DEADLINE=60000
export HYPOTHESIS_IGNORE_HEALTH_CHECKS=yes
xvfb-run -a python -m pytest -v tests' > /home/pyvista/test_commands.sh && chmod +x /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y vtk && pip install vtk==9.1.0 && pip install -e . && echo -e '#!/bin/bash
set -e
export HYPOTHESIS_DEADLINE=60000
export HYPOTHESIS_IGNORE_HEALTH_CHECKS=yes
xvfb-run -a python -m pytest -v tests' > /home/pyvista/test_commands.sh && chmod +x /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/>=3.5.*/>=3.5/' setup.py
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
sed -i '69s/.*/    python_requires='\''>=3.5'\'',/' setup.py
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
bash /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y vtk && pip install vtk==9.0.1 && sed -i '1i import pyvista\npyvista.OFF_SCREEN = True\npyvista.start_xvfb()' /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y vtk && pip install vtk==9.0.2 && sed -i '1i import pyvista\npyvista.OFF_SCREEN = True\npyvista.start_xvfb()' /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
bash /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
python -c "import pyvista; pyvista.OFF_SCREEN = True; pyvista.start_xvfb()"
export HYPOTHESIS_DEADLINE=60000
export HYPOTHESIS_IGNORE_HEALTH_CHECKS=yes
xvfb-run -a python -m pytest -v tests' > /home/pyvista/test_commands.sh && chmod +x /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
bash /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
python -c "import pyvista; pyvista.OFF_SCREEN = True"
export HYPOTHESIS_DEADLINE=60000
export HYPOTHESIS_IGNORE_HEALTH_CHECKS=yes
xvfb-run -a python -m pytest -v tests' > /home/pyvista/test_commands.sh && chmod +x /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
bash /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
python -c "import pyvista; pyvista.OFF_SCREEN = True"
export HYPOTHESIS_DEADLINE=60000
export HYPOTHESIS_IGNORE_HEALTH_CHECKS=yes
xvfb-run -a python -m pytest -v tests -k "not test_plot_over_line"' > /home/pyvista/test_commands.sh && chmod +x /home/pyvista/test_commands.sh
###ACTION_DELIMITER###
bash /home/pyvista/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
set -e
python -c "import pyvista; pyvista.OFF_SCREEN = True"
export HYPOTHESIS_DEADLINE=60000
export HYPOTHESIS_IGNORE_HEALTH_CHECKS=yes
xvfb-run -a python -m pytest -v tests -k "not test_plot_over_line"

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
set -e
python -c "import pyvista; pyvista.OFF_SCREEN = True"
export HYPOTHESIS_DEADLINE=60000
export HYPOTHESIS_IGNORE_HEALTH_CHECKS=yes
xvfb-run -a python -m pytest -v tests -k "not test_plot_over_line"

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
set -e
python -c "import pyvista; pyvista.OFF_SCREEN = True"
export HYPOTHESIS_DEADLINE=60000
export HYPOTHESIS_IGNORE_HEALTH_CHECKS=yes
xvfb-run -a python -m pytest -v tests -k "not test_plot_over_line"

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
RUN git clone https://github.com/pyvista/pyvista.git /home/pyvista

WORKDIR /home/pyvista
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pyvista", "pyvista_738_to_360")
class PYVISTA_738_TO_360(Instance):
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
        import json
        test_pattern = re.compile(r'(tests/[^:]+::[^ ]+)\s+(PASSED|FAILED|SKIPPED)|(PASSED|FAILED|SKIPPED)\s+(tests/[^:]+::[^ ]+)')
        matches = test_pattern.findall(log)
        for match in matches:
            test_name = match[0] if match[0] else match[3]
            status = match[1] if match[1] else match[2]
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
