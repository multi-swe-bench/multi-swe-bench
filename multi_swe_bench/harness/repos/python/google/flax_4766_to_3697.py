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
ls tests
###ACTION_DELIMITER###
cat tests/run_all_tests.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3-dev libopencv-dev
###ACTION_DELIMITER###
pip install -e ".[testing]"
###ACTION_DELIMITER###
apt-get install -y python3-pip
###ACTION_DELIMITER###
python3 -m pip install -e ".[testing]"
###ACTION_DELIMITER###
python3 -m venv venv && source venv/bin/activate && python3 -m pip install -e ".[testing]"
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv && source venv/bin/activate && pip install -e ".[testing]"
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nsource venv/bin/activate\nexport JAX_NUMPY_RANK_PROMOTION=raise\nexport FLAX_PROFILE=1\npytest -v -n auto tests\npytest -v -n auto flax/nnx/tests\npytest -v -n auto docs/_ext/codediff_test.py\nfor egd in $(find examples -maxdepth 1 -mindepth 1 -type d); do\n  if [[ $egd != *"_"* ]]; then\n    pytest -v $egd\n  fi\ndone\nfor egd in $(find flax/nnx/examples -maxdepth 1 -mindepth 1 -type d); do\n  if [[ $egd != *"_"* && $egd != *"toy_examples"* ]]; then\n    pytest -v $egd\n  fi\ndone' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
source venv/bin/activate
export JAX_NUMPY_RANK_PROMOTION=raise
export FLAX_PROFILE=1
pytest -v -n auto tests
pytest -v -n auto flax/nnx/tests
pytest -v -n auto docs/_ext/codediff_test.py
for egd in $(find examples -maxdepth 1 -mindepth 1 -type d); do
  if [[ $egd != *"_"* ]]; then
    pytest -v $egd
  fi
done
for egd in $(find flax/nnx/examples -maxdepth 1 -mindepth 1 -type d); do
  if [[ $egd != *"_"* && $egd != *"toy_examples"* ]]; then
    pytest -v $egd
  fi
done

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
export JAX_NUMPY_RANK_PROMOTION=raise
export FLAX_PROFILE=1
pytest -v -n auto tests
pytest -v -n auto flax/nnx/tests
pytest -v -n auto docs/_ext/codediff_test.py
for egd in $(find examples -maxdepth 1 -mindepth 1 -type d); do
  if [[ $egd != *"_"* ]]; then
    pytest -v $egd
  fi
done
for egd in $(find flax/nnx/examples -maxdepth 1 -mindepth 1 -type d); do
  if [[ $egd != *"_"* && $egd != *"toy_examples"* ]]; then
    pytest -v $egd
  fi
done

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
export JAX_NUMPY_RANK_PROMOTION=raise
export FLAX_PROFILE=1
pytest -v -n auto tests
pytest -v -n auto flax/nnx/tests
pytest -v -n auto docs/_ext/codediff_test.py
for egd in $(find examples -maxdepth 1 -mindepth 1 -type d); do
  if [[ $egd != *"_"* ]]; then
    pytest -v $egd
  fi
done
for egd in $(find flax/nnx/examples -maxdepth 1 -mindepth 1 -type d); do
  if [[ $egd != *"_"* && $egd != *"toy_examples"* ]]; then
    pytest -v $egd
  fi
done

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


@Instance.register("google", "flax_4766_to_3697")
class FLAX_4766_TO_3697(Instance):
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
        # Extract test names and statuses using regex
        # Pattern for passed tests: matches "PASSED " followed by test name (non-whitespace)
        passed_pattern = re.compile(r"PASSED ((?:tests|examples)/[\w/]+?\.py::[\w:]+)")
        passed_tests.update(passed_pattern.findall(log))
        # Pattern for failed tests: matches line number, "FAILED", and test name
        failed_pattern = re.compile(r"FAILED\s+((?:examples|tests)/[\w/]+?\.py::[\w:]+)", re.MULTILINE)
        failed_tests.update(failed_pattern.findall(log))
        # Pattern for skipped tests: matches "SKIPPED " followed by test name (if any)
        skipped_pattern = re.compile(r"SKIPPED ((?:examples|tests)/[\w/]+?\.py::[\w:]+)")
        skipped_tests.update(skipped_pattern.findall(log))
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
