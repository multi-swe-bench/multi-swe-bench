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
                """apt-get update && apt-get install -y locales && locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
###ACTION_DELIMITER###
locale
###ACTION_DELIMITER###
locale -a
###ACTION_DELIMITER###
sed -i 's/^# *en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
###ACTION_DELIMITER###
locale
###ACTION_DELIMITER###
cat /etc/default/locale
###ACTION_DELIMITER###
export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 && locale
###ACTION_DELIMITER###
grep 'en_US.UTF-8' /etc/locale.gen
###ACTION_DELIMITER###
locale -a
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pytest -v --no-header -rA --tb=short -p no:cacheprovider -m "not e2e"' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-11-jre-headless && export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64 && echo 'export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64' >> /etc/profile
###ACTION_DELIMITER###
apt-cache search openjdk | grep -i 'jre-headless'
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-17-jre-headless && export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 && echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> /etc/profile
###ACTION_DELIMITER###
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 && bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy && bash test_commands.sh
###ACTION_DELIMITER###
pip install --force-reinstall numpy && bash test_commands.sh
###ACTION_DELIMITER###
pip install numpy==1.26.0 && echo -e '#!/bin/bash
pytest -v --no-header -rA --tb=short -p no:cacheprovider -m "not e2e" --no-sqlalchemy' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pytest -v --no-header -rA --tb=short -p no:cacheprovider -m "not e2e" --no-sqlalchemy --ignore=tests/test_definitions/test_expectations_v3_api.py' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip install pandas==1.5.3 && bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pytest -v --no-header -rA --tb=short -p no:cacheprovider -m "not e2e" --no-sqlalchemy --ignore=tests/test_definitions/test_expectations_v3_api.py --ignore=tests/datasource/data_connector/test_configured_asset_glue_catalog_data_connector.py --ignore=tests/integration/usage_statistics/test_usage_stats_common_messages_are_sent_v3api.py --ignore=tests/profile/test_user_configurable_profiler_v3_batch_request.py --ignore=tests/render/renderer/v3/test_suite_edit_notebook_renderer.py' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
pytest -v --no-header -rA --tb=short -p no:cacheprovider -m "not e2e" --no-sqlalchemy --ignore=tests/test_definitions/test_expectations_v3_api.py --ignore=tests/datasource/data_connector/test_configured_asset_glue_catalog_data_connector.py --ignore=tests/integration/usage_statistics/test_usage_stats_common_messages_are_sent_v3api.py --ignore=tests/profile/test_user_configurable_profiler_v3_batch_request.py --ignore=tests/render/renderer/v3/test_suite_edit_notebook_renderer.py

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
pytest -v --no-header -rA --tb=short -p no:cacheprovider -m "not e2e" --no-sqlalchemy --ignore=tests/test_definitions/test_expectations_v3_api.py --ignore=tests/datasource/data_connector/test_configured_asset_glue_catalog_data_connector.py --ignore=tests/integration/usage_statistics/test_usage_stats_common_messages_are_sent_v3api.py --ignore=tests/profile/test_user_configurable_profiler_v3_batch_request.py --ignore=tests/render/renderer/v3/test_suite_edit_notebook_renderer.py

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
pytest -v --no-header -rA --tb=short -p no:cacheprovider -m "not e2e" --no-sqlalchemy --ignore=tests/test_definitions/test_expectations_v3_api.py --ignore=tests/datasource/data_connector/test_configured_asset_glue_catalog_data_connector.py --ignore=tests/integration/usage_statistics/test_usage_stats_common_messages_are_sent_v3api.py --ignore=tests/profile/test_user_configurable_profiler_v3_batch_request.py --ignore=tests/render/renderer/v3/test_suite_edit_notebook_renderer.py

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
RUN git clone https://github.com/great-expectations/great_expectations.git /home/great_expectations

WORKDIR /home/great_expectations
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("great-expectations", "great_expectations_7313_to_6981")
class GREAT_EXPECTATIONS_7313_TO_6981(Instance):
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
        passed_tests = set[str]() # Tests that passed successfully
        failed_tests = set[str]() # Tests that failed
        skipped_tests = set[str]() # Tests that were skipped
        import re
        import json
        # Define regex patterns to match test lines
        # Pattern 1: Test name followed by status and progress (e.g., "[  0%]")
        pattern1 = re.compile(r'^(.*?)\s+(PASSED|FAILED|SKIPPED|XFAIL)\s+\[\s*\d+%\s*\]$')
        # Pattern 2: Status followed by test name (with optional message after '-')
        pattern2 = re.compile(r'^(XFAIL|FAILED|SKIPPED|PASSED)\s+(.*?)(\s+-.*)?$')
        # Split log into lines and process each line
        for line in log.split('\n'):
            line = line.strip()
            if not line:
                continue
            match = pattern1.match(line)
            if match:
                test_name = match.group(1).strip()
                status = match.group(2).strip()
            else:
                match = pattern2.match(line)
                if match:
                    status = match.group(1).strip()
                    test_name = match.group(2).strip()
                else:
                    continue  # Skip lines that don't match
            # Categorize the test based on status
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status in ('FAILED', 'XFAIL'):
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
            # Ignore other statuses if any
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
