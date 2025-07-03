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

    def dependency(self) -> Image | None:
        return "python:3.6-buster"
    
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
                """ls -al
###ACTION_DELIMITER###

###ACTION_DELIMITER###
ls -al benchmarks
###ACTION_DELIMITER###
ls -al docs
###ACTION_DELIMITER###
ls -al tests
###ACTION_DELIMITER###
echo 'pytest --cov=pydantic' > /home/pydantic/test_commands.sh
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
bash /home/pydantic/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest --cov=pydantic

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
pytest --cov=pydantic

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
pytest --cov=pydantic

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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.6-buster

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
RUN git clone https://github.com/pydantic/pydantic.git /home/pydantic

WORKDIR /home/pydantic
RUN git reset --hard
RUN git checkout 9b98d14ff1c534b1f986755962c8cae5091a6a23

RUN git checkout {pr.base.sha}"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pydantic", "pydantic_v0_25")
class PYDANTIC_V0_25(Instance):
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
        import json
        # Extract failed test names from the FAILURES section
        failures_section = re.search(r'=+ FAILURES =+[\s\S]+?(?=\n=+|\Z)', log)
        failed_names = []
        if failures_section:
            # Find lines like: ____________________________ test_name _____________________________
            failed_names = re.findall(r'^_{5,}\s+([\w\d_]+)\s+_{5,}$', failures_section.group(0), re.MULTILINE)
            failed_tests.update(failed_names)
        # Parse summary lines for test results per file
        summary_line_re = re.compile(r'^(tests/[^\s:]+\.py)\s+([.sF]+)', re.MULTILINE)
        synthetic_failed = set()
        for match in summary_line_re.finditer(log):
            file_name = match.group(1)
            results = match.group(2)
            pass_idx = skip_idx = fail_idx = 1
            for c in results:
                if c == '.':
                    passed_tests.add(f"{file_name}::test_passed_{pass_idx}")
                    pass_idx += 1
                elif c == 'F':
                    synthetic_name = f"{file_name}::test_failed_{fail_idx}"
                    failed_tests.add(synthetic_name)
                    synthetic_failed.add(synthetic_name)
                    fail_idx += 1
                elif c == 's':
                    skipped_tests.add(f"{file_name}::test_skipped_{skip_idx}")
                    skip_idx += 1
        # If we have real failed test names, use them instead of synthetic
        if failures_section and failed_names:
            failed_tests = set(failed_names)
            # Remove synthetic failed names from passed/skipped sets if any overlap
            passed_tests = {t for t in passed_tests if t not in synthetic_failed}
            skipped_tests = {t for t in skipped_tests if t not in synthetic_failed}
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
