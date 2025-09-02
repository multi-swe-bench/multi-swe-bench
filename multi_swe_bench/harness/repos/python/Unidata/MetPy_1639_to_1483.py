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
                """apt-get update && apt-get install -y python3 python3-venv python3-pip build-essential libproj-dev proj-bin
###ACTION_DELIMITER###
python3 -m venv venv && source venv/bin/activate && pip install -e ".[test]"
###ACTION_DELIMITER###
cat setup.cfg
###ACTION_DELIMITER###
sed -i 's/pyproj>=2.3.0,<3.0/pyproj>=2.3.0/' setup.cfg
###ACTION_DELIMITER###
source venv/bin/activate && pip install -e ".[test]"
###ACTION_DELIMITER###
echo 'venv/bin/pytest -v -rA' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install pint==0.18 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install numpy==1.24.0 && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y python3-distutils && source venv/bin/activate && pip install numpy==1.24.0 && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y python3.12-distutils && source venv/bin/activate && pip install numpy==1.24.0 && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y python3-setuptools && source venv/bin/activate && pip install --upgrade setuptools && pip install numpy==1.24.0 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install setuptools==68.0.0 && pip install numpy==1.26.0 pint==0.19 && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pooch\.version\.full_version/pooch\.__version__/g' conftest.py && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/dtype=np.bool/dtype=bool/g' tests/calc/test_calc_tools.py && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install matplotlib==3.7.0 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install matplotlib==3.6.0 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install matplotlib==3.5.3 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install pytest-mpl==0.15.1 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install matplotlib==3.4.3 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install matplotlib==3.8.0 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install matplotlib==3.3.4 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install matplotlib==3.5.3 pytest-mpl==0.16.0 && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export MPLBACKEND=Agg
venv/bin/pytest -v -rA' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install matplotlib==3.7.0 pytest-mpl==0.17.0 && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install matplotlib==3.2.2 numpy==1.21.6 && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install --upgrade setuptools && pip install numpy==1.26.0 pint==0.19 matplotlib==3.7.0 pytest-mpl==0.17.0 pyproj>=2.3.0 && pip install -e ".[test]" && echo -e 'source venv/bin/activate
pytest -v -rA' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install setuptools==68.0.0 numpy==1.26.0 pint==0.19 matplotlib==3.5.3 pytest-mpl==0.16.0 pyproj==3.7.1 && pip install -e ".[test]" && echo -e 'source venv/bin/activate
pytest -v -rA' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libfreetype6-dev && rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install setuptools==68.0.0 numpy==1.26.0 pint==0.19 matplotlib==3.7.0 pytest-mpl==0.17.0 pyproj==3.7.1 && pip install -e ".[test]" && echo -e 'source venv/bin/activate
pytest -v -rA' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install setuptools==68.0.0 numpy==1.26.0 pint==0.19 matplotlib==3.6.0 pytest-mpl==0.16.0 pyproj==3.7.1 && pip install -e ".[test]" && echo -e 'source venv/bin/activate
pytest -v -rA' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libfreetype6-dev libpng-dev libjpeg-dev libopenjp2-7-dev libtiff-dev libxcb1-dev libxcb-render0-dev libxcb-shape0-dev libxcb-randr0-dev && rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install setuptools==68.0.0 numpy==1.26.0 pint==0.19 matplotlib==3.7.0 pytest-mpl==0.17.0 pyproj==3.7.1 && pip install -e ".[test]" && echo -e 'export MPLBACKEND=Agg
source venv/bin/activate
pytest -v -rA' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install setuptools==68.0.0 numpy==1.26.0 pint==0.20 matplotlib==3.7.3 pytest-mpl==0.17.0 pyproj==3.7.1 && pip install -e ".[test]" && echo -e 'export MPLBACKEND=Agg
source venv/bin/activate
pytest -v -rA' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install setuptools==68.0.0 numpy==1.26.0 pint==0.19 matplotlib==3.7.3 pytest-mpl==0.17.0 pyproj==3.7.1 && pip install -e ".[test]" && echo -e 'export MPLBACKEND=Agg
source venv/bin/activate
pytest -v -rA' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install setuptools==68.0.0 numpy==1.26.0 pint==0.19 matplotlib==3.7.3 pytest-mpl==0.17.0 pyproj==3.7.1 cartopy==0.24.0 && pip install -e ".[test]" && echo -e 'export MPLBACKEND=Agg
source venv/bin/activate
pytest -v -rA' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install setuptools==68.0.0 numpy==1.26.0 pint==0.19 matplotlib==3.7.3 pytest-mpl==0.17.0 pyproj==3.7.1 cartopy==0.24.0 && pip install -e ".[test]" && echo -e 'export MPLBACKEND=Agg
source venv/bin/activate
pytest -v -rA --mpl' > test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
export MPLBACKEND=Agg
source venv/bin/activate
pytest -v -rA --mpl

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
export MPLBACKEND=Agg
source venv/bin/activate
pytest -v -rA --mpl

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
export MPLBACKEND=Agg
source venv/bin/activate
pytest -v -rA --mpl

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
RUN git clone https://github.com/Unidata/MetPy.git /home/MetPy

WORKDIR /home/MetPy
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Unidata", "MetPy_1639_to_1483")
class METPY_1639_TO_1483(Instance):
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
        # Regex patterns to match test lines
        # Pattern 1: test name followed by status (e.g., "tests/...::test... PASSED [  0%]")
        pattern1 = re.compile(r'^(tests/[^:]+::test[\w\-\[\]_]+) (PASSED|FAILED|SKIPPED) \[\s*\d+%\]')
        # Pattern 2: status followed by test name (e.g., "FAILED tests/...::test... - ...")
        pattern2 = re.compile(r'^(PASSED|FAILED|SKIPPED) (tests/[^:]+::test[\w\-\[\]_]+) -')
        for line in log.splitlines():
            # Check pattern 1
            match = pattern1.match(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
                continue  # Move to next line
            # Check pattern 2
            match = pattern2.match(line)
            if match:
                status = match.group(1)
                test_name = match.group(2)
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
                elif status == 'SKIPPED':
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
