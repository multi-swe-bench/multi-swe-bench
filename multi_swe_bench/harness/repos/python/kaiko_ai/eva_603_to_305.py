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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
pip install -e .[all]
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate && pip install -e .[all]
###ACTION_DELIMITER###
echo -e '#!/bin/bash
source venv/bin/activate
pytest -v tests/eva/core tests/eva/vision' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip list | grep pytest
###ACTION_DELIMITER###
venv/bin/pip install pytest
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install pytest-cov
###ACTION_DELIMITER###
echo -e '#!/bin/bash
source venv/bin/activate
pytest -v --no-cov tests/eva/core tests/eva/vision' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install torchmetrics==1.3.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install torchmetrics==1.4.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y git-lfs && git lfs pull
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install torchmetrics==1.5.0
###ACTION_DELIMITER###
venv/bin/pip install torchmetrics==1.6.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
source venv/bin/activate
export TORCH_FORCE_WEIGHTS_ONLY_LOAD=1
pytest -v --no-cov tests/eva/core tests/eva/vision' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install torch==2.6.0
###ACTION_DELIMITER###
venv/bin/pip install torch==2.3.0 torchvision==0.18.0 transformers==4.38.2 && echo -e '#!/bin/bash
source venv/bin/activate
export TORCH_FORCE_WEIGHTS_ONLY_LOAD=1
pytest -v --no-cov tests/eva/core tests/eva/vision' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y openslide-tools
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
source venv/bin/activate
export TORCH_FORCE_WEIGHTS_ONLY_LOAD=1
pytest -vv --no-cov tests/eva/core tests/eva/vision' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i '$a from torch.nn.init import trunc_normal_' tests/eva/core/utils/__init__.py
###ACTION_DELIMITER###
sed -i '$a from torch.nn.init import trunc_normal_' src/eva/core/utils/__init__.py && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
source venv/bin/activate
export TORCH_FORCE_WEIGHTS_ONLY_LOAD=1
pytest -vv --no-cov tests/eva/core tests/eva/vision

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
source venv/bin/activate
export TORCH_FORCE_WEIGHTS_ONLY_LOAD=1
pytest -vv --no-cov tests/eva/core tests/eva/vision

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
source venv/bin/activate
export TORCH_FORCE_WEIGHTS_ONLY_LOAD=1
pytest -vv --no-cov tests/eva/core tests/eva/vision

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
RUN git clone https://github.com/kaiko-ai/eva.git /home/eva

WORKDIR /home/eva
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("kaiko-ai", "eva_603_to_305")
class EVA_603_TO_305(Instance):
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
        # Remove ANSI color codes from log content
        log_clean = re.sub(r'\x1b\[.*?m', '', log)
        # Regex pattern to match test names and statuses in cleaned log
        pattern = re.compile(
            r'(tests/[\w/-]+\.py::test_\w+(\[.*?\])?)\s+(PASSED|FAILED|SKIPPED)|'
            r'(PASSED|FAILED|SKIPPED)\s+(tests/[\w/-]+\.py::test_\w+(\[.*?\])?)'
        )
        # Find all matches in the cleaned log
        matches = pattern.findall(log_clean)
        for match in matches:
            # Check which part of the regex matched
            if match[0]:  # Part A: test name followed by status
                test_name = match[0]
                status = match[2]
            elif match[3]:  # Part B: status followed by test name
                test_name = match[4]
                status = match[3]
            else:
                continue  # no match
            # Strip color codes from the test name
            clean_test_name = re.sub(r'\x1b\[.*?m', '', test_name).strip()
            # Categorize the test based on status
            if status == 'PASSED':
                passed_tests.add(clean_test_name)
            elif status == 'FAILED':
                failed_tests.add(clean_test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(clean_test_name)
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
