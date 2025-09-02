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
                """ls -la
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
pip install -e ".[tests]"
###ACTION_DELIMITER###
pip install -e ".[tests]" --break-system-packages
###ACTION_DELIMITER###
echo 'pytest -v' > /home/optuna/test_commands.sh
###ACTION_DELIMITER###
cat /home/optuna/test_commands.sh
###ACTION_DELIMITER###
bash /home/optuna/test_commands.sh
###ACTION_DELIMITER###
pip list | grep pytest
###ACTION_DELIMITER###
pip install pytest --break-system-packages
###ACTION_DELIMITER###
bash /home/optuna/test_commands.sh
###ACTION_DELIMITER###
pip install mock --break-system-packages
###ACTION_DELIMITER###
bash /home/optuna/test_commands.sh
###ACTION_DELIMITER###
pip install pandas --break-system-packages
###ACTION_DELIMITER###
bash /home/optuna/test_commands.sh
###ACTION_DELIMITER###
pip install scikit-learn --break-system-packages
###ACTION_DELIMITER###
pip install lightgbm --break-system-packages
###ACTION_DELIMITER###
pip install -e ".[test]" --break-system-packages
###ACTION_DELIMITER###
pip install -e ".[testing]" --break-system-packages
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.8 python3.8-venv
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.8 python3.8-venv
###ACTION_DELIMITER###
echo 'pytest -v --ignore tests/integration_tests/test_chainer.py --ignore tests/integration_tests/test_cma.py --ignore tests/integration_tests/test_fastai.py --ignore tests/integration_tests/test_keras.py --ignore tests/integration_tests/test_mxnet.py --ignore tests/integration_tests/test_pytorch_ignite.py --ignore tests/integration_tests/test_pytorch_lightning.py --ignore tests/integration_tests/test_skopt.py --ignore tests/integration_tests/test_tensorflow.py --ignore tests/integration_tests/test_tfkeras.py --ignore tests/integration_tests/test_xgboost.py' > /home/optuna/test_commands.sh
###ACTION_DELIMITER###
bash /home/optuna/test_commands.sh
###ACTION_DELIMITER###
pip install plotly --break-system-packages
###ACTION_DELIMITER###
bash /home/optuna/test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --ignore tests/integration_tests/test_chainer.py --ignore tests/integration_tests/test_cma.py --ignore tests/integration_tests/test_fastai.py --ignore tests/integration_tests/test_keras.py --ignore tests/integration_tests/test_mxnet.py --ignore tests/integration_tests/test_pytorch_ignite.py --ignore tests/integration_tests/test_pytorch_lightning.py --ignore tests/integration_tests/test_skopt.py --ignore tests/integration_tests/test_tensorflow.py --ignore tests/integration_tests/test_tfkeras.py --ignore tests/integration_tests/test_xgboost.py --ignore tests/test_study.py --ignore tests/test_trial.py' > /home/optuna/test_commands.sh
###ACTION_DELIMITER###
bash /home/optuna/test_commands.sh
###ACTION_DELIMITER###
pip install git+https://github.com/automl/fanova.git --break-system-packages
###ACTION_DELIMITER###
apt-get update && apt-get install -y swig
###ACTION_DELIMITER###
pip install git+https://github.com/automl/fanova.git --break-system-packages
###ACTION_DELIMITER###
echo 'pytest -v' > /home/optuna/test_commands.sh
###ACTION_DELIMITER###
bash /home/optuna/test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --ignore tests/integration_tests/test_chainer.py --ignore tests/integration_tests/test_cma.py --ignore tests/integration_tests/test_fastai.py --ignore tests/integration_tests/test_keras.py --ignore tests/integration_tests/test_mxnet.py --ignore tests/integration_tests/test_pytorch_ignite.py --ignore tests/integration_tests/test_pytorch_lightning.py --ignore tests/integration_tests/test_skopt.py --ignore tests/integration_tests/test_tensorflow.py --ignore tests/integration_tests/test_tfkeras.py --ignore tests/integration_tests/test_xgboost.py' > /home/optuna/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v --ignore tests/integration_tests/test_chainer.py --ignore tests/integration_tests/test_cma.py --ignore tests/integration_tests/test_fastai.py --ignore tests/integration_tests/test_keras.py --ignore tests/integration_tests/test_mxnet.py --ignore tests/integration_tests/test_pytorch_ignite.py --ignore tests/integration_tests/test_pytorch_lightning.py --ignore tests/integration_tests/test_skopt.py --ignore tests/integration_tests/test_tensorflow.py --ignore tests/integration_tests/test_tfkeras.py --ignore tests/integration_tests/test_xgboost.py

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
pytest -v --ignore tests/integration_tests/test_chainer.py --ignore tests/integration_tests/test_cma.py --ignore tests/integration_tests/test_fastai.py --ignore tests/integration_tests/test_keras.py --ignore tests/integration_tests/test_mxnet.py --ignore tests/integration_tests/test_pytorch_ignite.py --ignore tests/integration_tests/test_pytorch_lightning.py --ignore tests/integration_tests/test_skopt.py --ignore tests/integration_tests/test_tensorflow.py --ignore tests/integration_tests/test_tfkeras.py --ignore tests/integration_tests/test_xgboost.py

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
pytest -v --ignore tests/integration_tests/test_chainer.py --ignore tests/integration_tests/test_cma.py --ignore tests/integration_tests/test_fastai.py --ignore tests/integration_tests/test_keras.py --ignore tests/integration_tests/test_mxnet.py --ignore tests/integration_tests/test_pytorch_ignite.py --ignore tests/integration_tests/test_pytorch_lightning.py --ignore tests/integration_tests/test_skopt.py --ignore tests/integration_tests/test_tensorflow.py --ignore tests/integration_tests/test_tfkeras.py --ignore tests/integration_tests/test_xgboost.py

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
RUN git clone https://github.com/optuna/optuna.git /home/optuna

WORKDIR /home/optuna
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("optuna", "optuna_1077_to_44")
class OPTUNA_1077_TO_44(Instance):
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
        # Define regex patterns to match test lines
        # Pattern 1: Matches lines like 'tests/... PASSED [ 0%]'
        pattern1 = re.compile(r'^(tests/.*?)\s+(PASSED|FAILED|SKIPPED)\s+\[')
        # Pattern 2: Matches lines like 'FAILED tests/...' (ignores trailing error messages)
        pattern2 = re.compile(r'^(PASSED|FAILED|SKIPPED)\s+(tests/.*?)(\s+-.*)?$')
        # Split log into lines
        lines = log.split('\n')
        for line in lines:
            line = line.strip()
            match1 = pattern1.match(line)
            if match1:
                test_name = match1.group(1).strip()
                status = match1.group(2)
            else:
                match2 = pattern2.match(line)
                if match2:
                    status = match2.group(1)
                    test_name = match2.group(2).strip()
                else:
                    continue  # No match, skip
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
