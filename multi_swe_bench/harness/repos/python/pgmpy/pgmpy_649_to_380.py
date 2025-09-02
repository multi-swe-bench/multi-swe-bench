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
python3 --version
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
python3 --version
###ACTION_DELIMITER###
echo -e 'networkx>=3.2.1
numpy>=1.26.0
scipy>=1.11.0
pandas>=2.1.4
pyparsing>=3.1.1
mock>=5.1.0
nose>=1.3.7' > requirements-dev.txt
###ACTION_DELIMITER###
pip3 install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3.12 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip3 install -r requirements-dev.txt
###ACTION_DELIMITER###
echo -e '#!/bin/bash
source venv/bin/activate
nosetests -v' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
pip3 install pytest pytest-nose
###ACTION_DELIMITER###
pip3 install pytest
###ACTION_DELIMITER###
echo -e '#!/bin/bash
source venv/bin/activate
pytest -v' > test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
pip3 install six
###ACTION_DELIMITER###
ls pgmpy/extern
###ACTION_DELIMITER###
sed -i 's/from pgmpy.extern.six.moves/from six.moves/' pgmpy/extern/tabulate.py
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from pgmpy.extern.six.moves/from six.moves/' pgmpy/factors/Factor.py
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from pgmpy.extern.six.moves/from six.moves/' pgmpy/factors/FactorSet.py
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from pgmpy.extern.six.moves/from six.moves/' pgmpy/factors/CPD.py
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
sed -i 's/from pgmpy.extern.six.moves/from six.moves/' pgmpy/factors/JointProbabilityDistribution.py
###ACTION_DELIMITER###
grep -r 'pgmpy.extern.six.moves' pgmpy/
###ACTION_DELIMITER###
grep -rl 'pgmpy.extern.six.moves' pgmpy/ | xargs sed -i 's/from pgmpy\.extern\.six\.moves/from six.moves/g'
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
grep -rl 'numpy.product' pgmpy/ | xargs sed -i 's/numpy.product/numpy.prod/g'
###ACTION_DELIMITER###
grep -rl 'np.product' pgmpy/ | xargs sed -i 's/np.product/np.prod/g'
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
grep -rl '\.node' pgmpy/
###ACTION_DELIMITER###
grep -rl '\.node' pgmpy/ | xargs sed -i 's/\.node/\.nodes/g'
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
grep -rl 'nodess' pgmpy/ | xargs sed -i 's/nodess/nodes/g'
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
grep -rl 'numpy\.int' pgmpy/ | xargs sed -i 's/numpy\.int/int/g'
###ACTION_DELIMITER###
grep -rl 'np\.int' pgmpy/ | xargs sed -i 's/np\.int/int/g'"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
source venv/bin/activate
pytest -v

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
pytest -v

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
pytest -v

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
RUN git clone https://github.com/pgmpy/pgmpy.git /home/pgmpy

WORKDIR /home/pgmpy
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pgmpy", "pgmpy_649_to_380")
class PGMPY_649_TO_380(Instance):
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
        lines = log.split('\n')
        pattern1 = re.compile(r'^(.*?)\s+(PASSED|FAILED|SKIPPED)\s+\[\s*\d+%\s*\]$')
        pattern2 = re.compile(r'^(PASSED|FAILED|SKIPPED)\s+(.*)$')
        for line in lines:
            line = line.strip()
            # Match lines like 'test_name PASSED [ 0%]'
            match = pattern1.match(line)
            if match:
                test_name = match.group(1).strip()
                status = match.group(2)
                if '.py::' in test_name:
                    if status == 'PASSED':
                        passed_tests.add(test_name)
                    elif status == 'FAILED':
                        failed_tests.add(test_name)
                    elif status == 'SKIPPED':
                        skipped_tests.add(test_name)
                continue
            # Match lines like 'FAILED test_name'
            match = pattern2.match(line)
            if match:
                status = match.group(1)
                test_name = match.group(2).strip()
                if '.py::' in test_name:
                    if status == 'PASSED':
                        passed_tests.add(test_name)
                    elif status == 'FAILED':
                        failed_tests.add(test_name)
                    elif status == 'SKIPPED':
                        skipped_tests.add(test_name)
                continue
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
