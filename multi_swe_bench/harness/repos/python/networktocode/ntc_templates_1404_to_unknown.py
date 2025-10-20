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
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
pip install poetry
###ACTION_DELIMITER###
apt-get install -y python3-full
###ACTION_DELIMITER###
python3 -m venv .venv && .venv/bin/pip install poetry
###ACTION_DELIMITER###
.venv/bin/poetry install
###ACTION_DELIMITER###
apt-get install -y libyaml-dev
###ACTION_DELIMITER###
.venv/bin/poetry install
###ACTION_DELIMITER###
.venv/bin/pip install cython
###ACTION_DELIMITER###
apt-get install -y python3-yaml
###ACTION_DELIMITER###
.venv/bin/poetry install
###ACTION_DELIMITER###
.venv/bin/pip install --upgrade setuptools && .venv/bin/pip install pyyaml==6.0 --global-option=--with-libyaml
###ACTION_DELIMITER###
.venv/bin/pip install pyyaml==6.0 --no-use-pep517 --global-option=--with-libyaml
###ACTION_DELIMITER###
.venv/bin/pip install wheel && .venv/bin/pip install pyyaml==6.0 --no-use-pep517 --global-option=--with-libyaml
###ACTION_DELIMITER###
rm -rf .venv && python3 -m venv --system-site-packages .venv && .venv/bin/pip install poetry && .venv/bin/poetry install
###ACTION_DELIMITER###
.venv/bin/poetry config virtualenvs.create false && .venv/bin/poetry install
###ACTION_DELIMITER###
.venv/bin/pip install cython && .venv/bin/poetry install
###ACTION_DELIMITER###
.venv/bin/pip download pyyaml==6.0 --no-deps --no-binary :all: && tar xzf PyYAML-6.0.tar.gz && cd PyYAML-6.0 && .venv/bin/python setup.py build_ext --inplace && .venv/bin/pip install . && cd .. && .venv/bin/poetry install
###ACTION_DELIMITER###
.venv/bin/pip download pyyaml==6.0 --no-deps --no-binary :all: && tar xzf PyYAML-6.0.tar.gz && cd PyYAML-6.0 && .venv/bin/cython yaml.pyx && .venv/bin/python setup.py build_ext --inplace && .venv/bin/pip install . && cd .. && .venv/bin/poetry install
###ACTION_DELIMITER###
.venv/bin/pip install pyyaml==6.0.1 && .venv/bin/poetry install --no-root
###ACTION_DELIMITER###
.venv/bin/poetry update pyyaml && .venv/bin/poetry install
###ACTION_DELIMITER###
.venv/bin/pip install --upgrade packaging && .venv/bin/poetry install
###ACTION_DELIMITER###
echo -e '#!/bin/bash
.venv/bin/pytest --verbose --no-header -rA --tb=no -p no:cacheprovider ./tests' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
.venv/bin/pytest --verbose --no-header -rA --tb=no -p no:cacheprovider ./tests

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
.venv/bin/pytest --verbose --no-header -rA --tb=no -p no:cacheprovider ./tests

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
.venv/bin/pytest --verbose --no-header -rA --tb=no -p no:cacheprovider ./tests

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
RUN git clone https://github.com/networktocode/ntc-templates.git /home/ntc-templates

WORKDIR /home/ntc-templates
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("networktocode", "ntc_templates_1404_to_unknown")
class NTC_TEMPLATES_1404_TO_UNKNOWN(Instance):
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
        # Compile regex patterns to match test lines
        # Combined pattern to match both test formats (status before/after test name)
        # Pattern 1: test name followed by status (e.g., [123] tests/... PASSED [0%])
        pattern1 = re.compile(r'^(tests/.*?)\s+(PASSED|FAILED|SKIPPED)\s+\[\s*\d+%?\s*\]')
        # Pattern 2: status followed by test name (e.g., [123] PASSED tests/...)
        pattern2 = re.compile(r'^(PASSED|FAILED|SKIPPED)\s+(tests/.*)')
        for line in log.split('\n'):
            line = line.strip()
            match = pattern1.search(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
            else:
                match = pattern2.search(line)
                if match:
                    test_name = match.group(2)
                    status = match.group(1)
                else:
                    continue
            # Add test name to the corresponding status set
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
