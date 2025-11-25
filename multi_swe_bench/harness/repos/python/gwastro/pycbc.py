from typing import Optional
import re

from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.instance import Instance, TestResult
from multi_swe_bench.harness.pull_request import PullRequest


class ImageDefault(Image):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config
        self._pr_mapping = self._load_pr_mapping()

    @property
    def pr(self) -> PullRequest:
        return self._pr

    @property
    def config(self) -> Config:
        return self._config

    def _load_pr_mapping(self) -> dict:
        """PR to Docker image mapping."""
        return {
            5202: "pycbc/pycbc-el8",
            5196: "pycbc/pycbc-el8",
            5185: "pycbc/pycbc-el8",
            5165: "pycbc/pycbc-el8",
            5121: "pycbc/pycbc-el8",
            5117: "pycbc/pycbc-el8",
            5085: "pycbc/pycbc-el8",
            5049: "pycbc/pycbc-el8",
            5040: "pycbc/pycbc-el8",
            5024: "pycbc/pycbc-el8",
            5019: "pycbc/pycbc-el8",
            5002: "pycbc/pycbc-el8",
            4991: "pycbc/pycbc-el8",
            4946: "pycbc/pycbc-el8",
            4932: "pycbc/pycbc-el8",
            4867: "pycbc/pycbc-el8",
            4848: "pycbc/pycbc-el8",
            4838: "pycbc/pycbc-el8",
            4822: "pycbc/pycbc-el8",
            4816: "pycbc/pycbc-el8",
            4776: "pycbc/pycbc-el8",
            4775: "pycbc/pycbc-el8",
            4771: "pycbc/pycbc-el8",
            4724: "pycbc/pycbc-el8",
            4634: "pycbc/pycbc-el8",
            4608: "pycbc/pycbc-el8",
            4604: "pycbc/pycbc-el8",
            4477: "pycbc/pycbc-el8",
            4400: "pycbc/pycbc-el8",
            4183: "pycbc/pycbc-el8",
            4192: "pycbc/pycbc-el8",
            4149: "pycbc/pycbc-el8",
            4080: "pycbc/pycbc-el8",
            4006: "pycbc/pycbc-el8",
            3997: "pycbc/pycbc-el8",
            3881: "pycbc/pycbc-el7",
            3879: "pycbc/pycbc-el7",
            3868: "pycbc/pycbc-el7",
            3851: "pycbc/pycbc-el7",
            3837: "pycbc/pycbc-el7",
            3807: "pycbc/pycbc-el7",
            3791: "pycbc/pycbc-el7",
            3742: "pycbc/pycbc-el7",
            3719: "pycbc/pycbc-el7",
            3629: "pycbc/pycbc-el7",
            3598: "pycbc/pycbc-el7",
            3586: "pycbc/pycbc-el7",
            3385: "pycbc/pycbc-el7",
            3244: "pycbc/pycbc-el7",
            3227: "pycbc/pycbc-el7",
            2485: "pycbc/pycbc-el7",
            2393: "pycbc/pycbc-el7",
            2394: "pycbc/pycbc-el7",
            2396: "pycbc/pycbc-el7",
            2253: "pycbc/pycbc-el7",
            2193: "pycbc/pycbc-el7",
            1897: "pycbc/pycbc-el7",
            1883: "pycbc/pycbc-el7",
            1694: "pycbc/pycbc-el7",
            1693: "pycbc/pycbc-el7",
            1459: "pycbc/pycbc-el7",
            1455: "pycbc/pycbc-el7",
            1360: "pycbc/pycbc-el7",
            1168: "pycbc/pycbc-el7",
            1077: "pycbc/pycbc-el7",
            104: "pycbc/pycbc-el7",
            87: "pycbc/pycbc-el7",
        }

    def dependency(self) -> str:
        """Determine base image from PR mapping."""
        if self.pr.number in self._pr_mapping:
            return self._pr_mapping[self.pr.number]
        # Default to el8 for newer PRs
        return "pycbc/pycbc-el8"

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
                "run.sh",
                """#!/bin/bash
set -e
cd /opt/pycbc/src/pycbc
for f in test/test*.py; do 
    timeout 15s python "$f" 2>&1 || true
done
""",
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
set -e
cd /opt/pycbc/src/pycbc
if ! git apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
for f in test/test*.py; do 
    timeout 15s python "$f" 2>&1 || true
done
""",
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
set -e
cd /opt/pycbc/src/pycbc
if ! git apply --whitespace=nowarn /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
for f in test/test*.py; do 
    timeout 15s python "$f" 2>&1 || true
done
""",
            ),
        ]

    def dockerfile(self) -> str:
        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        base_image = self.dependency()
        
        # Check if this is el7 or el8
        is_el7 = "el7" in base_image
        
        # Build dockerfile with proper git configuration
        dockerfile_content = f"""FROM {base_image}

# Set up proxy for network access
ENV HTTP_PROXY=http://sys-proxy-rd-relay.byted.org:3128
ENV HTTPS_PROXY=http://sys-proxy-rd-relay.byted.org:3128
ENV NO_PROXY=localhost,127.0.0.1

"""
        
        # For el7, we need to install git first
        if is_el7:
            dockerfile_content += """# Install git for el7
RUN yum install -y git || echo "Warning: git installation failed, trying to continue..."

"""
        
        dockerfile_content += f"""WORKDIR /opt/pycbc/src/pycbc

# Configure git
RUN git config --global --add safe.directory /opt/pycbc/src/pycbc && \\
    git config --global http.proxy ${{HTTP_PROXY}} && \\
    git config --global https.proxy ${{HTTPS_PROXY}}

# Fetch and checkout the PR
RUN git fetch origin && \\
    git fetch --no-tags origin "pull/{self.pr.number}/head:pr-{self.pr.number}" && \\
    git checkout pr-{self.pr.number}

# Install the PR-specific version of pycbc
RUN pip install -e .

# Copy test files
{copy_commands}

RUN chmod +x /home/*.sh
"""

        return dockerfile_content


@Instance.register("gwastro", "pycbc")
class PyCBC(Instance):
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
        """
        Parse the log content from running individual Python test files.
        
        Expected format:
        - Tests that pass show: "Ran X tests ... OK"
        - Tests that fail show: "FAILED (failures=X)" or error messages
        """
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        
        # Split log by test file runs (separated by test file headers)
        lines = log.splitlines()
        
        current_test_file = None
        test_run_buffer = []
        
        for i, line in enumerate(lines):
            # Try to detect test file execution patterns
            # Pattern 1: "Running CPU unit tests for X:"
            if "Running CPU unit tests for" in line or "Running" in line and "tests" in line:
                # Process previous test run if exists
                if current_test_file and test_run_buffer:
                    self._parse_test_run(current_test_file, test_run_buffer, 
                                       passed_tests, failed_tests, skipped_tests)
                
                # Start new test run
                current_test_file = line.strip()
                test_run_buffer = [line]
            elif current_test_file:
                test_run_buffer.append(line)
            
            # Also check for test result patterns
            if line.startswith("Ran ") and " test" in line:
                # Look ahead for OK or FAILED
                if i + 2 < len(lines):
                    next_lines = lines[i+1:i+3]
                    result_line = "\n".join(next_lines)
                    
                    if "OK" in result_line and "FAILED" not in result_line:
                        # Extract test count
                        match = re.match(r"Ran (\d+) test", line)
                        if match and current_test_file:
                            count = int(match.group(1))
                            # Generate test names based on current test file
                            test_name = current_test_file.replace("Running CPU unit tests for ", "").replace(":", "").strip()
                            if test_name:
                                passed_tests.add(test_name)
                    elif "FAILED" in result_line or "ERROR" in result_line:
                        match = re.match(r"Ran (\d+) test", line)
                        if match and current_test_file:
                            test_name = current_test_file.replace("Running CPU unit tests for ", "").replace(":", "").strip()
                            if test_name:
                                failed_tests.add(test_name)
        
        # Process last test run
        if current_test_file and test_run_buffer:
            self._parse_test_run(current_test_file, test_run_buffer, 
                               passed_tests, failed_tests, skipped_tests)
        
        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
    
    def _parse_test_run(self, test_name: str, buffer: list[str], 
                       passed_tests: set, failed_tests: set, skipped_tests: set):
        """Helper method to parse a single test run from buffer."""
        buffer_text = "\n".join(buffer)
        
        # Look for "Ran X tests ... OK" pattern
        if re.search(r"Ran \d+ test.*OK", buffer_text, re.DOTALL):
            # Check it's not a false positive (no FAILED after OK)
            if "FAILED" not in buffer_text.split("OK")[-1]:
                clean_name = test_name.replace("Running CPU unit tests for ", "").replace(":", "").strip()
                if clean_name:
                    passed_tests.add(clean_name)
                return
        
        # Look for failures
        if "FAILED" in buffer_text or "ERROR" in buffer_text or "Traceback" in buffer_text:
            clean_name = test_name.replace("Running CPU unit tests for ", "").replace(":", "").strip()
            if clean_name:
                failed_tests.add(clean_name)
            return


