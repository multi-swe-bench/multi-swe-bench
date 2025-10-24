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
        repo_name = self.pr.repo
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
python -m pip install --ignore-installed -U -e .[complete]
###ACTION_DELIMITER###
python -m pip install --upgrade pip
###ACTION_DELIMITER###
python -m pip install --ignore-installed -U -e .
###ACTION_DELIMITER###
python -m pip install pytest
###ACTION_DELIMITER###
python -m pytest -v
###ACTION_DELIMITER###
python -m pip install requests
###ACTION_DELIMITER###
python -m pytest -v
###ACTION_DELIMITER###
python -m pip install torch
###ACTION_DELIMITER###
python -m pytest -v
###ACTION_DELIMITER###
python -m pip install tensorflow
###ACTION_DELIMITER###
python -m pytest -v
###ACTION_DELIMITER###
python -m pip install tensorflow-probability
###ACTION_DELIMITER###
python -m pytest -v
###ACTION_DELIMITER###
python -m pip install tf-keras
###ACTION_DELIMITER###
python -m pytest -v
###ACTION_DELIMITER###
python -m pip install jax jaxlib
###ACTION_DELIMITER###
python -m pip install jax==0.1.77 jaxlib==0.1.56
###ACTION_DELIMITER###
python -m pip install --force-reinstall jax jaxlib
###ACTION_DELIMITER###
python -m pip install jax==0.2.25 jaxlib==0.1.71
###ACTION_DELIMITER###
PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip install --no-cache-dir jax==0.2.25 jaxlib==0.1.71
###ACTION_DELIMITER###
python -m pip install jax jaxlib && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip uninstall -y jax jaxlib && python -m pip install jax==0.3.25 jaxlib==0.3.25
###ACTION_DELIMITER###
python -m pip install jax==0.4.10 jaxlib==0.4.10 && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip uninstall -y ml_dtypes && python -m pip install ml_dtypes==0.2.0 && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip uninstall -y numpy && python -m pip install numpy==1.26.4 && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip install ml_dtypes==0.5.1 && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip install ml_dtypes==0.6.0 && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip install ml_dtypes==0.5.3 && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip install --no-cache-dir ml_dtypes==0.6.0 && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip uninstall -y tensorflow && python -m pip install tensorflow==2.15.0 && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip uninstall -y tensorflow-probability && python -m pip install tensorflow-probability==0.23.0 && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip uninstall -y scipy jax jaxlib && python -m pip install scipy==1.10.1 jax==0.4.16 jaxlib==0.4.16 && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip install iminuit && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip install pytest-cov && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip install uproot && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip install uproot3 && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip install matplotlib papermill && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip install pytest-mpl jupyter_client && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
python -m pip install scrapbook && PYHF_BACKEND=numpy python -m pytest -v
###ACTION_DELIMITER###
echo '#!/bin/bash
PYHF_BACKEND=numpy python -m pytest -v' > /home/pyhf/test_commands.sh && chmod +x /home/pyhf/test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
PYHF_BACKEND=numpy python -m pytest -v

""".replace("[[REPO_NAME]]", repo_name),
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
PYHF_BACKEND=numpy python -m pytest -v

""".replace("[[REPO_NAME]]", repo_name),
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
PYHF_BACKEND=numpy python -m pytest -v

""".replace("[[REPO_NAME]]", repo_name),
            ),
        ]

    def dockerfile(self) -> str:
        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        dockerfile_content = """
# This is a template for creating a Dockerfile to test patches
# LLM should fill in the appropriate values based on the context

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim with actual base image
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
RUN git clone https://github.com/scikit-hep/pyhf.git /home/pyhf

WORKDIR /home/pyhf
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("scikit-hep", "pyhf_993_to_983")
class PYHF_993_TO_983(Instance):
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

        return "bash /home/run.sh"

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

        # import json  # Uncomment if needed for JSON parsing
        lines = log.split("\n")
        for line in lines:
            # Remove line number (e.g., [  12])
            clean_line = re.sub(r"^\[\s*\d+\]\s*", "", line).strip()
            if not clean_line:
                continue
            # Check for PASSED status
            if "PASSED" in clean_line:
                # Capture test name before 'PASSED' (ignores trailing content like [0%])
                match = re.search(r"^(.*?)\s+PASSED\b", clean_line)
                if match:
                    test_name = match.group(1).strip()
                    passed_tests.add(test_name)
            # Check for FAILED status
            elif "FAILED" in clean_line:
                # Capture test name before 'FAILED' (ignores trailing content)
                match = re.search(r"^(.*?)\s+FAILED\b", clean_line)
                if match:
                    test_name = match.group(1).strip()
                    failed_tests.add(test_name)
            # Check for ERROR status (considered a failure)
            elif "ERROR" in clean_line:
                # Extract test name after 'ERROR' (handles trailing hyphens/characters)
                match = re.search(r"ERROR\s+(.*?)(?:\s|-|$)", clean_line)
                if match:
                    test_name = match.group(1).strip()
                    if test_name:
                        failed_tests.add(test_name)
            # Check for SKIPPED status
            elif "SKIPPED" in clean_line:
                test_name = clean_line.split("SKIPPED")[0].strip()
                if test_name and not any(
                    status in test_name for status in ["PASSED", "FAILED", "ERROR"]
                ):
                    skipped_tests.add(test_name)
        parsed_results = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
        }

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
