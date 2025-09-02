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
apt-get install -y python3-pip
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y python3-pip
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
apt-get install -y python3-numpy python3-scipy python3-matplotlib python3-pandas
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
apt-get install -y pytest
###ACTION_DELIMITER###
apt-get install -y python3-pytest
###ACTION_DELIMITER###
apt-get install -y python3-statsmodels
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
apt-get install -y python3-nose
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
apt-get remove -y python3-pandas
###ACTION_DELIMITER###
pip install pandas==0.22.0 --break-system-packages
###ACTION_DELIMITER###
apt-get install -y python3-statsmodels
###ACTION_DELIMITER###
echo 'pytest --no-header -rA --tb=no -p no:cacheprovider' > /home/seaborn/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
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
RUN git clone https://github.com/mwaskom/seaborn.git /home/seaborn

WORKDIR /home/seaborn
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("mwaskom", "seaborn_2079_to_1935")
class SEABORN_2079_TO_1935(Instance):
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
        passed_tests = set() 
        failed_tests = set() 
        skipped_tests = set() 
        import re
        for line in log.splitlines():
            if line.startswith("PASSED"):
                match = re.match(r"PASSED\s+(.*)", line)
                if match:
                    passed_tests.add(match.group(1).strip())
            elif line.startswith("FAILED"):
                match = re.match(r"FAILED\s+([^\s]+)", line)
                if match:
                    failed_tests.add(match.group(1).strip())
            elif re.match(r"^seaborn.*\s+[.sFE]+",line):
                test_file_match = re.match(r"([^\s]+)",line)
                if test_file_match:
                    test_file = test_file_match.group(1)
                    statuses = re.findall(r"(\w)(?:\[\d+%\s\]]+)$",line)
                    if statuses:
                        for status in statuses[0]:
                            if status == 's':
                               # This is a placeholder as the test name is not on this line
                               # The actual test name appears later in the log
                               pass
        # Look for skipped tests in the summary info, since they are not always explicitly marked
        skipped_summary = re.search(r"=+ short test summary info =+", log)
        if skipped_summary:
            summary_text = log[skipped_summary.end():]
            skipped_matches = re.findall(r"SKIPPED \[\d+\] ([^\n]+)", summary_text)
            for test_name in skipped_matches:
                # The test name might contain the file path and reason, we only want the test name part.
                file_and_reason = test_name.split(" - ")
                if len(file_and_reason) > 1:
                     skipped_tests.add(file_and_reason[0].strip())
                else:
                    # Handle cases where there is no explicit reason after the test name
                    # This could be improved with more specific log analysis if needed
                    parts = test_name.split(":")
                    if len(parts) > 2:
                        skipped_tests.add(f"{parts[0]}:{parts[1]}")
                    else: 
                        skipped_tests.add(test_name.strip())
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
