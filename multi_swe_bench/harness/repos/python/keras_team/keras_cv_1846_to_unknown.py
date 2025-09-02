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
                """pip install .[tests]
###ACTION_DELIMITER###
echo 'pytest -v keras_cv/' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install keras==2.15.0
###ACTION_DELIMITER###
pip install tensorflow==2.15.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install --force-reinstall keras==2.15.0
###ACTION_DELIMITER###
pip uninstall -y keras
###ACTION_DELIMITER###
pip install --force-reinstall keras==2.15.0
###ACTION_DELIMITER###
pip install keras-preprocessing
###ACTION_DELIMITER###
pip install --no-cache-dir --force-reinstall keras==2.15.0
###ACTION_DELIMITER###
pip uninstall -y keras && bash test_commands.sh
###ACTION_DELIMITER###
pip install keras==2.15.0 && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y keras && pip install tensorflow==2.16.0 keras==3.3.3 && bash test_commands.sh
###ACTION_DELIMITER###
pip install --upgrade pip && pip install tensorflow==2.16.1 keras==3.3.3 && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y keras && pip install --force-reinstall keras-preprocessing && export KERAS_BACKEND=tensorflow && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y numpy ml_dtypes tensorflow keras && pip install tensorflow==2.15.0 numpy==1.26.4 keras-preprocessing && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y keras && pip install --no-cache-dir tensorflow==2.15.0 && export KERAS_BACKEND=tensorflow && bash test_commands.sh
###ACTION_DELIMITER###
pip install --force-reinstall keras==2.15.0 && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y keras && export KERAS_BACKEND=tensorflow && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y keras && pip install tensorflow-keras && bash test_commands.sh
###ACTION_DELIMITER###
pip install tensorflow==2.3.0 keras==2.3.1 keras-preprocessing && bash test_commands.sh
###ACTION_DELIMITER###
pip install tensorflow==2.10.0 keras==2.10.0 keras-preprocessing && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y keras tensorflow && pip install tensorflow==2.11.0 keras-preprocessing && bash test_commands.sh
###ACTION_DELIMITER###
pip install --force-reinstall protobuf==3.19.6 tensorflow-datasets==4.9.3 && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y tensorflow protobuf && pip install tensorflow==2.12.0 protobuf>=3.20.0 tensorflow-datasets==4.9.3 && bash test_commands.sh
###ACTION_DELIMITER###
echo 'ABSL_FLAGS_verbosity=1 pytest -v keras_cv/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'ABSL_FLAGS_verbosity=1 pytest -v -- keras_cv/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'python -c "from absl import flags; flags.FLAGS.verbosity = 1" && pytest -v keras_cv/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'python -c "import tensorflow as tf; from absl import flags; flags.FLAGS.verbosity = 1" && pytest -v keras_cv/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e "from absl import flags
import sys
import pytest
flags.FLAGS.verbosity = 1
flags.FLAGS.mark_as_parsed()
sys.exit(pytest.main(sys.argv[1:]))" > run_tests.py && echo 'python run_tests.py -v keras_cv/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e "import tensorflow as tf
from absl import flags
import sys
import pytest
flags.FLAGS.verbosity = 1
flags.FLAGS.mark_as_parsed()
sys.exit(pytest.main(sys.argv[1:]))" > run_tests.py && echo 'python run_tests.py -v keras_cv/' > test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python run_tests.py -v keras_cv/

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
python run_tests.py -v keras_cv/

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
python run_tests.py -v keras_cv/

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
RUN git clone https://github.com/keras-team/keras-cv.git /home/keras-cv

WORKDIR /home/keras-cv
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("keras-team", "keras-cv_1846_to_unknown")
class KERAS_CV_1846_TO_UNKNOWN(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        # Implement the log parsing logic here
        # Regex patterns to match test status lines
        passed_pattern = re.compile(r'^PASSED\s+(.*)$', re.MULTILINE)
        failed_pattern = re.compile(r'^FAILED\s+(.*)$', re.MULTILINE)
        skipped_pattern = re.compile(r'^SKIPPED\s+\[\d+\]\s+(.*?):', re.MULTILINE)
        # Extract test names from log
        passed_tests.update(passed_pattern.findall(log))
        failed_tests.update(failed_pattern.findall(log))
        skipped_tests.update(skipped_pattern.findall(log))
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
