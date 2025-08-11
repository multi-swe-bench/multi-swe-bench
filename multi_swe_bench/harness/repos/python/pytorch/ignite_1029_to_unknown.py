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
        return "python:3.9.18-slim-bullseye"
    
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
ls -a
###ACTION_DELIMITER###
ls .github
###ACTION_DELIMITER###
ls .github/workflows
###ACTION_DELIMITER###
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
py.test --cov ignite --cov-report term-missing -vvv tests/
###ACTION_DELIMITER###

###ACTION_DELIMITER###
echo -e '#!/bin/bash\nCUDA_VISIBLE_DEVICES="" py.test --tx 4*popen//python=python3.9 --cov ignite --cov-report term-missing -vvv tests/\nexport WORLD_SIZE=2\npy.test --cov ignite --cov-append --cov-report term-missing --dist=each --tx $WORLD_SIZE*popen//python=python3.9 tests -m distributed -vvv' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
pip install 'numpy<1.20'
###ACTION_DELIMITER###
pip install numpy==1.23.5
###ACTION_DELIMITER###
echo -e '#!/bin/bash\npy.test -n auto --verbose tests/\nexport WORLD_SIZE=2\npy.test -n $WORLD_SIZE --verbose tests -m distributed' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nset -e\npy.test -n 4 --verbose tests/\nexport WORLD_SIZE=2\npy.test -n $WORLD_SIZE --verbose tests -m distributed' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nset -e\nCUDA_VISIBLE_DEVICES="" py.test --tx 4*popen//python=python3.9 -vvv tests/\nexport WORLD_SIZE=2\npy.test --dist=each --tx $WORLD_SIZE*popen//python=python3.9 tests -m distributed -vvv' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nset -e\npython -c "from visdom.server import download_scripts; download_scripts()"\nCUDA_VISIBLE_DEVICES="" py.test -n 4 -vvv tests/\nexport WORLD_SIZE=2\npy.test -n $WORLD_SIZE --dist=each -vvv tests -m distributed' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nset -e\npython -c "from visdom.server import download_scripts; download_scripts()" || true\nCUDA_VISIBLE_DEVICES="" py.test -n 2 -vvv tests/\nexport WORLD_SIZE=2\npy.test -n $WORLD_SIZE --dist=each -vvv tests -m distributed' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\npython -c "from visdom.server import download_scripts; download_scripts()" || true\nCUDA_VISIBLE_DEVICES="" py.test -n 2 -vvv --tb=short tests/\nexport WORLD_SIZE=2\npy.test -n $WORLD_SIZE --dist=each -vvv --tb=short tests -m distributed' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\npython -c "from visdom.server import download_scripts; download_scripts()" || true\nCUDA_VISIBLE_DEVICES="" py.test -n 1 -vvv --tb=short tests/\nexport WORLD_SIZE=2\npy.test -n 1 --dist=each -vvv --tb=short tests -m distributed' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\npython -c "from visdom.server import download_scripts; download_scripts()" || true\nCUDA_VISIBLE_DEVICES="" py.test -vvv --tb=short tests/\nexport WORLD_SIZE=2\npy.test --dist=each -vvv --tb=short tests -m distributed' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\npython -c "from visdom.server import download_scripts; download_scripts()" || true\nCUDA_VISIBLE_DEVICES="" py.test -vvv --tb=short -k "not visdom" tests/\nexport WORLD_SIZE=2\npy.test --dist=each -vvv --tb=short -k "not visdom" tests -m distributed' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\npython -c "from visdom.server import download_scripts; download_scripts()" || true\nCUDA_VISIBLE_DEVICES="" pytest --no-header -rA --tb=line -p no:cacheprovider -vvv -k "not visdom" tests/\nexport WORLD_SIZE=2\npytest --no-header -rA --tb=line -p no:cacheprovider --dist=each -vvv -k "not visdom" tests -m distributed' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nCUDA_VISIBLE_DEVICES="" pytest --no-header -rA --tb=no -p no:cacheprovider -n 2 -vvv -k "not visdom" tests/\nexport WORLD_SIZE=2\npytest --no-header -rA --tb=no -p no:cacheprovider --dist=each -n $WORLD_SIZE -vvv -k "not visdom" tests -m distributed' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgomp1 && echo -e '#!/bin/bash\nCUDA_VISIBLE_DEVICES="" pytest -vvv --tb=line -p no:cacheprovider -k "not visdom" tests/\nexport WORLD_SIZE=2\npytest -vvv --tb=line -p no:cacheprovider --dist=each -k "not visdom" tests -m distributed' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
CUDA_VISIBLE_DEVICES="" pytest -vvv --tb=line -p no:cacheprovider -k "not visdom" tests/
export WORLD_SIZE=2
pytest -vvv --tb=line -p no:cacheprovider --dist=each -k "not visdom" tests -m distributed

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
CUDA_VISIBLE_DEVICES="" pytest -vvv --tb=line -p no:cacheprovider -k "not visdom" tests/
export WORLD_SIZE=2
pytest -vvv --tb=line -p no:cacheprovider --dist=each -k "not visdom" tests -m distributed

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
CUDA_VISIBLE_DEVICES="" pytest -vvv --tb=line -p no:cacheprovider -k "not visdom" tests/
export WORLD_SIZE=2
pytest -vvv --tb=line -p no:cacheprovider --dist=each -k "not visdom" tests -m distributed

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
FROM python:3.9.18-slim-bullseye

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
RUN git clone https://github.com/pytorch/ignite.git /home/ignite

WORKDIR /home/ignite
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pytorch", "ignite_1029_to_unknown")
class IGNITE_1029_TO_UNKNOWN(Instance):
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
        # Regex patterns to match test lines and error lines
        test_pattern = re.compile(r'(tests/.+?\.py::test_[\w-]+)\s+(PASSED|FAILED|SKIPPED)')
        error_pattern = re.compile(r'ERROR\s+(tests/.+?\.py::test_[\w-]+)\s+-')
        # Iterate over each line in the log
        for line in log.split('\n'):
            line = line.strip()
            # Check for test lines (PASSED/FAILED/SKIPPED)
            test_match = test_pattern.search(line)
            if test_match:
                test_name = test_match.group(1)
                status = test_match.group(2)
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
                elif status == 'SKIPPED':
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
