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
pip install cython numpy==1.19.5 scipy==1.5.4 pandas==1.1.5 patsy==0.5.2
###ACTION_DELIMITER###
pip install -e . --no-use-pep517
###ACTION_DELIMITER###
pip install cython==0.29.21
###ACTION_DELIMITER###
pip install -e . --no-use-pep517
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip install -e . --no-use-pep517
###ACTION_DELIMITER###
echo 'nosetests -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install nose
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
python setup.py build_ext --inplace
###ACTION_DELIMITER###
apt-get update && apt-get install -y libopenblas-dev
###ACTION_DELIMITER###
python setup.py build_ext --inplace
###ACTION_DELIMITER###
python setup.py clean && python setup.py build_ext --inplace
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install scipy==1.2.3
###ACTION_DELIMITER###
apt-get update && apt-get install -y gfortran
###ACTION_DELIMITER###
pip install scipy==1.2.3
###ACTION_DELIMITER###
apt-get update && apt-get install -y libarpack2-dev
###ACTION_DELIMITER###
pip install scipy==1.2.3
###ACTION_DELIMITER###
echo -e 'import scipy.misc\nfrom scipy.special import factorial, comb\nscipy.misc.factorial = factorial\nscipy.misc.comb = comb\nimport nose\nnose.run()' > run_tests.py && echo 'python run_tests.py' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pandas==0.24.2 scipy==1.4.1 && pip install -e . --no-use-pep517
###ACTION_DELIMITER###
pip install setuptools==57.5.0 && pip install scipy==1.4.1 pandas==0.24.2 && pip install -e . --no-use-pep517
###ACTION_DELIMITER###
sed -i 's/from scipy\.misc import factorial, comb/from scipy.special import factorial, comb/g' $(grep -rl 'from scipy.misc import factorial, comb' statsmodels/) && pip install -e . --no-use-pep517
###ACTION_DELIMITER###
grep -rl 'scipy\.misc\.factorial\|scipy\.misc\.comb' statsmodels/ | xargs sed -i 's/scipy\.misc\.factorial/scipy.special.factorial/g; s/scipy\.misc\.comb/scipy.special.comb/g'
###ACTION_DELIMITER###
grep -rl --include='*.py' 'from scipy\.misc import factorial, comb' statsmodels/ | xargs sed -i 's/from scipy\.misc import factorial, comb/from scipy.special import factorial, comb/g'
###ACTION_DELIMITER###
grep -rl --include='*.py' 'scipy\.misc\.(factorial|comb)' statsmodels/ | xargs sed -i 's/scipy\.misc\.(factorial|comb)/scipy.special.\1/g'
###ACTION_DELIMITER###
grep -rl --include='*.py' 'scipy\.misc\.(factorial|comb)' statsmodels/ | xargs sed -i -E 's/scipy\.misc\.(factorial|comb)/scipy.special.\1/g'
###ACTION_DELIMITER###
grep -r 'scipy\.misc' statsmodels/
###ACTION_DELIMITER###
grep -rl --include='*.py' 'scipy\.misc' statsmodels/ | xargs sed -i 's/scipy\.misc\./scipy.special./g'
###ACTION_DELIMITER###
echo 'nosetests -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
grep -rl --include='*.py' 'scipy\.misc' statsmodels/ | xargs sed -i -E 's/(from scipy\.misc import) (factorial|comb|logsumexp|factorial2)/\1 \2/g; s/scipy\.misc\.(factorial|comb|logsumexp|factorial2)/scipy.special.\1/g'
###ACTION_DELIMITER###
grep -r 'scipy\.misc' statsmodels/ && bash test_commands.sh
###ACTION_DELIMITER###
grep -rl --include='*.py' 'scipy\.misc' statsmodels/ | xargs sed -i 's/scipy\.misc/scipy.special/g'
###ACTION_DELIMITER###
grep -rl --include='*.py' 'scipy\.misc' statsmodels/ && pip install -e . --no-use-pep517 && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
nosetests -v

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
nosetests -v

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
nosetests -v

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
RUN git clone https://github.com/statsmodels/statsmodels.git /home/statsmodels

WORKDIR /home/statsmodels
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("statsmodels", "statsmodels_4603_to_3351")
class STATSMODELS_4603_TO_3351(Instance):
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
        test_status = {}  # Track the latest status of each test
        # Regex patterns for additional status lines
        error_pattern = re.compile(r'(?:(AssertionError|Error|FAILED|ERROR):\s*([\w.]+)|([\w.]+):\s*(AssertionError|Error|FAILED|ERROR)|([\w.]+)\s+(?:failed|error)|test (?:failed|error):\s*([\w.]+)|(?:failed|error) in\s*([\w.]+))', re.IGNORECASE | re.MULTILINE)
        skip_pattern = re.compile(r'^(SKIP|SKIPPED):\s*([\w.]+)$', re.MULTILINE)
        # Process lines with '...' (primary status lines)
        for line in log.split('\n'):
            line = line.strip()
            if '...' in line:
                parts = line.split('...', 1)
                if len(parts) != 2:
                    continue
                test_part = parts[0].strip()
                status_part = parts[1].strip()
                # Extract test name (remove line number prefix)
                test_name = test_part.split(']', 1)[1].strip() if ']' in test_part else test_part
                # Extract status
                status = status_part.split()[0].lower() if status_part else ''
                test_status[test_name] = status  # Update with latest status
        # Process ERROR lines (update status to 'error')
        for match in error_pattern.finditer(log):
            test_name = match.group(2) or match.group(3) or match.group(5) or match.group(6) or match.group(7)
            if test_name:
                test_status[test_name.strip()] = 'error'  # Override with error status
        # Process SKIP/SKIPPED lines (update status to 'skipped')
        for match in skip_pattern.finditer(log):
            test_name = match.group(2).strip()
            test_status[test_name] = 'skipped'  # Override with skipped status
        # Categorize tests based on latest status
        for test_name, status in test_status.items():
            if status == 'ok':
                passed_tests.add(test_name)
            elif status.startswith('fail') or status == 'error':
                failed_tests.add(test_name)
            elif status == 'skipped':
                skipped_tests.add(test_name)
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
