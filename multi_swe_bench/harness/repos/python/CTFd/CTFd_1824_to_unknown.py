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
                """apt-get update && apt-get install -y build-essential python3-dev python3-pip libffi-dev
###ACTION_DELIMITER###
pip3 install -r requirements.txt --break-system-packages
###ACTION_DELIMITER###
apt-get install -y libev-dev
###ACTION_DELIMITER###
sed -i 's/gevent==20.9.0/gevent==23.9.1/' requirements.txt && sed -i 's/greenlet==0.4.17/greenlet==3.0.0/' requirements.txt
###ACTION_DELIMITER###
pip3 install -r requirements.txt --break-system-packages
###ACTION_DELIMITER###
apt-get install -y libxml2-dev libxslt1-dev
###ACTION_DELIMITER###
pip3 install -r requirements.txt --break-system-packages
###ACTION_DELIMITER###
sed -i 's/lxml==4.6.2/lxml==4.9.3/' requirements.txt
###ACTION_DELIMITER###
pip3 install -r requirements.txt --break-system-packages
###ACTION_DELIMITER###
echo -e 'export FLASK_APP=CTFd
flask db upgrade
pytest -v --setup-show' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip3 install pytest six==1.16.0 --break-system-packages
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/html5lib==1.0.1/html5lib==1.1/' requirements.txt && pip3 install -r requirements.txt --break-system-packages
###ACTION_DELIMITER###
apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && apt-get install -y python3.9 python3.9-venv python3.9-dev
###ACTION_DELIMITER###
pip3 install six --break-system-packages
###ACTION_DELIMITER###
pip3 install six==1.16.0 --break-system-packages
###ACTION_DELIMITER###
python3.9 -m venv venv
###ACTION_DELIMITER###
apt-get install -y python3.9 python3.9-venv python3.9-dev
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y && apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.9 python3.9-venv python3.9-dev
###ACTION_DELIMITER###
python3.9 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate
###ACTION_DELIMITER###
pip install -r requirements.txt
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
export FLASK_APP=CTFd
flask db upgrade
pytest -v --setup-show' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install pytest && echo -e 'source venv/bin/activate\nexport FLASK_APP=CTFd\nflask db upgrade\npytest -v --setup-show' > test_commands.sh
###ACTION_DELIMITER###
sed -i 's/urllib3==1.25.11/urllib3==1.26.15/' requirements.txt && source venv/bin/activate && pip install -r requirements.txt && echo -e '#!/bin/bash\nvenv/bin/python -m flask db upgrade\nvenv/bin/pytest -v --setup-show' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
sed -i 's/urllib3==1.26.15/urllib3==1.25.11/' requirements.txt && source venv/bin/activate && pip install -r requirements.txt && echo -e '#!/bin/bash\nsource venv/bin/activate\nexport FLASK_APP=CTFd\nflask db upgrade\npytest -v --setup-show' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install freezegun moto
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip uninstall -y moto && pip install moto==1.3.16
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
source venv/bin/activate
export FLASK_APP=CTFd
flask db upgrade
pytest -v --setup-show

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
export FLASK_APP=CTFd
flask db upgrade
pytest -v --setup-show

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
export FLASK_APP=CTFd
flask db upgrade
pytest -v --setup-show

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
RUN git clone https://github.com/CTFd/CTFd.git /home/CTFd

WORKDIR /home/CTFd
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("CTFd", "CTFd_1824_to_unknown")
class CTFD_1824_TO_UNKNOWN(Instance):
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
        passed_tests = set() # Tests that passed successfully
        failed_tests = set() # Tests that failed
        skipped_tests = set() # Tests that were skipped
        import re
        import json
        # Parse passed tests
        passed_pattern = re.compile(r'(tests/[^:]+::test_\w+)PASSED')
        passed_tests.update(passed_pattern.findall(log))
        # Parse failed tests
        failed_pattern = re.compile(r'FAILED (tests/[^:]+::test_\w+)')
        failed_tests.update(failed_pattern.findall(log))
        # Parse skipped tests
        skipped_pattern = re.compile(r'(tests/[^:]+::test_\w+)SKIPPED')
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
