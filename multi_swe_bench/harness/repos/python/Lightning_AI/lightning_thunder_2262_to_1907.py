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
                """ls -la
###ACTION_DELIMITER###
ls -la .github
###ACTION_DELIMITER###
ls -la .github/workflows
###ACTION_DELIMITER###
pip install torch==2.6.0 torchvision==0.21 nvfuser-cu124-torch26
###ACTION_DELIMITER###
pip install torch==2.6.0 torchvision==0.21 nvfuser-cu124-torch26 --extra-index-url https://pypi.nvidia.com/
###ACTION_DELIMITER###
pip install torch==2.6.0 torchvision==0.21
###ACTION_DELIMITER###
pip install lightning-thunder
###ACTION_DELIMITER###
pip install git+https://github.com/Lightning-AI/lightning-thunder.git@main
###ACTION_DELIMITER###
pip install git+https://github.com/Lightning-AI/lightning-thunder.git@74ac17eb1676c064b48ae48a8935ff062a7bcdad
###ACTION_DELIMITER###
pip install -r requirements/base.txt && pip install -r requirements/test.txt && pip install -e .
###ACTION_DELIMITER###
pip install networkx==3.2.1 && pip install --no-deps git+https://github.com/Lightning-AI/lightning-thunder.git@74ac17eb1676c064b48ae48a8935ff062a7bcdad
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.10 python3.10-pip
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.10 && curl https://bootstrap.pypa.io/get-pip.py | python3.10
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl python3.10
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python3.10 -t bullseye-backports
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bookworm-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python3.10 -t bookworm-backports
###ACTION_DELIMITER###
sed -i '/bullseye-backports/d' /etc/apt/sources.list && apt-get update && apt-get install -y python3.10
###ACTION_DELIMITER###
cat pyproject.toml
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python3.10 -t bullseye-backports
###ACTION_DELIMITER###
sed -i '/backports/d' /etc/apt/sources.list && echo 'deb http://deb.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y -t bullseye-backports python3.10
###ACTION_DELIMITER###
sed -i '/backports/d' /etc/apt/sources.list && echo 'deb [trusted=yes] http://archive.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y -t bullseye-backports python3.10
###ACTION_DELIMITER###
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && bash Miniconda3-latest-Linux-x86_64.sh -b -p /miniconda && /miniconda/bin/conda create -y -n py310 python=3.10 && /miniconda/bin/conda init bash && source ~/.bashrc && conda activate py310
###ACTION_DELIMITER###
/miniconda/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main --channel https://repo.anaconda.com/pkgs/r
###ACTION_DELIMITER###
/miniconda/bin/conda create -y -n py310 python=3.10
###ACTION_DELIMITER###
conda activate py310
###ACTION_DELIMITER###
source ~/.bashrc && conda activate py310
###ACTION_DELIMITER###
source /miniconda/envs/py310/bin/activate
###ACTION_DELIMITER###
/miniconda/envs/py310/bin/python --version
###ACTION_DELIMITER###
/miniconda/envs/py310/bin/pip install -r requirements/base.txt && /miniconda/envs/py310/bin/pip install -r requirements/test.txt
###ACTION_DELIMITER###
/miniconda/envs/py310/bin/pip install -e .
###ACTION_DELIMITER###
echo -e '#!/bin/bash\n\npytest thunder/tests/ --ignore=thunder/tests/distributed --ignore=thunder/tests/test_ops.py --ignore=thunder/tests/test_grad.py -v --datefmt="%Y%m%d-%H:%M:%S.%f" --random-order -n 4 --durations=250\npytest thunder/tests/distributed/ -v --datefmt="%Y%m%d-%H:%M:%S.%f" --random-order --durations=250\npytest thunder/tests/test_ops.py -v --datefmt="%Y%m%d-%H:%M:%S.%f" --random-order -n 4 --durations=250\npytest thunder/tests/test_grad.py -v --datefmt="%Y%m%d-%H:%M:%S.%f" --random-order -n 4 --durations=250' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pytest/\/miniconda\/envs\/py310\/bin\/pytest/g' test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash

/miniconda/envs/py310/bin/pytest thunder/tests/ --ignore=thunder/tests/distributed --ignore=thunder/tests/test_ops.py --ignore=thunder/tests/test_grad.py -v --datefmt="%Y%m%d-%H:%M:%S.%f" --random-order -n 4 --durations=250
/miniconda/envs/py310/bin/pytest thunder/tests/distributed/ -v --datefmt="%Y%m%d-%H:%M:%S.%f" --random-order --durations=250
/miniconda/envs/py310/bin/pytest thunder/tests/test_ops.py -v --datefmt="%Y%m%d-%H:%M:%S.%f" --random-order -n 4 --durations=250
/miniconda/envs/py310/bin/pytest thunder/tests/test_grad.py -v --datefmt="%Y%m%d-%H:%M:%S.%f" --random-order -n 4 --durations=250

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

/miniconda/envs/py310/bin/pytest thunder/tests/ --ignore=thunder/tests/distributed --ignore=thunder/tests/test_ops.py --ignore=thunder/tests/test_grad.py -v --datefmt="%Y%m%d-%H:%M:%S.%f" --random-order -n 4 --durations=250
/miniconda/envs/py310/bin/pytest thunder/tests/distributed/ -v --datefmt="%Y%m%d-%H:%M:%S.%f" --random-order --durations=250
/miniconda/envs/py310/bin/pytest thunder/tests/test_ops.py -v --datefmt="%Y%m%d-%H:%M:%S.%f" --random-order -n 4 --durations=250
/miniconda/envs/py310/bin/pytest thunder/tests/test_grad.py -v --datefmt="%Y%m%d-%H:%M:%S.%f" --random-order -n 4 --durations=250

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

/miniconda/envs/py310/bin/pytest thunder/tests/ --ignore=thunder/tests/distributed --ignore=thunder/tests/test_ops.py --ignore=thunder/tests/test_grad.py -v --datefmt="%Y%m%d-%H:%M:%S.%f" --random-order -n 4 --durations=250
/miniconda/envs/py310/bin/pytest thunder/tests/distributed/ -v --datefmt="%Y%m%d-%H:%M:%S.%f" --random-order --durations=250
/miniconda/envs/py310/bin/pytest thunder/tests/test_ops.py -v --datefmt="%Y%m%d-%H:%M:%S.%f" --random-order -n 4 --durations=250
/miniconda/envs/py310/bin/pytest thunder/tests/test_grad.py -v --datefmt="%Y%m%d-%H:%M:%S.%f" --random-order -n 4 --durations=250

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
RUN git clone https://github.com/Lightning-AI/lightning-thunder.git /home/lightning-thunder

WORKDIR /home/lightning-thunder
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Lightning-AI", "lightning_thunder_2262_to_1907")
class LIGHTNING_THUNDER_2262_TO_1907(Instance):
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
        # Regex pattern to match test lines with status and test name
        # Captures status (PASSED, SKIPPED, XFAILED, FAILED) and test name
        pattern = re.compile(r'\[gw\d+\]\x1b\[\d+m \[\s*\d+%\] \x1b\[0m\x1b\[\d+m(PASSED|SKIPPED|XFAILED|FAILED)\x1b\[0m \[.*?\] (thunder/tests/[^ \n]+)')
        matches = pattern.findall(log)
        for status, test_name in matches:
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
            elif status in ['XFAILED', 'FAILED']:
                failed_tests.add(test_name)
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
