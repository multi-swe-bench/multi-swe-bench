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
                """apt-get update && apt-get install -y python3 python3-pip python3-venv python3-distutils python3-setuptools
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip python3-venv python3-setuptools
###ACTION_DELIMITER###
python3 -m venv --system-site-packages venv && source venv/bin/activate && pip install . && pip install -r requirements-tests.txt
###ACTION_DELIMITER###
echo -e '#!/bin/bash
xonsh run-tests.xsh -v' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install pytest==7.4.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install pytest==6.2.5
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nsource venv/bin/activate\nxonsh run-tests.xsh -v' > test_commands.sh && source venv/bin/activate && pip install pytest-timeout==2.1.0 pytest-flake8==1.0.7
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.9 python3.9-pip python3.9-venv python3.9-distutils python3.9-setuptools && python3.9 -m venv --system-site-packages venv && source venv/bin/activate && pip install . && pip install -r requirements-tests.txt
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.9 python3.9-pip python3.9-venv python3.9-distutils python3.9-setuptools
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nsource venv/bin/activate\npytest -v -p no:xonsh tests/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.9 python3.9-pip python3.9-venv python3.9-distutils python3.9-setuptools
###ACTION_DELIMITER###
apt-get install -y python3.9 python3.9-venv python3.9-distutils && python3.9 -m ensurepip --upgrade && python3.9 -m pip install setuptools
###ACTION_DELIMITER###
python3.9 -m venv --system-site-packages venv && source venv/bin/activate && pip install . && pip install -r requirements-tests.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip install ply==3.11 && pip install . && pip install -r requirements-tests.txt
###ACTION_DELIMITER###
apt-get install -y python3.9-dev build-essential && python3.9 -m venv venv && source venv/bin/activate && pip install ply==3.11 && pip install . && pip install -r requirements-tests.txt
###ACTION_DELIMITER###
apt-get install -y python3.8 python3.8-venv python3.8-dev python3.8-distutils && python3.8 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install ply==3.11 && pip install . && pip install -r requirements-tests.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip install ply==3.11 && python setup.py build_tables && pip install . && pip install -r requirements-tests.txt
###ACTION_DELIMITER###
python3.8 -m venv --system-site-packages venv && source venv/bin/activate && pip install setuptools wheel ply==3.11 && python setup.py build_tables && pip install . && pip install -r requirements-tests.txt
###ACTION_DELIMITER###
source venv/bin/activate && pip install setuptools wheel ply==3.11 && pip install . && pip install -r requirements-tests.txt
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nsource venv/bin/activate\npytest -v tests/' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install pytest==7.0.0 && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nsource venv/bin/activate\npytest -v -p no:xonsh tests/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install ply==3.12 && pip install --force-reinstall . && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y python3.7 python3.7-venv python3.7-dev python3.7-distutils && python3.7 -m venv venv && source venv/bin/activate && pip install setuptools wheel ply==3.11 && pip install . && pip install -r requirements-tests.txt && echo -e '#!/bin/bash\nsource venv/bin/activate\npytest -v -p no:xonsh tests/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###

###ACTION_DELIMITER###

###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
source venv/bin/activate
pytest -v -p no:xonsh tests/

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
pytest -v -p no:xonsh tests/

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
pytest -v -p no:xonsh tests/

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
RUN git clone https://github.com/xonsh/xonsh.git /home/xonsh

WORKDIR /home/xonsh
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("xonsh", "xonsh_3126_to_3068")
class XONSH_3126_TO_3068(Instance):
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
        # Pattern for passed tests: captures full test name (including spaces) until PASSED
        passed_pattern = re.compile(r'(tests/.*?)\s+PASSED')
        # Pattern for failed tests: captures full test name until space or end of line (flexible)
        failed_pattern = re.compile(r'(?:FAILED|ERROR)\s+(tests/.*?)(?=\s|$)')
        # Pattern for skipped tests: handles 'tests/... SKIPPED' and 'SKIPPED (text) tests/...'
        skipped_pattern = re.compile(r'(tests/.*?)\s+SKIPPED|SKIPPED.*?(tests/.*?)(?=\s|$)')
        # Extract test names
        passed_tests.update(passed_pattern.findall(log))
        failed_tests.update(failed_pattern.findall(log))
        # Flatten tuples from skipped matches (extract non-empty test names)
        skipped_matches = skipped_pattern.findall(log)
        skipped_tests.update([match[0] if match[0] else match[1] for match in skipped_matches])
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
