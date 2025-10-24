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
                """ls
###ACTION_DELIMITER###
ls -a
###ACTION_DELIMITER###
ls .github
###ACTION_DELIMITER###
ls .github/workflows
###ACTION_DELIMITER###
pip install -e .[tests]
###ACTION_DELIMITER###
apt-get update && apt-get install -y libhdf5-dev
###ACTION_DELIMITER###
pip install -e .[tests]
###ACTION_DELIMITER###
export HDF5_DIR=/usr && pip install -e .[tests]
###ACTION_DELIMITER###
pip install --upgrade pip && pip install tables --install-option='--hdf5=/usr' && pip install -e .[tests]
###ACTION_DELIMITER###
export HDF5_DIR=/usr && pip install tables && pip install -e .[tests]
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.10 python3.10-dev python3.10-venv
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y -t bullseye-backports python3.10 python3.10-dev python3.10-venv
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bookworm-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y -t bookworm-backports python3.10 python3.10-dev python3.10-venv
###ACTION_DELIMITER###
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba && ./bin/micromamba create -f environment.yml -y && ./bin/micromamba activate cta-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl bzip2
###ACTION_DELIMITER###
sed -i '/bullseye-backports/d' /etc/apt/sources.list && apt-get update && apt-get install -y curl bzip2
###ACTION_DELIMITER###
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba && ./bin/micromamba env create -f environment.yml -y && ./bin/micromamba activate cta-dev
###ACTION_DELIMITER###
eval "$(./bin/micromamba shell hook --shell bash)" && ./bin/micromamba activate cta-dev
###ACTION_DELIMITER###
./bin/micromamba run -n cta-dev pip install -e .[tests]
###ACTION_DELIMITER###
echo 'pytest -v -n auto --dist loadscope --doctest-modules --doctest-glob=*.rst --ignore=docs/conf.py src/ctapipe docs' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo './bin/micromamba run -n cta-dev pytest -v -n auto --dist loadscope --doctest-modules --doctest-glob=*.rst --ignore=docs/conf.py src/ctapipe docs' > test_commands.sh && chmod +x test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
./bin/micromamba run -n cta-dev pytest -v -n auto --dist loadscope --doctest-modules --doctest-glob=*.rst --ignore=docs/conf.py src/ctapipe docs

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
./bin/micromamba run -n cta-dev pytest -v -n auto --dist loadscope --doctest-modules --doctest-glob=*.rst --ignore=docs/conf.py src/ctapipe docs

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
./bin/micromamba run -n cta-dev pytest -v -n auto --dist loadscope --doctest-modules --doctest-glob=*.rst --ignore=docs/conf.py src/ctapipe docs

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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
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
RUN git clone https://github.com/cta-observatory/ctapipe.git /home/ctapipe

WORKDIR /home/ctapipe
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("cta-observatory", "ctapipe_2611_to_2483")
class CTAPIPE_2611_TO_2483(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re

        # Regex pattern to match test status and name (handles [gw...] and percentage prefixes)
        # Regex for PASSED, FAILED, XFAIL (with :: in test name)
        main_pattern = r"\b(PASSED|FAILED|XFAIL)\b.*?(src/.*?::.*?)(?=\s|$)"
        main_matches = re.findall(main_pattern, log)
        for status, test_name in main_matches:
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status == "FAILED":
                failed_tests.add(test_name)
            elif status == "XFAIL":
                skipped_tests.add(test_name)  # XFAIL is considered skipped
        # Regex for SKIPPED tests in summary (extract test name from parentheses)
        skipped_pattern = r"SKIPPED.*?(src/.*?\.py):\d+.*?\((.*?)\)"
        skipped_matches = re.findall(skipped_pattern, log)
        for file_path, test_name in skipped_matches:
            full_test_name = f"{file_path}::{test_name}"
            skipped_tests.add(full_test_name)
        # Remove skipped tests from passed/failed to avoid overlap
        passed_tests -= skipped_tests
        failed_tests -= skipped_tests
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
