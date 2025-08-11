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
apt-get update && apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
pip install flax
###ACTION_DELIMITER###
python3 -m venv venv && venv/bin/pip install flax
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv && venv/bin/pip install flax
###ACTION_DELIMITER###
venv/bin/pip install pytest pytest-xdist tensorflow_datasets
###ACTION_DELIMITER###
echo 'venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pytest -v tests/checkpoints_test.py
###ACTION_DELIMITER###
venv/bin/pip uninstall -y flax && venv/bin/pip install -e .
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip uninstall -y jax jaxlib && venv/bin/pip install jax==0.4.23 jaxlib==0.4.23
###ACTION_DELIMITER###
venv/bin/pip install jax==0.4.27 jaxlib==0.4.27
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pytest -v tests/checkpoints_test.py
###ACTION_DELIMITER###
venv/bin/pip install tensorflow
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install jax==0.5.0 jaxlib==0.5.0 orbax-checkpoint==0.11.20
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip uninstall -y jax jaxlib tensorflow && venv/bin/pip install jax==0.2.25 jaxlib==0.2.25 tensorflow==2.5.0 && venv/bin/pip install -e .
###ACTION_DELIMITER###
venv/bin/pip uninstall -y jax jaxlib tensorflow && venv/bin/pip install jax==0.4.13 jaxlib==0.4.13 tensorflow==2.15.0 && venv/bin/pip install -e .
###ACTION_DELIMITER###
venv/bin/pip install jax==0.4.17 jaxlib==0.4.17 tensorflow==2.15.0 && venv/bin/pip install -e .
###ACTION_DELIMITER###
venv/bin/pip install jax==0.4.17 jaxlib==0.4.17 tensorflow==2.16.0 orbax-checkpoint==0.4.0 && venv/bin/pip install -e .
###ACTION_DELIMITER###
venv/bin/pip install jax==0.4.17 jaxlib==0.4.17 tensorflow==2.16.1 orbax-checkpoint==0.2.0 && venv/bin/pip install -e .
###ACTION_DELIMITER###
venv/bin/pip install jax==0.4.17 jaxlib==0.4.17 tensorflow==2.16.0rc0 orbax-checkpoint==0.2.0 && venv/bin/pip install -e .
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/

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
venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/

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
venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/

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
RUN git clone https://github.com/google/flax.git /home/flax

WORKDIR /home/flax
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("google", "flax_177_to_147")
class FLAX_177_TO_147(Instance):
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
        # Regex pattern to match test names and their statuses
        pattern = r'(tests/[^\s]+) (PASSED|FAILED|SKIPPED)|(PASSED|FAILED|SKIPPED) (tests/[^\s]+)'
        # Find all matches in the log content
        for match in re.finditer(pattern, log):
            # Extract test name and status from the match groups
            test_name = match.group(1) if match.group(1) is not None else match.group(4)
            status = match.group(2) if match.group(2) is not None else match.group(3)
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
