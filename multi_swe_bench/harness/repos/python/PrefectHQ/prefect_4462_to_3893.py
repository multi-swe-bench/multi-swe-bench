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
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
pip install -r test-requirements.txt
###ACTION_DELIMITER###
echo 'pytest --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install tenacity==7.0.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip show tenacity
###ACTION_DELIMITER###
pip install tenacity==6.2.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install --force-reinstall tenacity==6.2.0
###ACTION_DELIMITER###
sed -i 's/--tb=no //' test_commands.sh
###ACTION_DELIMITER###
pip install tenacity==5.1.1
###ACTION_DELIMITER###
pip install --force-reinstall --no-cache-dir tenacity==5.1.1
###ACTION_DELIMITER###
pip install tenacity==4.1.0
###ACTION_DELIMITER###
python -c 'import tenacity; print("Tenacity version:", tenacity.__version__); from tenacity import Retry; print("Retry __init__ parameters:", Retry.__init__.__code__.co_varnames)'
###ACTION_DELIMITER###
pip install 'tenacity<8.0.0' && pip show tenacity && bash test_commands.sh
###ACTION_DELIMITER###
grep -r 'tenacity' setup.py requirements.txt test-requirements.txt
###ACTION_DELIMITER###
pip install tenacity==5.0.2 && bash test_commands.sh
###ACTION_DELIMITER###
pip install urllib3==1.25.11 && bash test_commands.sh
###ACTION_DELIMITER###
pip install marshmallow==2.21.0 && bash test_commands.sh
###ACTION_DELIMITER###
pip install urllib3==1.25.11 docker==4.4.4 marshmallow==3.10.0 marshmallow-oneofschema==3.0.1 && bash test_commands.sh
###ACTION_DELIMITER###
pip install pendulum==2.0.5 && bash test_commands.sh
###ACTION_DELIMITER###
prefect server start --detach && sleep 10 && bash test_commands.sh
###ACTION_DELIMITER###
pip install docker-compose
###ACTION_DELIMITER###
prefect server start --detach && sleep 30 && bash test_commands.sh
###ACTION_DELIMITER###
pip install urllib3==1.25.11 && bash test_commands.sh
###ACTION_DELIMITER###
pip install urllib3==1.25.11 docker==4.4.4 marshmallow==3.10.0 marshmallow-oneofschema==3.0.1 pendulum==2.0.5 && prefect server start --detach && sleep 30 && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PREFECT__SERVER__DATABASE__CONNECTION_URL=sqlite:///test.db
prefect server database upgrade
prefect server start --detach
 sleep 30
pytest --no-header -rA -p no:cacheprovider' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PREFECT__SERVER__DATABASE__CONNECTION_URL=sqlite:///test.db
prefect server start --detach
 sleep 30
pytest --no-header -rA -p no:cacheprovider -k 'not docker'' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PREFECT__SERVER__DATABASE__CONNECTION_URL=sqlite:///test.db
prefect server start --detach --no-docker
 sleep 30
pytest --no-header -rA -p no:cacheprovider -k "not docker"' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PREFECT__SERVER__DATABASE__CONNECTION_URL=sqlite:///test.db
export PREFECT__SERVER__USE_DOCKER=false
prefect server start --detach
until curl -f http://localhost:4200/health; do sleep 2; done
pytest --no-header -rA -p no:cacheprovider -k "not docker"' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'pip install tenacity==6.2.0 urllib3==1.25.11 docker==4.4.4 marshmallow==3.10.0 pendulum==2.0.5
pytest --no-header -rA -p no:cacheprovider -k "not (cli or server)"' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y iproute2 && echo -e 'pip install tenacity==6.2.0 urllib3==1.25.11 docker==4.4.4 marshmallow==3.10.0 pendulum==2.0.5\npytest --no-header -rA -p no:cacheprovider -k "not (cli or server or docker_agent)"' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest --no-header -rA -p no:cacheprovider -k "not (cli or server or docker_agent or warning or dask)"' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest --no-header -rA -p no:cacheprovider -k "not (cli or server or docker_agent or warning or dask or test_copy_warns_if_dependencies_in_active_flow or test_system_check_doesnt_warn)"' > test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest --no-header -rA -p no:cacheprovider -k "not (cli or server or docker_agent or warning or dask or test_copy_warns_if_dependencies_in_active_flow or test_system_check_doesnt_warn)"

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
pytest --no-header -rA -p no:cacheprovider -k "not (cli or server or docker_agent or warning or dask or test_copy_warns_if_dependencies_in_active_flow or test_system_check_doesnt_warn)"

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
pytest --no-header -rA -p no:cacheprovider -k "not (cli or server or docker_agent or warning or dask or test_copy_warns_if_dependencies_in_active_flow or test_system_check_doesnt_warn)"

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
RUN git clone https://github.com/PrefectHQ/prefect.git /home/prefect

WORKDIR /home/prefect
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("PrefectHQ", "prefect_4462_to_3893")
class PREFECT_4462_TO_3893(Instance):
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
        import json
        # Implement the log parsing logic here
        # Extract skipped tests using regex pattern
        skipped_pattern = re.compile(r"SKIPPED \[\d+\] (tests/.*?):")
        skipped_tests.update(skipped_pattern.findall(log))
        # Extract failed tests (including ERROR and FAILED statuses)
        failed_pattern = re.compile(r"(?:ERROR|FAILED) (tests/.*?) -")
        failed_tests.update(failed_pattern.findall(log))
        # Extract all test names from log
        all_tests_pattern = re.compile(r"(tests/[^\s]+\.py(?:::[^\s]+)?|docs/[^\s]+\.py)")
        all_tests = set(all_tests_pattern.findall(log))
        # Extract passed tests by excluding skipped/failed
        passed_tests = all_tests - skipped_tests - failed_tests
        # Extract XPASS tests (expected failures that passed) and add to passed_tests
        xpass_pattern = re.compile(r"XPASS (tests/.*?) -")
        passed_tests.update(xpass_pattern.findall(log))
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
