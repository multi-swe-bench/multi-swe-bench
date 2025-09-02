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
                """pip install --upgrade jax jaxlib
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
pip3 install --upgrade jax jaxlib
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install -e ".[testing]"
###ACTION_DELIMITER###
apt-get install -y cmake
###ACTION_DELIMITER###
pip install -e ".[testing]"
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pytest --no-header -rA --tb=no -p no:cacheprovider -v tests/' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
source venv/bin/activate
pytest --no-header -rA --tb=no -p no:cacheprovider -v tests/' > test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
venv/bin/python -m pytest --no-header -rA --tb=no -p no:cacheprovider -v tests/' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
venv/bin/python -m pytest -v --tb=short tests/' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
venv/bin/python -m pytest -v --tb=long tests/checkpoints_test.py' > test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y jax jaxlib && pip install jax==0.3.25 jaxlib==0.3.25
###ACTION_DELIMITER###
apt-get install -y python3.10 python3.10-venv
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.8 python3.8-venv
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.8 python3.8-venv
###ACTION_DELIMITER###
python3.8 -m venv venv38
###ACTION_DELIMITER###
source venv38/bin/activate
###ACTION_DELIMITER###
pip install jax jaxlib
###ACTION_DELIMITER###
pip install -e ".[testing]"
###ACTION_DELIMITER###
echo -e '#!/bin/bash
venv38/bin/python -m pytest -v tests/' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y jax jaxlib && pip install jax==0.2.25 jaxlib==0.2.25
###ACTION_DELIMITER###
pip install jax==0.2.21 jaxlib==0.2.21
###ACTION_DELIMITER###
pip install https://github.com/google/jax/releases/download/jax-v0.2.19/jaxlib-0.2.19-cp38-cp38-manylinux2010_x86_64.whl && pip install jax==0.2.19
###ACTION_DELIMITER###
pip install https://storage.googleapis.com/jax-releases/jaxlib-0.2.20-cp38-none-manylinux2010_x86_64.whl && pip install jax==0.2.20
###ACTION_DELIMITER###
pip install https://github.com/google/jax/releases/download/jax-v0.2.18/jaxlib-0.2.18-cp38-cp38-manylinux2010_x86_64.whl && pip install jax==0.2.18
###ACTION_DELIMITER###
pip install https://storage.googleapis.com/jax-releases/jaxlib-0.2.25-cp38-none-manylinux2010_x86_64.whl && pip install jax==0.2.25
###ACTION_DELIMITER###
sed -i '/jax.config.enable_omnistaging()/d' tests/linen/dotgetter_test.py tests/linen/linen_attention_test.py tests/linen/linen_linear_test.py tests/linen/linen_test.py tests/linen/linen_transforms_test.py tests/linen/module_test.py tests/linen/toplevel_test.py
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
pip install jax jaxlib
###ACTION_DELIMITER###
pip uninstall -y jax jaxlib && pip install -e ".[testing]"
###ACTION_DELIMITER###
pip install jax==0.3.25 jaxlib==0.3.25
###ACTION_DELIMITER###
pip install jax jaxlib && ./test_commands.sh
###ACTION_DELIMITER###
pip install https://github.com/google/jax/releases/download/jax-v0.2.21/jaxlib-0.2.21-cp38-none-manylinux2010_x86_64.whl && pip install jax==0.2.21
###ACTION_DELIMITER###
pip install https://storage.googleapis.com/jax-releases/jaxlib-0.3.15-cp38-none-manylinux2010_x86_64.whl && pip install jax==0.3.15
###ACTION_DELIMITER###
pip install https://github.com/google/jax/releases/download/jax-v0.2.21/jaxlib-0.2.21-cp38-cp38-manylinux2010_x86_64.whl && pip install jax==0.2.21
###ACTION_DELIMITER###
echo -e '#!/bin/bash
venv38/bin/python -m pytest -v --disable-warnings tests/' > test_commands.sh && chmod +x test_commands.sh && ./test_commands.sh
###ACTION_DELIMITER###
pip install https://github.com/google/jax/releases/download/jax-v0.2.21/jaxlib-0.2.21-cp38-none-manylinux2010_x86_64.whl && pip install jax==0.2.21 && ./test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
venv38/bin/python -m pytest -v --disable-warnings tests/

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
venv38/bin/python -m pytest -v --disable-warnings tests/

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
venv38/bin/python -m pytest -v --disable-warnings tests/

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
RUN git clone https://github.com/google/flax.git /home/flax

WORKDIR /home/flax
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("google", "flax_1180_to_217")
class FLAX_1180_TO_217(Instance):
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
        # Regular expressions to match test cases
        pattern1 = r'^(\S+)\s+(PASSED|FAILED|SKIPPED)\s+\[\s*\d+%\]'  # Test name first, then status and percentage
        pattern2 = r'^(PASSED|FAILED|SKIPPED)\s+(\S+)(?:\s+-.*)?$'    # Status first, then test name (optional message)
        # Find all matches for both patterns
        matches1 = re.findall(pattern1, log, re.MULTILINE)
        matches2 = re.findall(pattern2, log, re.MULTILINE)
        # Process matches from pattern1
        for test_name, status in matches1:
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
        # Process matches from pattern2
        for status, test_name in matches2:
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
