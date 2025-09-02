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
                """apt-get update && apt-get install -y python3 python3-pip python3-distutils python3.12-venv wget gnupg
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip python3-setuptools python3.12-venv wget gnupg
###ACTION_DELIMITER###
python3 -m venv venv && source venv/bin/activate && pip3 install -r requirements.txt
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
pytest -v --doctest-modules nipype' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip3 install setuptools
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from collections import Iterator/from collections.abc import Iterator/' nipype/utils/misc.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from traits.trait_handlers import TraitDictObject, TraitListObject/from traits.trait_handlers import trait_dict_object as TraitDictObject, trait_list_object as TraitListObject/' nipype/interfaces/base/traits_extension.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip3 install traits==6.3.2
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from traits.trait_handlers import trait_dict_object as TraitDictObject, trait_list_object as TraitListObject/from traits.trait_handlers import TraitDictObject, TraitListObject/' nipype/interfaces/base/traits_extension.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
wget -q -O /etc/apt/trusted.gpg.d/neurodebian.gpg https://neurodebian.net/_static/neurodebian.gpg && echo 'deb http://neurodebian.net/debian noble main' > /etc/apt/sources.list.d/neurodebian.list && apt-get update && apt-get install -y fsl-core mrtrix3 ants
###ACTION_DELIMITER###
wget -q -O /etc/apt/trusted.gpg.d/neurodebian.gpg https://neurodebian.net/_static/neurodebian.gpg && echo 'deb http://neurodebian.net/debian jammy main' > /etc/apt/sources.list.d/neurodebian.list && apt-get update && apt-get install -y mrtrix3
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
pytest -v --doctest-modules -k "not mrtrix and not fsl and not ants" nipype' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
source venv/bin/activate
pytest -v --doctest-modules -k "not mrtrix and not fsl and not ants" nipype

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
source venv/bin/activate
pytest -v --doctest-modules -k "not mrtrix and not fsl and not ants" nipype

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
source venv/bin/activate
pytest -v --doctest-modules -k "not mrtrix and not fsl and not ants" nipype

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
RUN git clone https://github.com/nipy/nipype.git /home/nipype

WORKDIR /home/nipype
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("nipy", "nipype_2533_to_2476")
class NIPYPE_2533_TO_2476(Instance):
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
        # Regex pattern to match test status lines
        # Pattern matches lines like "[gw3] [  0%] PASSED test_name"
        pattern = r'(?:\[\s*\d+\]\s+)?(?:\[gw\d+\]\s+\[\s*\d+%\]\s+)?(PASSED|FAILED|SKIPPED|XFAILED|ERROR)\s+([\w\/]+\.py::[\w_.]+(?:::[\w_.]+)*)'
        matches = re.finditer(pattern, log)
        test_status = {}
        for match in matches:
            status = match.group(1)
            test_name = match.group(2).strip()
            test_status[test_name] = status  # Overwrite with latest status
        for test_name, status in test_status.items():
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ('FAILED', 'XFAILED', 'ERROR'):
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
