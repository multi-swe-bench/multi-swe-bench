import re
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

    def dependency(self) -> Image | None:
        return "python:3.11-slim"

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
ls -al conans
###ACTION_DELIMITER###
python -m pip install -r conans/requirements.txt && python -m pip install -r conans/requirements_server.txt && python -m pip install -r conans/requirements_dev.txt
###ACTION_DELIMITER###
echo 'export PYTHONPATH=$PYTHONPATH:$(pwd)\npython -m pytest . --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash /home/conan/test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYTHONPATH=$PYTHONPATH:$(pwd)\npython -m pytest . --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash /home/conan/test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m pytest . --no-header -rA --tb=no -p no:cacheprovider

""".format(pr=self.pr),
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
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m pytest . --no-header -rA --tb=no -p no:cacheprovider

""".format(pr=self.pr),
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
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m pytest . --no-header -rA --tb=no -p no:cacheprovider

""".format(pr=self.pr),
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
FROM python:3.11-slim

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
RUN git clone https://github.com/conan-io/conan.git /home/conan

WORKDIR /home/conan
RUN git reset --hard
RUN git checkout a474e3d67c1a0acfc4f8fa7db2f71de4bd089466

RUN git checkout {pr.base.sha}"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("conan-io", "conan_2_5_0")
class CONAN_2_5_0(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        # Regex patterns for test result lines
        # Example: PASSED test/functional/only_source_test.py::OnlySourceTest::test_build_policies_in_conanfile
        passed_pat = re.compile(r"^PASSED\s+([\w/\.:-]+)", re.MULTILINE)
        failed_pat = re.compile(r"^FAILED\s+([\w/\.:-]+)", re.MULTILINE)
        xfail_pat = re.compile(r"^XFAIL\s+([\w/\.:-]+)", re.MULTILINE)
        # SKIPPED lines do not always have full test name, so we rely on summary lines for skipped tests
        # But if present, we can try to extract file:line
        skipped_pat = re.compile(r"^SKIPPED.*?([\w/\.]+\.py(?:::\w+)*).*", re.MULTILINE)
        # Find all matches
        passed_tests.update(passed_pat.findall(log))
        failed_tests.update(failed_pat.findall(log))
        skipped_tests.update(xfail_pat.findall(log))
        # For SKIPPED, only add if full test name is present
        for m in skipped_pat.findall(log):
            if "::" in m:
                skipped_tests.add(m)
        # Remove skipped tests from passed/failed if overlap
        passed_tests -= skipped_tests
        failed_tests -= skipped_tests

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
