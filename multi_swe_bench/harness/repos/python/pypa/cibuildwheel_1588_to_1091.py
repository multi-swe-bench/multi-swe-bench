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
                """ls -la
###ACTION_DELIMITER###
pip install -e .[test]
###ACTION_DELIMITER###
echo 'pytest -v unit_test test --durations 0 --timeout=2400' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'pytest -v unit_test --durations 0 --timeout=2400
pytest -v test --durations 0 --timeout=2400' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libssl-dev podman
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y ca-certificates && ln -s /usr/bin/podman /usr/bin/docker && bash test_commands.sh
###ACTION_DELIMITER###
echo 'nox -s test' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip install nox && echo 'nox -s test' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'nox -s test-3.11' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
nox -l
###ACTION_DELIMITER###
echo 'nox -s tests' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v unit_test test --run-podman --durations 0 --timeout=2400' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'pytest -v unit_test --durations 0 --timeout=2400
pytest -v test --run-podman --durations 0 --timeout=2400' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export CIBW_CONTAINER_ENGINE=podman
pytest -v unit_test --durations 0 --timeout=2400
pytest -v test --run-podman --durations 0 --timeout=2400' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
podman system service --time=0 &
export CIBW_CONTAINER_ENGINE=podman
export CIBW_MANYLINUX_X86_64_IMAGE=quay.io/pypa/manylinux2014_x86_64
export CIBW_MUSLLINUX_X86_64_IMAGE=quay.io/pypa/musllinux_1_1_x86_64
pytest -v unit_test test --run-podman --durations 0 --timeout=2400' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export CIBW_CONTAINER_ENGINE=podman
pytest -v unit_test --durations 0 --timeout=2400
pytest -v test --durations 0 --timeout=2400' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pip install nox
nox -s tests' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export CIBW_CONTAINER_ENGINE=podman
pip install nox
nox -s tests -- --run-podman' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export CIBW_CONTAINER_ENGINE=podman
pytest -v unit_test --durations 0 --timeout=2400
pytest -v test --run-podman --durations 0 --timeout=2400' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
export CIBW_CONTAINER_ENGINE=podman
pytest -v unit_test --durations 0 --timeout=2400
pytest -v test --run-podman --durations 0 --timeout=2400

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
export CIBW_CONTAINER_ENGINE=podman
pytest -v unit_test --durations 0 --timeout=2400
pytest -v test --run-podman --durations 0 --timeout=2400

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
export CIBW_CONTAINER_ENGINE=podman
pytest -v unit_test --durations 0 --timeout=2400
pytest -v test --run-podman --durations 0 --timeout=2400

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

# Choose an appropriate base image based on the project's requirements - replace python:3.11-slim with actual base image
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
RUN git clone https://github.com/pypa/cibuildwheel.git /home/cibuildwheel

WORKDIR /home/cibuildwheel
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pypa", "cibuildwheel_1588_to_1091")
class CIBUILDWHEEL_1588_TO_1091(Instance):
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
        passed_tests: set[str] = set()
        failed_tests: set[str] = set()
        skipped_tests: set[str] = set()
        import re
        # Extract passed tests (lines like 'test_name PASSED ...')
        passed_pattern = re.compile(r'^(.*?) PASSED\b', re.MULTILINE)
        passed_tests.update(passed_pattern.findall(log))
        # Extract failed tests (lines like 'FAILED test_name - ...')
        failed_pattern = re.compile(r'^FAILED (.*?)(?: -|$)', re.MULTILINE)
        failed_tests.update(failed_pattern.findall(log))
        # Extract skipped tests (lines like 'test_name SKIPPED ...' or 'SKIPPED test_name')
        skipped_pattern = re.compile(r'^(.*?) SKIPPED\b|^SKIPPED (.*?)(?: -|$)', re.MULTILINE)
        for match in skipped_pattern.findall(log):
            test = match[0] if match[0] else match[1]
            if test:
                skipped_tests.add(test)
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
