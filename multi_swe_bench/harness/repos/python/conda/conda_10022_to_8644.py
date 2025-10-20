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
        repo_name= self.pr.repo
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
pip install -e .
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###

###ACTION_DELIMITER###

###ACTION_DELIMITER###
echo -e "#!/bin/bash\n\nPYTHONHASHSEED=\$(python -c 'import random as r; print(r.randint(0,4294967296))')\nPYTHON_MAJOR_VERSION=\$(python -c 'import sys; print(sys.version_info[0])')\nTEST_PLATFORM=\$(python -c 'import sys; print(\"win\" if sys.platform.startswith(\"win\") else \"unix\")')\nSYS_PREFIX=\$(python -c 'import sys; print(sys.prefix)')\n\npy.test --basetemp=\$SYS_PREFIX/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m \"not integration and not installed\"\npy.test --basetemp=\$SYS_PREFIX/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m \"integration and not installed\"\npy.test --basetemp=\$SYS_PREFIX/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m \"installed\" --shell=bash --shell=zsh" > /home/conda/test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash

PYTHONHASHSEED=$(python -c "import random as r; print(r.randint(0,4294967296))")
PYTHON_MAJOR_VERSION=$(python -c "import sys; print(sys.version_info[0])")
TEST_PLATFORM=$(python -c "import sys; print(\"win\" if sys.platform.startswith(\"win\") else \"unix\")")
SYS_PREFIX=$(python -c "import sys; print(sys.prefix)")

py.test --basetemp=$SYS_PREFIX/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m "not integration and not installed"
py.test --basetemp=$SYS_PREFIX/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m "integration and not installed"
py.test --basetemp=$SYS_PREFIX/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m "installed" --shell=bash --shell=zsh' > /home/conda/test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install pytest-cov
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
eval "$(python -m conda init --dev bash)"
###ACTION_DELIMITER###
make unit
###ACTION_DELIMITER###
conda create -n test_env -y python=3.9 && conda activate test_env && pip install -e . && make unit
###ACTION_DELIMITER###
pip install tqdm
###ACTION_DELIMITER###
conda create -n test_env -y python=3.9
###ACTION_DELIMITER###
pip install conda-package-handling
###ACTION_DELIMITER###
conda create -n test_env -y python=3.9
###ACTION_DELIMITER###
conda activate test_env && pip install -e . && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nmake unit' > test_commands.sh && chmod +x test_commands.sh && conda activate test_env && pip install pytest pytest-cov tqdm conda-package-handling && bash test_commands.sh
###ACTION_DELIMITER###
conda activate base && pip install pytest pytest-cov tqdm conda-package-handling && bash test_commands.sh
###ACTION_DELIMITER###
conda create -n base -y python=3.9 && conda activate base && pip install -e . && pip install pytest pytest-cov tqdm conda-package-handling && bash test_commands.sh
###ACTION_DELIMITER###
conda init bash && source ~/.bashrc && conda activate base && bash test_commands.sh
###ACTION_DELIMITER###
conda install -y menuinst && /usr/local/bin/python -m pytest --basetemp=/usr/local/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m 'not integration and not installed'
###ACTION_DELIMITER###
pip install mock responses && /usr/local/bin/python -m pytest --basetemp=/usr/local/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m 'not integration and not installed'
###ACTION_DELIMITER###
pip install pytest-skiplist && conda activate base && export CONDA_PREFIX=/usr/local && /usr/local/bin/python -m pytest --basetemp=/usr/local/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m 'not integration and not installed'
###ACTION_DELIMITER###
pip install pytest==6.2.5 && pip install mock responses && conda activate base && export CONDA_PREFIX=/usr/local && /usr/local/bin/python -m pytest --basetemp=/usr/local/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m 'not integration and not installed'
###ACTION_DELIMITER###
pip install mock responses pytest-cov && conda activate base && export CONDA_PREFIX=/usr/local && /usr/local/bin/python -m pytest --basetemp=/usr/local/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m 'not integration and not installed'
###ACTION_DELIMITER###
conda activate base && export CONDA_PREFIX=/usr/local && /usr/local/bin/python -m pytest --basetemp=/usr/local/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m 'not integration and not installed'
###ACTION_DELIMITER###
pip install ruamel.yaml==0.16.12 && conda activate base && export CONDA_PREFIX=/usr/local && /usr/local/bin/python -m pytest --basetemp=/usr/local/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m 'not integration and not installed'
###ACTION_DELIMITER###
conda init bash && source ~/.bashrc && conda activate base && export CONDA_PREFIX=/usr/local && chmod -R 777 /usr/local/../conda.tmp && /usr/local/bin/python -m pytest --basetemp=/usr/local/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m 'not integration and not installed'
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nconda activate base\nexport CONDA_PREFIX=/usr/local\n/usr/local/bin/python -m pytest --basetemp=/usr/local/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m "not integration and not installed"' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
conda activate base
export CONDA_PREFIX=/usr/local
/usr/local/bin/python -m pytest --basetemp=/usr/local/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m "not integration and not installed"

""".replace("[[REPO_NAME]]", repo_name)
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
if ! git -C /home/[[REPO_NAME]] apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
#!/bin/bash
conda activate base
export CONDA_PREFIX=/usr/local
/usr/local/bin/python -m pytest --basetemp=/usr/local/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m "not integration and not installed"

""".replace("[[REPO_NAME]]", repo_name)
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
if ! git -C /home/[[REPO_NAME]] apply --whitespace=nowarn  /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
#!/bin/bash
conda activate base
export CONDA_PREFIX=/usr/local
/usr/local/bin/python -m pytest --basetemp=/usr/local/../conda.tmp -v --cov-report xml --cov-report term-missing --cov-append --cov conda -m "not integration and not installed"

""".replace("[[REPO_NAME]]", repo_name)
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
RUN git clone https://github.com/conda/conda.git /home/conda

WORKDIR /home/conda
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("conda", "conda_10022_to_8644")
class CONDA_10022_TO_8644(Instance):
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
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        import json
        # Parse passed tests
        passed_pattern = re.compile(r'(tests/.*?)\s+PASSED')
        passed_tests.update(passed_pattern.findall(log))
        # Parse failed tests from progress lines
        failed_progress_pattern = re.compile(r'\[\s*\d+\s*\]\s+(tests/.*?)\s+FAILED')
        failed_tests.update(failed_progress_pattern.findall(log))
        # Parse failed tests from summary lines
        failed_summary_pattern = re.compile(r'FAILED\s+(tests/.*?)\s+-')
        failed_tests.update(failed_summary_pattern.findall(log))
        # Parse error tests (considered as failed)
        error_pattern = re.compile(r'\[\s*\d+\s*\]\s+ERROR\s+(tests/.*)')
        failed_tests.update(error_pattern.findall(log))
        # Parse skipped tests from summary lines
        skipped_pattern = re.compile(r'\[\s*\d+\s*\]\s+SKIPPED\s+(tests/.*?)\s+-')
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
