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
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo -e 'python -m pytest -v --pyargs nilearn --cov=nilearn
pytest -v --doctest-glob=*.rst $(find doc/ -name *.rst)
pytest -v doc/_additional_doctests.txt' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'python -m pytest -v --pyargs nilearn
pytest -v --doctest-glob=*.rst doc/ doc/_additional_doctests.txt' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/numpy/numpy<1.20/' requirements-dev.txt && sed -i 's/matplotlib/matplotlib<3.6/' requirements-dev.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo 'contourpy<=1.0.5' >> requirements-dev.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
python setup.py build_ext -i
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/nibabel/nibabel<4.0.0/' requirements-dev.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
python setup.py build_ext -i
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export MPLBACKEND=Agg
python -m pytest -v --pyargs nilearn
pytest -v --doctest-glob=*.rst doc/ doc/_additional_doctests.txt' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/scikit-learn/scikit-learn<1.1/' requirements-dev.txt && sed -i 's/joblib/joblib<1.0/' requirements-dev.txt && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
export MPLBACKEND=Agg
python -m pytest -v --pyargs nilearn
pytest -v --doctest-glob=*.rst doc/ doc/_additional_doctests.txt

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
export MPLBACKEND=Agg
python -m pytest -v --pyargs nilearn
pytest -v --doctest-glob=*.rst doc/ doc/_additional_doctests.txt

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
export MPLBACKEND=Agg
python -m pytest -v --pyargs nilearn
pytest -v --doctest-glob=*.rst doc/ doc/_additional_doctests.txt

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
RUN git clone https://github.com/nilearn/nilearn.git /home/nilearn

WORKDIR /home/nilearn
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("nilearn", "nilearn_2770_to_2559")
class NILEARN_2770_TO_2559(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        import json
        # Regex pattern to identify test names
        test_name_pattern = re.compile(r'(nilearn/[^:]+::[\w_.]+)')
        lines = log.split('\n')
        processed_tests = set()
        for i, line in enumerate(lines):
            test_names = test_name_pattern.findall(line)
            for test_name in test_names:
                if test_name in processed_tests:
                    continue
                # Check current line for status
                if 'PASSED' in line:
                    passed_tests.add(test_name)
                    processed_tests.add(test_name)
                elif 'FAILED' in line:
                    failed_tests.add(test_name)
                    processed_tests.add(test_name)
                elif 'SKIPPED' in line:
                    skipped_tests.add(test_name)
                    processed_tests.add(test_name)
                else:
                    # Look ahead up to 5 lines for status
                    for j in range(i + 1, len(lines)):
                        # Stop if next test is found
                        if test_name_pattern.search(lines[j]):
                            break
                        next_line = lines[j]
                        if 'PASSED' in next_line:
                            passed_tests.add(test_name)
                            processed_tests.add(test_name)
                            break
                        elif 'FAILED' in next_line:
                            failed_tests.add(test_name)
                            processed_tests.add(test_name)
                            break
                        elif 'SKIPPED' in next_line:
                            skipped_tests.add(test_name)
                            processed_tests.add(test_name)
                            break
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
