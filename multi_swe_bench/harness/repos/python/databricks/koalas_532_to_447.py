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
                """ls
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.7 python3.7-venv
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common && add-apt-repository -y ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.7 python3.7-venv
###ACTION_DELIMITER###
python3.7 -m venv koalas-venv-3.7
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip install -e .[spark]
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip install -r requirements-dev.txt
###ACTION_DELIMITER###
apt-get install -y openjdk-8-jdk && export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nexport JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64\nkoalas-venv-3.7/bin/pytest -v --no-header -rA -p no:cacheprovider .' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip uninstall -y pyspark && koalas-venv-3.7/bin/pip install pyspark==3.0.3
###ACTION_DELIMITER###
koalas-venv-3.7/bin/python -c "from pyspark.sql.types import to_arrow_type; print('Success')"
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip uninstall -y pyspark && koalas-venv-3.7/bin/pip install pyspark==3.1.3
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip uninstall -y pyspark && koalas-venv-3.7/bin/pip install --no-cache-dir pyspark==3.2.0 && koalas-venv-3.7/bin/python -c "from pyspark.sql.types import to_arrow_type; print('Success')"
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip uninstall -y pyspark && koalas-venv-3.7/bin/pip cache purge && koalas-venv-3.7/bin/pip install --no-cache-dir pyspark==3.1.0 && koalas-venv-3.7/bin/python -c "from pyspark.sql.types import to_arrow_type; print('Success')"
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip uninstall -y pyspark && koalas-venv-3.7/bin/pip install --no-cache-dir pyspark==3.0.1 && koalas-venv-3.7/bin/python -c "from pyspark.sql.types import to_arrow_type; print('Success')"
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip uninstall -y pyspark pyarrow pandas && koalas-venv-3.7/bin/pip install --no-cache-dir pyspark==3.0.0 pyarrow==0.17.0 pandas==1.0.5 && koalas-venv-3.7/bin/python -c "from pyspark.sql.types import to_arrow_type; print('Success')"
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip uninstall -y pyspark pandas pyarrow && koalas-venv-3.7/bin/pip install --no-cache-dir pyspark==2.4.8 pandas==0.25.3 pyarrow==0.17.0 && koalas-venv-3.7/bin/python -c "from pyspark.sql.types import to_arrow_type; print('Success')"
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nexport JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64\nkoalas-venv-3.7/bin/pytest -v --no-header -rA -p no:cacheprovider .' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip uninstall -y pandas && koalas-venv-3.7/bin/pip install --no-cache-dir pandas==1.0.5 && bash test_commands.sh
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip uninstall -y pandas && koalas-venv-3.7/bin/pip install --no-cache-dir pandas==1.1.5 && bash test_commands.sh
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip uninstall -y pandas && koalas-venv-3.7/bin/pip install --no-cache-dir pandas==1.2.5 && bash test_commands.sh
###ACTION_DELIMITER###
ls -l koalas-venv-3.7/lib/python3.7/site-packages/pandas/plotting/ && grep '_all_kinds' koalas-venv-3.7/lib/python3.7/site-packages/pandas/plotting/_core.py
###ACTION_DELIMITER###
rm -rf koalas-venv-3.7 && python3.7 -m venv koalas-venv-3.7 && koalas-venv-3.7/bin/pip install -e .[spark] && koalas-venv-3.7/bin/pip install -r requirements-dev.txt && koalas-venv-3.7/bin/pip install --no-cache-dir pyspark==2.4.8 pandas==1.0.5 pyarrow==0.17.0 && bash test_commands.sh
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip uninstall -y matplotlib && koalas-venv-3.7/bin/pip install matplotlib==3.0.0 && bash test_commands.sh
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip uninstall -y pandas && koalas-venv-3.7/bin/pip install --no-cache-dir pandas==1.0.5 && bash test_commands.sh
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip uninstall -y pandas && koalas-venv-3.7/bin/pip install --no-cache-dir pandas==0.25.3 && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf koalas-venv-3.7 && python3.7 -m venv koalas-venv-3.7 && koalas-venv-3.7/bin/pip install -e .[spark] && koalas-venv-3.7/bin/pip install -r requirements-dev.txt && koalas-venv-3.7/bin/pip install --no-cache-dir pyspark==2.4.8 pandas==1.2.5 pyarrow==0.17.0 matplotlib==3.0.0 && bash test_commands.sh
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip uninstall -y pandas && koalas-venv-3.7/bin/pip install --no-cache-dir pandas==0.25.3 && grep '_all_kinds' koalas-venv-3.7/lib/python3.7/site-packages/pandas/plotting/_core.py && bash test_commands.sh
###ACTION_DELIMITER###
koalas-venv-3.7/bin/python -c "from pandas.plotting._core import _all_kinds; print('Success')" && bash test_commands.sh
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip install --force-reinstall pandas==0.25.3 && koalas-venv-3.7/bin/python -c "from pandas.plotting._core import _all_kinds; print('Success')" && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf koalas-venv-3.7 && python3.7 -m venv koalas-venv-3.7 && koalas-venv-3.7/bin/pip install pandas==0.25.3 matplotlib==3.0.0 pyarrow==0.17.0 pyspark==2.4.8 && koalas-venv-3.7/bin/pip install -e .[spark] && koalas-venv-3.7/bin/pip install -r requirements-dev.txt && koalas-venv-3.7/bin/python -c "from pandas.plotting._core import _all_kinds; print('Success')" && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf koalas-venv-3.7 && python3.7 -m venv koalas-venv-3.7 && koalas-venv-3.7/bin/pip install pandas==0.25.3 matplotlib==3.0.0 pyarrow==0.17.0 pyspark==2.4.8 pytz==2022.7.1 && koalas-venv-3.7/bin/pip install -e .[spark] && koalas-venv-3.7/bin/pip install -r requirements-dev.txt && koalas-venv-3.7/bin/python -c "from pandas.plotting._core import _all_kinds; print('Success')" && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf koalas-venv-3.7 && python3.7 -m venv koalas-venv-3.7 && koalas-venv-3.7/bin/pip install pandas==0.23.4 matplotlib==3.0.0 pyarrow==0.10.0 pyspark==2.4.0 pytz==2022.7.1 && koalas-venv-3.7/bin/pip install -e .[spark] && koalas-venv-3.7/bin/pip install -r requirements-dev.txt && koalas-venv-3.7/bin/python -c "from pandas.plotting._core import _all_kinds; print('Success')" && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf koalas-venv-3.7 && python3.7 -m venv koalas-venv-3.7 && koalas-venv-3.7/bin/pip install Cython && koalas-venv-3.7/bin/pip install pandas==0.23.4 matplotlib==3.0.0 pyarrow==0.10.0 pyspark==2.4.0 pytz==2022.7.1 && koalas-venv-3.7/bin/pip install -e .[spark] && koalas-venv-3.7/bin/pip install -r requirements-dev.txt && koalas-venv-3.7/bin/python -c "from pandas.plotting._core import _all_kinds; print('Success')" && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf koalas-venv-3.7 && python3.7 -m venv koalas-venv-3.7 && koalas-venv-3.7/bin/pip install wheel && koalas-venv-3.7/bin/pip install pandas==0.25.3 matplotlib==3.0.0 pyarrow==0.17.0 pyspark==2.4.8 pytz==2022.7.1 && koalas-venv-3.7/bin/pip install -e .[spark] && koalas-venv-3.7/bin/pip install -r requirements-dev.txt && koalas-venv-3.7/bin/python -c "from pandas.plotting._core import _all_kinds; print('Success')" && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libfreetype6-dev libpng-dev libopenblas-dev libgfortran5 && rm -rf koalas-venv-3.7 && python3.7 -m venv koalas-venv-3.7 && koalas-venv-3.7/bin/pip install --upgrade pip && koalas-venv-3.7/bin/pip install wheel && koalas-venv-3.7/bin/pip install pandas==0.25.3 matplotlib==3.0.0 pyarrow==0.17.0 pyspark==2.4.8 pytz==2022.7.1 && koalas-venv-3.7/bin/pip install -e .[spark] && koalas-venv-3.7/bin/pip install -r requirements-dev.txt && koalas-venv-3.7/bin/python -c "import pandas.plotting; from pandas.plotting._core import _all_kinds; print('Success')" && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf koalas-venv-3.7 && python3.7 -m venv koalas-venv-3.7 && koalas-venv-3.7/bin/pip install pandas==0.25.3 matplotlib==3.0.0 pyarrow==0.17.0 && koalas-venv-3.7/bin/python -c "from pandas.plotting._core import _all_kinds; print('Success')"
###ACTION_DELIMITER###
grep '_all_kinds' koalas-venv-3.7/lib/python3.7/site-packages/pandas/plotting/_core.py
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip uninstall -y pandas && koalas-venv-3.7/bin/pip install --no-cache-dir pandas==0.25.3 && koalas-venv-3.7/bin/python -c "import pandas.plotting; from pandas.plotting._core import _all_kinds; print('Success')"
###ACTION_DELIMITER###
ls -l koalas-venv-3.7/lib/python3.7/site-packages/pandas/plotting/ && koalas-venv-3.7/bin/pip uninstall -y pandas && koalas-venv-3.7/bin/pip install --no-cache-dir pandas==0.25.4 && koalas-venv-3.7/bin/python -c "import pandas; print('Imported pandas'); import pandas.plotting; print('Imported pandas.plotting'); from pandas.plotting._core import _all_kinds; print('Success')"
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip uninstall -y pandas && koalas-venv-3.7/bin/pip install --no-cache-dir pandas==0.25.3 && koalas-venv-3.7/bin/python -c "import pandas; print('Imported pandas'); import pandas.plotting; print('Imported pandas.plotting'); from pandas.plotting._core import _all_kinds; print('Success')"
###ACTION_DELIMITER###

###ACTION_DELIMITER###
rm -rf koalas-venv-3.7 && python3.7 -m venv koalas-venv-3.7 && koalas-venv-3.7/bin/pip install pandas==1.3.5 matplotlib==3.5.3 pyarrow==0.17.0 pyspark==3.0.0 && koalas-venv-3.7/bin/python -c "from pandas.plotting._core import _all_kinds; print('Success')"
###ACTION_DELIMITER###
rm -rf koalas-venv-3.7 && python3.7 -m venv koalas-venv-3.7 && koalas-venv-3.7/bin/pip install pandas==0.23.4 matplotlib==3.0.0 pyarrow==0.15.0 pyspark==2.4.0 && koalas-venv-3.7/bin/python -c "from pandas.plotting._core import _all_kinds; print('Success')"
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nexport JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64\nkoalas-venv-3.7/bin/pytest -v --no-header -rA -p no:cacheprovider .' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
koalas-venv-3.7/bin/pip install -r requirements-dev.txt && bash test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
koalas-venv-3.7/bin/pytest -v --no-header -rA -p no:cacheprovider .

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
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
koalas-venv-3.7/bin/pytest -v --no-header -rA -p no:cacheprovider .

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
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
koalas-venv-3.7/bin/pytest -v --no-header -rA -p no:cacheprovider .

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
RUN git clone https://github.com/databricks/koalas.git /home/koalas

WORKDIR /home/koalas
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("databricks", "koalas_532_to_447")
class KOALAS_532_TO_447(Instance):
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
        # Parse test statuses from log lines
        for line in log.split('\n'):
            # Match lines with test status (FAILED, PASSED, SKIPPED)
            match = re.search(r'^(?:\[\s*\d+\s*\]\s*)?(FAILED|PASSED|SKIPPED)\s+([^-]+?)\s*(?:-|$)', line)
            if match:
                status = match.group(1)
                test_name = match.group(2).strip()
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
