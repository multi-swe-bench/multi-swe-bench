from typing import Optional

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
apt-get update && apt-get install -y python3.7 python3.7-dev python3.7-venv build-essential
###ACTION_DELIMITER###
add-apt-repository -y ppa:deadsnakes/ppa
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository -y ppa:deadsnakes/ppa
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.7 python3.7-dev python3.7-venv
###ACTION_DELIMITER###
python3.7 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install -e ".[tests]"
###ACTION_DELIMITER###
pip install setuptools-scm==7.1.0
###ACTION_DELIMITER###
pip install -e ".[tests]"
###ACTION_DELIMITER###
pip install --upgrade pip
###ACTION_DELIMITER###
pip install -e ".[tests]" --no-build-isolation
###ACTION_DELIMITER###
pip install wheel
###ACTION_DELIMITER###
pip install -e ".[tests]" --no-build-isolation
###ACTION_DELIMITER###
echo 'pytest -v -rA --tb=short tests/' > /home/renku-python/test_commands.sh
###ACTION_DELIMITER###
bash /home/renku-python/test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -rA --tb=short -p no:yapf tests/' > /home/renku-python/test_commands.sh
###ACTION_DELIMITER###
bash /home/renku-python/test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i 's/ --yapf//' pytest.ini
###ACTION_DELIMITER###
bash /home/renku-python/test_commands.sh
###ACTION_DELIMITER###
sed -i 's/ --flake8 --pep8//' pytest.ini
###ACTION_DELIMITER###
bash /home/renku-python/test_commands.sh
###ACTION_DELIMITER###
pip install attrs==19.3.0
###ACTION_DELIMITER###
bash /home/renku-python/test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libmagic1
###ACTION_DELIMITER###
bash /home/renku-python/test_commands.sh
###ACTION_DELIMITER###
pip install PyYAML==5.0.1
###ACTION_DELIMITER###
pip install PyYAML==3.13
###ACTION_DELIMITER###
git config --global user.name 'Test User' && git config --global user.email 'test@example.com'
###ACTION_DELIMITER###
bash /home/renku-python/test_commands.sh
###ACTION_DELIMITER###
apt-get install -y git-lfs && git lfs install
###ACTION_DELIMITER###
pip install click==7.1.2
###ACTION_DELIMITER###
bash /home/renku-python/test_commands.sh
###ACTION_DELIMITER###
apt-get install -y nodejs
###ACTION_DELIMITER###
apt-get install -y npm"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v -rA --tb=short -p no:yapf tests/

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
pytest -v -rA --tb=short -p no:yapf tests/

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
pytest -v -rA --tb=short -p no:yapf tests/

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
RUN git clone https://github.com/SwissDataScienceCenter/renku-python.git /home/renku-python

WORKDIR /home/renku-python
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("SwissDataScienceCenter", "renku_python_307_to_254")
class RENKU_PYTHON_307_TO_254(Instance):
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
        # Implement the log parsing logic here
        test_pattern = re.compile(r'tests/[^:]+::[^ ]+')
        for line in log.split('\n'):
            line = line.strip()
            if 'PASSED' in line:
                match = test_pattern.search(line)
                if match:
                    passed_tests.add(match.group())
            elif 'FAILED' in line:
                match = test_pattern.search(line)
                if match:
                    failed_tests.add(match.group())
            elif 'SKIPPED' in line:
                match = test_pattern.search(line)
                if match:
                    skipped_tests.add(match.group())
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
