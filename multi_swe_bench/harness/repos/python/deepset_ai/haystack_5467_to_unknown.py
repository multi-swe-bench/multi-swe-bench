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
                """pip install -e '.[dev]'
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install scikit-learn
###ACTION_DELIMITER###
pip install scikit-learn==1.3.0
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install numpy==1.26.0
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install 'farm-haystack[inference]'
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install 'farm-haystack[all]'
###ACTION_DELIMITER###
pip install 'farm-haystack[audio, docstores]'
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install 'farm-haystack[crawler, ray]'
###ACTION_DELIMITER###
pip install 'farm-haystack[preprocessing]'
###ACTION_DELIMITER###
pip install weaviate-client==3.18.0
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install 'farm-haystack[pdf]'
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
ls -l rest_api/test/
###ACTION_DELIMITER###
touch rest_api/__init__.py
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install httpx
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
ls -l rest_api/
###ACTION_DELIMITER###
ls -l rest_api/rest_api/
###ACTION_DELIMITER###
sed -i 's/from rest_api.pipeline/from rest_api.rest_api.pipeline/' rest_api/test/test_rest_api.py
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
sed -i 's/from rest_api.controller/from rest_api.rest_api.controller/' rest_api/rest_api/pipeline/__init__.py
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
sed -i 's/from rest_api.pipeline/from ..pipeline/' rest_api/rest_api/controller/__init__.py
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
sed -i 's/from rest_api.utils/from rest_api.rest_api.utils/' rest_api/test/test_rest_api.py
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
sed -i 's/from rest_api.pipeline/from .pipeline/' rest_api/rest_api/utils.py
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
sed -i 's/from rest_api.controller/from .controller/' rest_api/rest_api/utils.py
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
echo 'pytest -v -n auto' > /home/haystack/test_commands.sh
###ACTION_DELIMITER###
pip install pytest-xdist
###ACTION_DELIMITER###
bash /home/haystack/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v -n auto

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
pytest -v -n auto

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
pytest -v -n auto

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
RUN git clone https://github.com/deepset-ai/haystack.git /home/haystack

WORKDIR /home/haystack
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("deepset-ai", "haystack_5467_to_unknown")
class HAYSTACK_5467_TO_UNKNOWN(Instance):
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
        pass
