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
                """python3 --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y
###ACTION_DELIMITER###
apt-get install -y python3.7 python3.7-venv
###ACTION_DELIMITER###
python3.7 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install .
###ACTION_DELIMITER###
pip install -r test_requirements/django-1.10.txt
###ACTION_DELIMITER###
sed -i 's/python-coveralls==2.5.0/python-coveralls>=2.9.1/' test_requirements/requirements_base.txt
###ACTION_DELIMITER###
pip install -r test_requirements/django-1.10.txt
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
pip install -r test_requirements/django-1.10.txt
###ACTION_DELIMITER###
sed -i 's/django-treebeard>=4.1/django-treebeard<=4.1.2/' test_requirements/requirements_base.txt
###ACTION_DELIMITER###
pip install -r test_requirements/django-1.10.txt
###ACTION_DELIMITER###
sed -i 's/django-sekizai>=0.7/django-sekizai<=0.10.0/' test_requirements/requirements_base.txt
###ACTION_DELIMITER###
pip install -r test_requirements/django-1.10.txt
###ACTION_DELIMITER###
sed -i 's/django-sekizai<=0.10.0/django-sekizai==0.10.0/' test_requirements/requirements_base.txt
###ACTION_DELIMITER###
sed -i 's|https://github.com/divio/djangocms-text-ckeditor/archive/master.zip|https://github.com/divio/djangocms-text-ckeditor/archive/3.4.0.zip|' test_requirements/requirements_base.txt
###ACTION_DELIMITER###
pip install -r test_requirements/django-1.10.txt
###ACTION_DELIMITER###
apt-get install -y libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7-dev libtiff5-dev tk-dev tcl-dev
###ACTION_DELIMITER###
pip install -r test_requirements/django-1.10.txt
###ACTION_DELIMITER###
sed -i 's/Pillow==3.3/Pillow==5.4.1/' test_requirements/requirements_base.txt
###ACTION_DELIMITER###
pip install -r test_requirements/django-1.10.txt
###ACTION_DELIMITER###
echo 'python manage.py test -v 2' > test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
python manage.py test -v 2

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
python manage.py test -v 2

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
python manage.py test -v 2

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
RUN git clone https://github.com/django-cms/django-cms.git /home/django-cms

WORKDIR /home/django-cms
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("django-cms", "django_cms_6023_to_5702")
class DJANGO_CMS_6023_TO_5702(Instance):
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
        passed_tests: set[str] = set() # Tests that passed successfully
        failed_tests: set[str] = set() # Tests that failed
        skipped_tests: set[str] = set() # Tests that were skipped
        import re
        lines = log.splitlines()
        current_test = None
        for line in lines:
            # Check if the line contains both test name and status
            combined_match = re.search(r'(test_[^\s]+).*?\.\.\.\s*(ok|passed|pass|success|failed|fail|skipped|error|xfail)', line, re.IGNORECASE)
            if combined_match:
                test_name = combined_match.group(1).strip()
                status = combined_match.group(2).lower()
                if status in ('ok', 'passed', 'pass', 'success'):
                    passed_tests.add(test_name)
                elif status in ('failed', 'fail'):
                    failed_tests.add(test_name)
                elif status == 'skipped':
                    skipped_tests.add(test_name)
                elif status in ('error', 'xfail'):
                    failed_tests.add(test_name)
            else:
                # Check for test name only (status may be on next line)
                test_match = re.search(r'(test_[^\s]+)\s*\(', line)
                if test_match:
                    current_test = test_match.group(1).strip()
                # Check for status in current line if test name was found earlier
                elif current_test:
                    status_match = re.search(r'\.\.\.\s*(ok|passed|pass|success|failed|skipped|error|xfail)', line, re.IGNORECASE)
                    if status_match:
                        status = status_match.group(1).lower()
                        if status in ('ok', 'passed', 'pass', 'success'):
                            passed_tests.add(current_test)
                        elif status == 'failed':
                            failed_tests.add(current_test)
                        elif status == 'skipped':
                            skipped_tests.add(current_test)
                        elif status in ('error', 'xfail'):
                            failed_tests.add(current_test)
                        current_test = None
                    elif 'Error' in line or 'Exception' in line or 'Traceback' in line:
                        failed_tests.add(current_test)
                        current_test = None
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
