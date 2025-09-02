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
                """apt-get update && apt-get install -y python3 python3-pip python3-venv
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
venv/bin/pip install -e . pytest coverage
###ACTION_DELIMITER###
echo 'venv/bin/python -m coverage run --source thunder -m pytest thunder tests -v' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install pytest-benchmark
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls -l
###ACTION_DELIMITER###
ls -l thunder
###ACTION_DELIMITER###
echo 'venv/bin/python -m coverage run --source thunder -m pytest thunder/tests -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls -l requirements
###ACTION_DELIMITER###
venv/bin/pip install -r requirements/test.txt
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cat README.md
###ACTION_DELIMITER###
echo 'THUNDER_EXECUTOR=torch.compile venv/bin/python -m coverage run --source thunder -m pytest thunder/tests -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install nvidia-transformer-engine nvfuser && echo 'THUNDER_EXECUTOR=nvfuser venv/bin/python -m coverage run --source thunder -m pytest thunder/tests -v' > test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install transformer-engine nvfuser && echo 'THUNDER_EXECUTOR=torch.compile venv/bin/python -m coverage run --source thunder -m pytest thunder/tests -v' > test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget && wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-ubuntu2404.pin && mv cuda-ubuntu2404.pin /etc/apt/preferences.d/cuda-repository-pin-600 && wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda-repo-ubuntu2404-12-1-local_12.1.0-530.30.02-1_amd64.deb && dpkg -i cuda-repo-ubuntu2404-12-1-local_12.1.0-530.30.02-1_amd64.deb && cp /var/cuda-repo-ubuntu2404-12-1-local/cuda-*-keyring.gpg /usr/share/keyrings/ && apt-get update && apt-get -y install cuda-runtime-12-1
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget gnupg2 && wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-ubuntu2404.pin && mv cuda-ubuntu2404.pin /etc/apt/preferences.d/cuda-repository-pin-600 && wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb && dpkg -i cuda-keyring_1.1-1_all.deb && apt-get update && apt-get -y install cuda-runtime-12-6 libcudnn8
###ACTION_DELIMITER###
cat .github/workflows/ci-testing.yml
###ACTION_DELIMITER###
echo 'venv/bin/python -m coverage run --source thunder -m pytest thunder/tests/ --ignore=thunder/tests/distributed --ignore=thunder/tests/test_ops.py --ignore=thunder/tests/test_grad.py -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install -r requirements/base.txt -r requirements/test.txt && venv/bin/pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cpu && echo 'THUNDER_EXECUTOR=torch.compile venv/bin/python -m coverage run --source thunder -m pytest thunder/tests/ --ignore=thunder/tests/distributed --ignore=thunder/tests/test_ops.py --ignore=thunder/tests/test_grad.py -v' > test_commands.sh
###ACTION_DELIMITER###
echo 'THUNDER_EXECUTOR=torch.compile venv/bin/python -m coverage run --source thunder -m pytest thunder/tests/ --ignore=thunder/tests/distributed --ignore=thunder/tests/test_ops.py --ignore=thunder/tests/test_grad.py -v' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cpu && echo 'export THUNDER_EXECUTOR=torch.compile
venv/bin/python -m coverage run --source thunder -m pytest thunder/tests/ --ignore=thunder/tests/distributed --ignore=thunder/tests/test_ops.py --ignore=thunder/tests/test_grad.py -v' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip uninstall -y torch && venv/bin/pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cu121 && echo 'THUNDER_EXECUTOR=torch.compile venv/bin/python -m coverage run --source thunder -m pytest thunder/tests/ --ignore=thunder/tests/distributed --ignore=thunder/tests/test_ops.py --ignore=thunder/tests/test_grad.py -v' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cu121
###ACTION_DELIMITER###
echo 'venv/bin/python -c "import thunder; thunder.set_executor(\"torch.compile\")" && venv/bin/python -m coverage run --source thunder -m pytest thunder/tests/ --ignore=thunder/tests/distributed --ignore=thunder/tests/test_ops.py --ignore=thunder/tests/test_grad.py -v' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
export THUNDER_EXECUTOR=torch.compile
venv/bin/python -m coverage run --source thunder -m pytest thunder/tests/ --ignore=thunder/tests/distributed --ignore=thunder/tests/test_ops.py --ignore=thunder/tests/test_grad.py -v' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
export THUNDER_EXECUTOR=torch.compile
venv/bin/python -m coverage run --source thunder -m pytest thunder/tests/ --ignore=thunder/tests/distributed --ignore=thunder/tests/test_ops.py --ignore=thunder/tests/test_grad.py -v --deselect thunder/tests/test_auto_register_torchops.py::test_torch_ops_trace[cpu-inference-nn.functional.embedding_bag]' > test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
export THUNDER_EXECUTOR=torch.compile
venv/bin/python -m coverage run --source thunder -m pytest thunder/tests/ --ignore=thunder/tests/distributed --ignore=thunder/tests/test_ops.py --ignore=thunder/tests/test_grad.py -v --deselect thunder/tests/test_auto_register_torchops.py::test_torch_ops_trace[cpu-inference-nn.functional.embedding_bag]

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
export THUNDER_EXECUTOR=torch.compile
venv/bin/python -m coverage run --source thunder -m pytest thunder/tests/ --ignore=thunder/tests/distributed --ignore=thunder/tests/test_ops.py --ignore=thunder/tests/test_grad.py -v --deselect thunder/tests/test_auto_register_torchops.py::test_torch_ops_trace[cpu-inference-nn.functional.embedding_bag]

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
export THUNDER_EXECUTOR=torch.compile
venv/bin/python -m coverage run --source thunder -m pytest thunder/tests/ --ignore=thunder/tests/distributed --ignore=thunder/tests/test_ops.py --ignore=thunder/tests/test_grad.py -v --deselect thunder/tests/test_auto_register_torchops.py::test_torch_ops_trace[cpu-inference-nn.functional.embedding_bag]

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
RUN git clone https://github.com/Lightning-AI/lightning-thunder.git /home/lightning-thunder

WORKDIR /home/lightning-thunder
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)



@Instance.register("Lightning-AI", "lightning_thunder_1003_to_829")
class LIGHTNING_THUNDER_1003_TO_829(Instance):
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
        lines = log.split('\n')
        for line in lines:
            # Check for PASSED tests
            if '\x1b[32mPASSED\x1b[0m' in line:
                parts = line.split('] ', 1)
                if len(parts) >= 2:
                    test_part = parts[1]
                    test_name = test_part.split(' \x1b[', 1)[0]
                    passed_tests.add(test_name)
            # Check for SKIPPED tests
            elif '\x1b[33mSKIPPED\x1b[0m' in line:
                parts = line.split('] ', 1)
                if len(parts) >= 2:
                    test_part = parts[1]
                    test_name = test_part.split(' \x1b[', 1)[0]
                    skipped_tests.add(test_name)
            # Check for FAILED tests
            elif '\x1b[31mFAILED\x1b[0m' in line:
                parts = line.split('\x1b[31mFAILED\x1b[0m ', 1)
                if len(parts) >= 2:
                    test_part = parts[1]
                    test_name_part = test_part.split(' - ', 1)[0]
                    test_name = re.sub(r'\x1b\[\d+m', '', test_name_part)
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
