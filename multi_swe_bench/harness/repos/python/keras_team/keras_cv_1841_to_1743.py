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
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
pip3 install -r requirements.txt
###ACTION_DELIMITER###
pip3 install -r requirements.txt --break-system-packages
###ACTION_DELIMITER###
echo 'pytest --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pytest --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
pip3 install -e . --break-system-packages
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip3 uninstall -y keras tensorflow && pip3 install tensorflow==2.15.0 keras==2.15.0 --break-system-packages
###ACTION_DELIMITER###
pip3 uninstall -y keras tensorflow --break-system-packages && pip3 install tensorflow==2.15.0 keras==2.15.0 --break-system-packages
###ACTION_DELIMITER###
pip3 uninstall -y keras tensorflow --break-system-packages && pip3 install tensorflow==2.16.0 --break-system-packages
###ACTION_DELIMITER###
apt-get install -y python3.11 python3.11-venv python3.11-dev
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y && apt-get update
###ACTION_DELIMITER###
apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y && apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.11 python3.11-venv python3.11-dev
###ACTION_DELIMITER###
python3.11 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
pip uninstall -y tensorflow keras && pip install tensorflow==2.15.0 keras==2.15.0
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y keras && pip install keras==2.14.0
###ACTION_DELIMITER###
pip uninstall -y tensorflow keras && pip install tensorflow==2.12.0 keras==2.12.0
###ACTION_DELIMITER###
pip install keras-preprocessing
###ACTION_DELIMITER###
pip uninstall -y tensorflow keras && pip install tensorflow==2.10.0 keras==2.10.0
###ACTION_DELIMITER###
echo -e '#!/bin/bash
source venv/bin/activate
pytest --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y python3.9 python3.9-venv && python3.9 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install tensorflow==2.10.0 keras==2.10.0 && pip install -r requirements.txt && pip install -e .
###ACTION_DELIMITER###
source venv/bin/activate && pip uninstall -y keras && pip install --force-reinstall tensorflow==2.10.0 && python -c 'import tensorflow as tf; print(tf.__version__)' && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip uninstall -y tensorflow && pip install --no-cache-dir tensorflow==2.10.0 && pip install absl-py==1.4.0 && python -c 'import tensorflow as tf; print(tf.__version__)' && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip uninstall -y tensorflow && pip install --no-cache-dir tensorflow==2.10.0 && python -c 'import tensorflow as tf; print(tf.__version__)' && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf venv && python3.9 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install tensorflow==2.10.0 keras==2.10.0 && pip install -r requirements.txt && pip install -e . && python -c 'import tensorflow as tf; print("TensorFlow version:", tf.__version__)' && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf venv && python3.9 -m venv venv && source venv/bin/activate && pip install pip==22.0 && pip install tensorflow==2.10.0 numpy<1.24 && pip install keras==2.10.0 && pip install -r requirements.txt && pip install -e . && python -c 'import tensorflow as tf; print("TensorFlow version:", tf.__version__)' && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf venv && python3.9 -m venv venv && source venv/bin/activate && pip install --upgrade pip==22.0 && pip install tensorflow==2.10.0 "numpy<1.24" && pip install keras==2.10.0 && pip install -r requirements.txt && pip install -e . && python -c 'import tensorflow as tf; print("TensorFlow version:", tf.__version__)' && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf venv && python3.9 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install tensorflow==2.11.0 "numpy<1.24" && pip install -r requirements.txt && pip install -e . && python -c 'import tensorflow as tf; print("TensorFlow version:", tf.__version__)' && bash test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
source venv/bin/activate
pytest --no-header -rA --tb=no -p no:cacheprovider

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
pytest --no-header -rA --tb=no -p no:cacheprovider

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
pytest --no-header -rA --tb=no -p no:cacheprovider

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
RUN git clone https://github.com/keras-team/keras-cv.git /home/keras-cv

WORKDIR /home/keras-cv
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("keras-team", "keras_cv_1841_to_1743")
class KERAS_CV_1841_TO_1743(Instance):
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
        # Extract all test names from 'call' lines (preserving order)
        test_names_ordered = re.findall(r'call\s+([^\s]+)', log)
        # Extract failed tests from 'FAILED' lines in summary
        failed_tests = set(re.findall(r'FAILED\s+([^\s]+)', log))
        # Extract skipped tests from progress lines (marked with 's')
        skipped_tests = set()
        # Parse progress lines (e.g., 'keras_cv/.../test.py ..s')
        progress_matches = re.findall(r'^(\S+\.py)\s+([\.s\s]+)$', log, re.MULTILINE)
        for file_path, status_str in progress_matches:
            # Clean status string (remove spaces between characters)
            status_chars = re.sub(r'\s', '', status_str)
            # Get all tests in order for this file
            file_tests = [test for test in test_names_ordered if test.startswith(file_path)]
            # Map 's' characters to skipped tests
            for i, char in enumerate(status_chars):
                if char == 's' and i < len(file_tests):
                    skipped_tests.add(file_tests[i])
        # Calculate passed tests (all tests not failed or skipped)
        passed_tests = set(test_names_ordered) - failed_tests - skipped_tests
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
