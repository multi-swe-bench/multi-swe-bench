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
        repo_name = self.pr.repo
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
./setup.sh --install
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository -y ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.7 python3.7-dev python3.7-venv
###ACTION_DELIMITER###
./setup.sh --install
###ACTION_DELIMITER###
apt-get install -y python3.7-pip
###ACTION_DELIMITER###
wget https://bootstrap.pypa.io/get-pip.py && python3.7 get-pip.py
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget https://bootstrap.pypa.io/get-pip.py && python3.7 get-pip.py
###ACTION_DELIMITER###
wget https://bootstrap.pypa.io/pip/3.7/get-pip.py && python3.7 get-pip.py
###ACTION_DELIMITER###
wget https://bootstrap.pypa.io/pip/3.7/get-pip.py -O get-pip.py && python3.7 get-pip.py
###ACTION_DELIMITER###
./setup.sh --install
###ACTION_DELIMITER###
apt-get install -y build-essential libssl-dev libffi-dev
###ACTION_DELIMITER###
wget https://downloads.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz && tar xzf ta-lib-0.4.0-src.tar.gz && cd ta-lib && ./configure --prefix=/usr/local && make && make install && cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
###ACTION_DELIMITER###
python3.7 -m venv .env && . .env/bin/activate && pip install --upgrade pip && pip install -r requirements.txt -r requirements-common.txt -r requirements-dev.txt
###ACTION_DELIMITER###
sed -i 's/ccxt==1.19.86/ccxt==1.19.1/' requirements-common.txt && . .env/bin/activate && pip install -r requirements.txt -r requirements-common.txt -r requirements-dev.txt
###ACTION_DELIMITER###
. .env/bin/activate && pip install numpy && pip install -r requirements.txt -r requirements-common.txt -r requirements-dev.txt
###ACTION_DELIMITER###
. .env/bin/activate && pip install numpy && pip install TA-Lib==0.4.17 && pip install -r requirements.txt -r requirements-common.txt -r requirements-dev.txt
###ACTION_DELIMITER###
. .env/bin/activate && pip install --no-build-isolation TA-Lib==0.4.17
###ACTION_DELIMITER###
. .env/bin/activate && pip install wheel && pip install --no-build-isolation TA-Lib==0.4.17
###ACTION_DELIMITER###
. .env/bin/activate && pip install -r requirements.txt -r requirements-common.txt -r requirements-dev.txt
###ACTION_DELIMITER###
echo -e '#!/bin/bash
. .env/bin/activate
pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
grep -r 'numpy' requirements*.txt && sed -i 's/numpy==1.17.4/numpy==1.21.6/' requirements*.txt && . .env/bin/activate && pip install -r requirements.txt -r requirements-common.txt -r requirements-dev.txt && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/--no-header //' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/-p no:cacheprovider/-p no:cacheprovider -p no:random-order/' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && pip uninstall -y pytest-random-order && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/--tb=no/--tb=short/' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH && pip install markupsafe==2.0.1 && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && pip install itsdangerous==1.1.0 && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && pip install werkzeug==1.0.1 && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && pip install --no-build-isolation TA-Lib==0.4.17 && pip install matplotlib && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && pip install numpy==1.19.5 && sed -i '1a export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && pip uninstall -y py_find_1st && pip install --no-binary :all: py_find_1st==1.1.4 && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && pip uninstall -y numpy py_find_1st && pip install --no-cache-dir numpy==1.19.5 && pip install --no-cache-dir --no-binary :all: py_find_1st==1.1.4 && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && pip uninstall -y TA-Lib py_find_1st && pip install --no-binary :all: TA-Lib==0.4.17 py_find_1st==1.1.4 && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && pip uninstall -y numpy py_find_1st TA-Lib && pip install numpy==1.21.6 && pip install --no-binary :all: py_find_1st==1.1.4 TA-Lib==0.4.17 && bash test_commands.sh
###ACTION_DELIMITER###
ldconfig && sed -i '1a export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf .env && python3.7 -m venv .env && . .env/bin/activate && pip install --upgrade pip && pip install numpy==1.17.4 && pip install --no-binary :all: py_find_1st==1.1.4 TA-Lib==0.4.17 && pip install -r requirements.txt -r requirements-common.txt -r requirements-dev.txt && sed -i '1a export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && pip uninstall -y pytest-random-order && sed -i 's/-p no:random-order//' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && pip uninstall -y markupsafe && pip install markupsafe==1.1.1 && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && pip uninstall -y itsdangerous && pip install itsdangerous==1.1.0 && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && pip uninstall -y werkzeug && pip install werkzeug==1.0.1 && bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pytest -v/pytest -v --full-trace/' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libgfortran5 && . .env/bin/activate && pip install matplotlib==3.5.3 && sed -i '1a export MPLBACKEND=Agg' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf .env && python3.7 -m venv .env && . .env/bin/activate && pip install --upgrade pip && pip install numpy==1.21.6 && pip install --no-binary :all: py_find_1st==1.1.4 TA-Lib==0.4.17 && pip install -r requirements.txt -r requirements-common.txt -r requirements-dev.txt && apt-get install -y libgfortran5 && sed -i '1a export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH\nexport MPLBACKEND=Agg' test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && pip uninstall -y pytest-random-order && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && pip uninstall -y markupsafe && pip install markupsafe==1.1.1 && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && pip uninstall -y itsdangerous && pip install itsdangerous==1.1.0 && bash test_commands.sh
###ACTION_DELIMITER###
. .env/bin/activate && pip uninstall -y werkzeug && pip install werkzeug==1.0.1 && bash test_commands.sh
###ACTION_DELIMITER###
""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export MPLBACKEND=Agg
export MPLBACKEND=Agg
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
. .env/bin/activate
pytest -v --full-trace -rA --tb=short -p no:cacheprovider 

""".replace("[[REPO_NAME]]", repo_name),
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
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export MPLBACKEND=Agg
export MPLBACKEND=Agg
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
. .env/bin/activate
pytest -v --full-trace -rA --tb=short -p no:cacheprovider 

""".replace("[[REPO_NAME]]", repo_name),
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
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export MPLBACKEND=Agg
export MPLBACKEND=Agg
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
. .env/bin/activate
pytest -v --full-trace -rA --tb=short -p no:cacheprovider 

""".replace("[[REPO_NAME]]", repo_name),
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
RUN git clone https://github.com/freqtrade/freqtrade.git /home/freqtrade

WORKDIR /home/freqtrade
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("freqtrade", "freqtrade_2576_to_2479")
class FREQTRADE_2576_TO_2479(Instance):
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

        return "bash /home/run.sh"

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

        # Implement the log parsing logic here
        pattern1 = re.compile(
            r"(tests/[^:]+::[^ ]+)\s+(PASSED|FAILED|SKIPPED)"
        )  # test name followed by status
        pattern2 = re.compile(
            r"(PASSED|FAILED|SKIPPED)\s+(tests/[^:]+::[^ -]+)"
        )  # status followed by test name
        for line in log.split("\n"):
            match = pattern1.search(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
            else:
                match = pattern2.search(line)
                if match:
                    status = match.group(1)
                    test_name = match.group(2)
                else:
                    continue
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status == "FAILED":
                failed_tests.add(test_name)
            elif status == "SKIPPED":
                skipped_tests.add(test_name)
        parsed_results = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
        }

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
