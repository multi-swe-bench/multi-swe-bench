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
echo -e "y\nn\nn\nn" | ./setup.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.8 python3.8-venv python3.8-dev
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.10 python3.10-venv python3.10-dev
###ACTION_DELIMITER###
apt-get install -y python3-venv python3-dev
###ACTION_DELIMITER###
sed -i 's/for v in 10 9 8/for v in 12 10 9 8/' setup.sh
###ACTION_DELIMITER###
echo -e "y\nn\nn\nn" | ./setup.sh
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
echo -e "y\nn\nn\nn" | ./setup.sh
###ACTION_DELIMITER###
echo -e "y\nn\nn\nn" | ./setup.sh -i
###ACTION_DELIMITER###
apt-get install -y build-essential
###ACTION_DELIMITER###
python3 -m venv .env && source .env/bin/activate && echo -e "y\nn\nn\nn" | ./setup.sh -i
###ACTION_DELIMITER###
echo -e "y\nn\nn\nn" | ./setup.sh -i
###ACTION_DELIMITER###
deactivate && echo -e "y\nn\nn\nn" | ./setup.sh -i
###ACTION_DELIMITER###
apt-get install -y autotools-dev
###ACTION_DELIMITER###
apt-get install -y python3-pip libta-lib-dev
###ACTION_DELIMITER###
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && tar -xzf ta-lib-0.4.0-src.tar.gz && cd ta-lib && ./configure --prefix=/usr && make && make install && cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && tar -xzf ta-lib-0.4.0-src.tar.gz && cd ta-lib && ./configure --prefix=/usr && make && make install && cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
###ACTION_DELIMITER###
python3 -m venv .env && source .env/bin/activate && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python get-pip.py && rm get-pip.py && echo -e "y\nn\nn\nn" | ./setup.sh -i
###ACTION_DELIMITER###
deactivate && echo -e "y\nn\nn\nn" | ./setup.sh -i
###ACTION_DELIMITER###
sed -i '22,26 s/^/#/' setup.sh && python3 -m venv .env && source .env/bin/activate && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python get-pip.py && rm get-pip.py && echo -e "y\nn\nn\nn" | ./setup.sh -i
###ACTION_DELIMITER###
sed -i -e 's/sudo //g' -e '/ta-lib/d' setup.sh && source .env/bin/activate && echo -e "y\nn\nn\nn" | ./setup.sh -i
###ACTION_DELIMITER###
ls -la requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && pip install setuptools
###ACTION_DELIMITER###
source .env/bin/activate && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get install -y python3.10 python3.10-venv && python3.10 -m venv .env && source .env/bin/activate && pip install setuptools && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get install -y software-properties-common && add-apt-repository -y ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.9 python3.9-venv && python3.9 -m venv .env && source .env/bin/activate && pip install --upgrade setuptools && pip install -r requirements-dev.txt
###ACTION_DELIMITER###

###ACTION_DELIMITER###
apt-get update --fix-missing
###ACTION_DELIMITER###
apt-get install -y software-properties-common && add-apt-repository -y ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.9 python3.9-venv && python3.9 -m venv .env && source .env/bin/activate && pip install --upgrade setuptools && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && pip install --upgrade pip && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && pip install git+https://github.com/ccxt/ccxt.git@1.95.30
###ACTION_DELIMITER###
source .env/bin/activate && pip install git+https://github.com/ccxt/ccxt.git@v1.95.30
###ACTION_DELIMITER###
sed -i 's/ccxt==1.95.30/ccxt==4.1.80/' requirements.txt && source .env/bin/activate && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get install -y python3.9-dev && source .env/bin/activate && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
source .env/bin/activate && pip install ta-lib --global-option=build_ext --global-option="-I/usr/local/include" --global-option="-L/usr/local/lib"
###ACTION_DELIMITER###
apt-get install -y cmake && source .env/bin/activate && pip install ta-lib --config-settings=build_ext="-I/usr/local/include;-L/usr/local/lib"
###ACTION_DELIMITER###
source .env/bin/activate && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
sed -i 's/TA-Lib==0.4.25/ta-lib==0.6.6/' requirements.txt && source .env/bin/activate && pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo -e "#!/bin/bash\nsource .env/bin/activate\npytest --verbose --no-header -rA --tb=no -p no:cacheprovider" > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
source .env/bin/activate
pytest --verbose --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
./test_commands.sh
###ACTION_DELIMITER###
sed -i 's/pytest --verbose/pytest -p no:random_order --verbose/' test_commands.sh && ./test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
source .env/bin/activate
pytest -p no:random_order --verbose --no-header -rA --tb=no -p no:cacheprovider

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
source .env/bin/activate
pytest -p no:random_order --verbose --no-header -rA --tb=no -p no:cacheprovider

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
source .env/bin/activate
pytest -p no:random_order --verbose --no-header -rA --tb=no -p no:cacheprovider

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


@Instance.register("freqtrade", "freqtrade_7571_to_7506")
class FREQTRADE_7571_TO_7506(Instance):
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

        # Regex pattern to match test cases with PASSED, FAILED, or SKIPPED status
        pattern = r"(PASSED|FAILED|SKIPPED)\s+(tests/.*?\.py::test_\w+(?:\[.*?\])?)\b|(tests/.*?\.py::test_\w+(?:\[.*?\])?)\s+(PASSED|FAILED|SKIPPED)\b"
        for match in re.finditer(pattern, log):
            status1, test1, test2, status2 = match.groups()
            if status1 and test1:
                status = status1
                test_name = test1
            else:
                status = status2
                test_name = test2
            # Clean up the test name (remove any trailing whitespace or characters)
            test_name = test_name.strip()
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
