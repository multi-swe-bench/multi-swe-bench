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
        repo_name= self.pr.repo
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
node -v
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y nodejs npm
###ACTION_DELIMITER###
node -v && npm -v
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip python-is-python3
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
apt-get install -y python2.7
###ACTION_DELIMITER###
apt-get install -y python2
###ACTION_DELIMITER###
npm install -g node-gyp@latest
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
yarn add node-sass@7.0.1
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
npm run test-client -- --verbose
npm run test-app -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgtk2.0-0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libxss1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgconf-2-4
###ACTION_DELIMITER###
yarn add node-sass@8.0.0
###ACTION_DELIMITER###
add-apt-repository universe && apt-get update && apt-get install -y libgconf-2-4
###ACTION_DELIMITER###
apt-get install -y software-properties-common && add-apt-repository universe && apt-get update && apt-get install -y libgconf-2-4
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
yarn remove node-sass && yarn add sass
###ACTION_DELIMITER###
add-apt-repository universe && apt-get update && apt-get install -y libgconf-2-4 libgtk2.0-0 libxss1 libnss3 libasound2
###ACTION_DELIMITER###
apt-get update && apt-get install -y libxss1 libnss3 libasound2 libgtk-3-0
###ACTION_DELIMITER###
apt-get install -y libxss1 libnss3 libasound2t64 libgtk-3-0t64
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
yarn add node-sass@8.0.0
###ACTION_DELIMITER###
sed -i 's/^deb http:\/\/archive\.ubuntu\.com\/ubuntu\/ noble main$/deb http:\/\/archive\.ubuntu\.com\/ubuntu\/ noble main universe/' /etc/apt/sources.list
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgconf-2-4
###ACTION_DELIMITER###
yarn add node-sass@4.14.1 && apt-get update && apt-get install -y libgconf-2-4
###ACTION_DELIMITER###
npm config set python python3 && npm rebuild node-sass
###ACTION_DELIMITER###
npm install -g node-gyp@latest && export PYTHON=python3 && npm rebuild node-sass
###ACTION_DELIMITER###
add-apt-repository universe && apt-get update && apt-get install -y python2.7 && npm config set python python2.7 && npm rebuild node-sass
###ACTION_DELIMITER###
sed -i 's/^deb http:\/\/archive\.ubuntu\.com\/ubuntu\/ noble main$/deb http:\/\/archive\.ubuntu\.com\/ubuntu\/ noble main universe/' /etc/apt/sources.list && apt-get update
###ACTION_DELIMITER###
apt-get install -y libgconf-2-4"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e
npm run test-client -- --verbose
npm run test-app -- --verbose

""".replace("[[REPO_NAME]]", repo_name)
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
if ! git -C /home/[[REPO_NAME]] apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
#!/bin/bash
set -e
npm run test-client -- --verbose
npm run test-app -- --verbose

""".replace("[[REPO_NAME]]", repo_name)
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
if ! git -C /home/[[REPO_NAME]] apply --whitespace=nowarn  /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
#!/bin/bash
set -e
npm run test-client -- --verbose
npm run test-app -- --verbose

""".replace("[[REPO_NAME]]", repo_name)
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
RUN git clone https://github.com/Azure/BatchExplorer.git /home/BatchExplorer

WORKDIR /home/BatchExplorer
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Azure", "BatchExplorer_755_to_unknown")
class BATCHEXPLORER_755_TO_UNKNOWN(Instance):
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
