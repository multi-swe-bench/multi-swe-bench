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
apt-get update && apt-get install -y python3.8 python3.8-venv python3.8-pip
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.8 python3.8-venv python3.8-pip
###ACTION_DELIMITER###
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.8 get-pip.py
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.8 get-pip.py
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.8
###ACTION_DELIMITER###
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.8 get-pip.py
###ACTION_DELIMITER###
curl https://bootstrap.pypa.io/pip/3.8/get-pip.py -o get-pip.py && python3.8 get-pip.py
###ACTION_DELIMITER###
apt-get install -y python3.8-distutils
###ACTION_DELIMITER###
curl https://bootstrap.pypa.io/pip/3.8/get-pip.py -o get-pip.py && python3.8 get-pip.py
###ACTION_DELIMITER###
python3.8 -m venv venv
###ACTION_DELIMITER###
python3.8 -m venv --without-pip venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
curl https://bootstrap.pypa.io/pip/3.8/get-pip.py -o get-pip.py && python get-pip.py
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo './venv/bin/pytest -v --no-header -rA --tb=short -p no:cacheprovider tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
grep -r 'import' tests/conftest.py
###ACTION_DELIMITER###
python3.8 -c 'from great_expectations.data_context.cloud_constants import GXCloudEnvironmentVariable'
###ACTION_DELIMITER###
pip check
###ACTION_DELIMITER###
java -version
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-11-jdk
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/-v/-vv/' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
pytest -vv --no-header -rA --tb=short -p no:cacheprovider -W ignore::PendingDeprecationWarning tests/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
pytest -vv --no-header -rA --tb=short -p no:cacheprovider -W ignore::PendingDeprecationWarning -W ignore::DeprecationWarning tests/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y locales && locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
pytest -vv --no-header -rA --tb=short -p no:cacheprovider -W ignore::PendingDeprecationWarning -W ignore::DeprecationWarning tests/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
./venv/bin/pytest -v --no-header -rA --tb=short -p no:cacheprovider -W ignore::PendingDeprecationWarning -W ignore::DeprecationWarning tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
./venv/bin/pytest -v -n auto --no-header -rA --tb=short -p no:cacheprovider -W ignore::PendingDeprecationWarning -W ignore::DeprecationWarning tests/' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install pytest-xdist && echo -e '#!/bin/bash
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
./venv/bin/pytest -v -n auto --no-header -rA --tb=short -p no:cacheprovider -W ignore::PendingDeprecationWarning -W ignore::DeprecationWarning tests/' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
./venv/bin/pytest -v -n auto --no-header -rA --tb=short -p no:cacheprovider -W ignore::PendingDeprecationWarning -W ignore::DeprecationWarning tests/

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
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
./venv/bin/pytest -v -n auto --no-header -rA --tb=short -p no:cacheprovider -W ignore::PendingDeprecationWarning -W ignore::DeprecationWarning tests/

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
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
./venv/bin/pytest -v -n auto --no-header -rA --tb=short -p no:cacheprovider -W ignore::PendingDeprecationWarning -W ignore::DeprecationWarning tests/

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
RUN git clone https://github.com/great-expectations/great_expectations.git /home/great_expectations

WORKDIR /home/great_expectations
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("great-expectations", "great_expectations_7837_to_7691")
class GREAT_EXPECTATIONS_7837_TO_7691(Instance):
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
        # Parse test statuses using regex
        passed_matches = re.findall(r'PASSED\s+(tests/.*?\.py::.*?)(?=\s|$)', log)
        passed_tests.update(passed_matches)
        failed_matches = re.findall(r'FAILED\s+(tests/.*?\.py::.*?)(?=\s|$)', log)
        failed_tests.update(failed_matches)
        skipped_matches = re.findall(r'SKIPPED\s+(tests/.*?\.py::.*?)(?=\s|$)', log)
        skipped_tests.update(skipped_matches)
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
