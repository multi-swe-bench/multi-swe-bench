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
        return "python:3.11-slim"
    
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
apt-get update && apt-get install -y nodejs npm ruby build-essential libjpeg-dev zlib1g-dev
###ACTION_DELIMITER###
pip install -e .[testing]
###ACTION_DELIMITER###
echo -e '#!/bin/bash
flake8 wagtail
isort --check-only --diff --recursive wagtail
npm run lint:js
npm run lint:css
python -u runtests.py
npm run test:unit:coverage -- --runInBand
npm run build' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
apt-get update && apt-get install -y python2
###ACTION_DELIMITER###
apt-get update && apt-get install -y git build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev
###ACTION_DELIMITER###
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
###ACTION_DELIMITER###
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc && echo 'eval "$(pyenv init -)"' >> ~/.bashrc && source ~/.bashrc
###ACTION_DELIMITER###
export PATH="$HOME/.pyenv/bin:$PATH" && eval "$(pyenv init -)" && pyenv install 2.7.18
###ACTION_DELIMITER###
npm config set python /root/.pyenv/versions/2.7.18/bin/python && npm install
###ACTION_DELIMITER###
export PYTHON=/root/.pyenv/versions/2.7.18/bin/python && npm install
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && source ~/.bashrc && nvm install 14 && nvm use 14 && npm install
###ACTION_DELIMITER###
source ~/.bashrc && nvm install 8 && nvm use 8 && export PYTHON=/root/.pyenv/versions/2.7.18/bin/python && npm install
###ACTION_DELIMITER###
gem install scss_lint
###ACTION_DELIMITER###
apt-get update && apt-get install -y ruby3.1-dev
###ACTION_DELIMITER###
gem install scss_lint
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pyenv install 3.6.15 && pyenv local 3.6.15
###ACTION_DELIMITER###
pip install -e .[testing]
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install --upgrade pip==21.3.1
###ACTION_DELIMITER###
pip install flake8==3.9.2 && pip install --upgrade isort
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
flake8 wagtail
isort --check-only --diff --recursive wagtail
npm run lint:js
npm run lint:css
python -u runtests.py
npm run test:unit:coverage -- --runInBand
npm run build

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
flake8 wagtail
isort --check-only --diff --recursive wagtail
npm run lint:js
npm run lint:css
python -u runtests.py
npm run test:unit:coverage -- --runInBand
npm run build

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
flake8 wagtail
isort --check-only --diff --recursive wagtail
npm run lint:js
npm run lint:css
python -u runtests.py
npm run test:unit:coverage -- --runInBand
npm run build

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
FROM python:3.11-slim

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
RUN git clone https://github.com/wagtail/wagtail.git /home/wagtail

WORKDIR /home/wagtail
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("wagtail", "wagtail_3763_to_3608")
class WAGTAIL_3763_TO_3608(Instance):
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
        # Parse test results using regex
        pass_pattern = re.compile(r'PASS\s+(.+\.test\.js)')
        failed_pattern = re.compile(r'FAIL\s+(.+\.test\.js)')
        skipped_pattern = re.compile(r'SKIPPED\s+(.+\.test\.js)')
        passed_tests.update(pass_pattern.findall(log))
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
