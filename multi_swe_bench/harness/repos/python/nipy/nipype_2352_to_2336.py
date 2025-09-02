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

###ACTION_DELIMITER###
pip install .[tests]
###ACTION_DELIMITER###
echo 'pytest -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install traits==6.3.2
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.19.5
###ACTION_DELIMITER###
pip install numpy==1.22.4
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y numpy scipy nibabel && pip install numpy==1.19.5 scipy==1.6.3 nibabel==3.2.2
###ACTION_DELIMITER###
pip install --force-reinstall numpy==1.19.5 && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y numpy scipy && pip install numpy==1.18.5 scipy==1.4.1 nibabel==3.2.2 && bash test_commands.sh
###ACTION_DELIMITER###
pip install --only-binary numpy numpy==1.19.5 scipy==1.6.3 nibabel==3.2.2 && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y numpy scipy && pip install --only-binary numpy numpy==1.18.5 scipy==1.4.1 nibabel==3.2.2 && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential && pip install --upgrade setuptools wheel && pip install numpy==1.18.5 scipy==1.4.1 nibabel==3.2.2 && bash test_commands.sh
###ACTION_DELIMITER###
pip install setuptools==44.0.0 && pip install numpy==1.18.5 scipy==1.4.1 nibabel==3.2.2 && bash test_commands.sh
###ACTION_DELIMITER###
pip install setuptools==50.0.0 && pip install --no-use-pep517 numpy==1.18.5 scipy==1.4.1 nibabel==3.2.2 && bash test_commands.sh
###ACTION_DELIMITER###
pip install cython && pip install setuptools==50.0.0 && pip install numpy==1.18.5 scipy==1.4.1 nibabel==3.2.2 && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y python3-dev && pip install setuptools==41.0.0 && pip install --no-use-pep517 numpy==1.18.5 scipy==1.4.1 nibabel==3.2.2 && bash test_commands.sh
###ACTION_DELIMITER###
pip install setuptools==58.0.0 && pip install numpy==1.19.5 scipy==1.6.3 nibabel==3.2.2 traits==6.3.2 pytest==7.0.0 && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential python3-dev cython && pip install numpy==1.18.5 --no-binary numpy && pip install scipy==1.4.1 nibabel==3.2.2 traits==6.3.2 && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential python3-dev cython3 && pip install numpy==1.18.5 --no-binary numpy && pip install scipy==1.4.1 nibabel==3.2.2 traits==6.3.2 && bash test_commands.sh
###ACTION_DELIMITER###
pip install setuptools==50.0.0 && pip install numpy==1.19.5 scipy==1.6.3 nibabel==3.2.2 traits==6.3.2 pytest==7.0.0 && bash test_commands.sh
###ACTION_DELIMITER###
echo 'python -c "import nipype; nipype.test(args=[\"-v\"])"' > test_commands.sh && pip install numpy==1.19.5 scipy==1.6.3 nibabel==3.2.2 traits==6.3.2 && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip install -r requirements.txt && pip install .[tests] && bash test_commands.sh
###ACTION_DELIMITER###
pip install --force-reinstall numpy==1.19.5 && bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.17.5 && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v

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
pytest -v

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
pytest -v

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
RUN git clone https://github.com/nipy/nipype.git /home/nipype

WORKDIR /home/nipype
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("nipy", "nipype_2352_to_2336")
class NIPYPE_2352_TO_2336(Instance):
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
        passed_tests = set() # Tests that passed successfully
        failed_tests = set() # Tests that failed
        skipped_tests = set() # Tests that were skipped
        import re
        import json
        # Regex patterns to match test status lines
        # Revised regex patterns to match test status lines
        passed_pattern = re.compile(r'(\S+)\s+PASSED\s+\[\s*\d+%\]')
        skipped_pattern = re.compile(r'(\S+)\s+SKIPPED\s+\[\s*\d+%\]')
        failed_pattern = re.compile(r'(?:FAILED|ERROR)\s+(\S+)')
        # Extract test names using the patterns
        passed_tests = set(passed_pattern.findall(log))
        skipped_tests = set(skipped_pattern.findall(log))
        failed_tests = set(failed_pattern.findall(log))
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
