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
                """ls
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3-matplotlib python3-numpy python3-pil python3-scipy python3-tk build-essential cython3
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install numpy
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install cython
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install numpy==1.24.2
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
echo 'pytest -v skimage --doctest-modules' > test_commands.sh
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install numpy==1.19.5
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install numpy==1.23.5
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install --force-reinstall scipy
###ACTION_DELIMITER###
pip uninstall -y numpy && pip install numpy==1.23.5
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y scipy && pip install scipy==1.5.4
###ACTION_DELIMITER###
apt-get update && apt-get install -y libopenblas-dev liblapack-dev
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v skimage --doctest-modules --filterwarnings "ignore:np.float is a deprecated alias:DeprecationWarning" --filterwarnings "ignore:np.bool is a deprecated alias:DeprecationWarning" --filterwarnings "ignore:Converting np.inexact:DeprecationWarning"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'export PYTHONWARNINGS="ignore:np.float is a deprecated alias:DeprecationWarning,ignore:np.bool is a deprecated alias:DeprecationWarning,ignore:Converting np.inexact:DeprecationWarning" && pytest -v skimage --doctest-modules' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
export PYTHONWARNINGS="ignore:np.float is a deprecated alias:DeprecationWarning,ignore:np.bool is a deprecated alias:DeprecationWarning,ignore:Converting np.inexact:DeprecationWarning" && pytest -v skimage --doctest-modules

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
export PYTHONWARNINGS="ignore:np.float is a deprecated alias:DeprecationWarning,ignore:np.bool is a deprecated alias:DeprecationWarning,ignore:Converting np.inexact:DeprecationWarning" && pytest -v skimage --doctest-modules

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
export PYTHONWARNINGS="ignore:np.float is a deprecated alias:DeprecationWarning,ignore:np.bool is a deprecated alias:DeprecationWarning,ignore:Converting np.inexact:DeprecationWarning" && pytest -v skimage --doctest-modules

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
RUN git clone https://github.com/scikit-image/scikit-image.git /home/scikit-image

WORKDIR /home/scikit-image
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("scikit-image", "scikit_image_2761_to_2754")
class SCIKIT_IMAGE_2761_TO_2754(Instance):
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
        # Regex patterns to match test lines
        # Pattern 1: Test name followed by status and [percentage]
        pattern1 = re.compile(r'^(.+?)\s+(PASSED|FAILED|SKIPPED)\s+\[.*?\]$')
        # Pattern 2: Status followed by test name, optional trailing info
        pattern2 = re.compile(r'^(PASSED|FAILED|SKIPPED)\s+(.+?)(\s+-.*)?$')
        for line in log.splitlines():
            line = line.strip()
            if not line:
                continue
            # Check pattern1
            match = pattern1.match(line)
            if match:
                test_name = match.group(1).strip()
                status = match.group(2)
            else:
                # Check pattern2
                match = pattern2.match(line)
                if match:
                    status = match.group(1)
                    test_name = match.group(2).strip()
                else:
                    # No match, skip
                    continue
            # Add to the appropriate set
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
