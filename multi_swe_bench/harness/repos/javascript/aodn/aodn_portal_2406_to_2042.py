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
        return "openjdk:11-jdk-slim"

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
                """ls -la /home/aodn-portal
###ACTION_DELIMITER###
mvn -version
###ACTION_DELIMITER###
apt-get update && apt-get install -y maven
###ACTION_DELIMITER###
mvn -version
###ACTION_DELIMITER###
wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public | gpg --dearmor > /usr/share/keyrings/adoptium.gpg && echo "deb [signed-by=/usr/share/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print $2}' /etc/os-release) main" > /etc/apt/sources.list.d/adoptium.list && apt-get update && apt-get install -y temurin-8-jdk
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget gnupg
###ACTION_DELIMITER###
wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public | gpg --dearmor > /usr/share/keyrings/adoptium.gpg && echo "deb [signed-by=/usr/share/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print $2}' /etc/os-release) main" > /etc/apt/sources.list.d/adoptium.list && apt-get update && apt-get install -y temurin-8-jdk
###ACTION_DELIMITER###
update-alternatives --set java /usr/lib/jvm/temurin-8-jdk-amd64/bin/java && update-alternatives --set javac /usr/lib/jvm/temurin-8-jdk-amd64/bin/javac && java -version && mvn -version
###ACTION_DELIMITER###
ls /usr/lib/jvm/temurin-8-jdk-amd64/bin/java && update-alternatives --install /usr/bin/java java /usr/lib/jvm/temurin-8-jdk-amd64/bin/java 200 && update-alternatives --set java /usr/lib/jvm/temurin-8-jdk-amd64/bin/java && export JAVA_HOME=/usr/lib/jvm/temurin-8-jdk-amd64 && export PATH=$JAVA_HOME/bin:$PATH && java -version && mvn -version
###ACTION_DELIMITER###
mvn clean install
###ACTION_DELIMITER###
echo '#!/bin/bash
mvn clean test -Dstyle.color=never -e -Dsurefire.printSummary=always -Dsurefire.useFile=false' > /home/aodn-portal/test_commands.sh && chmod +x /home/aodn-portal/test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
mvn clean test -Dstyle.color=never -e -Dsurefire.printSummary=always -Dsurefire.useFile=false

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
mvn clean test -Dstyle.color=never -e -Dsurefire.printSummary=always -Dsurefire.useFile=false

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
mvn clean test -Dstyle.color=never -e -Dsurefire.printSummary=always -Dsurefire.useFile=false

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

# Choose an appropriate base image based on the project's requirements - replace openjdk:11-jdk-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM openjdk:11-jdk-slim

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
RUN git clone https://github.com/aodn/aodn-portal.git /home/aodn-portal

WORKDIR /home/aodn-portal
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("aodn", "aodn_portal_2406_to_2042")
class AODN_PORTAL_2406_TO_2042(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re

        # Implement the log parsing logic here
        # Extract all test names using regex patterns
        test_patterns = [
            re.compile(r"(test[A-Za-z0-9_]+)\(([A-Za-z0-9.]+)\)"),  # testMethod(Class)
            re.compile(r"([A-Za-z0-9.]+)\.(test[A-Za-z0-9_]+)"),  # Class.testMethod
        ]
        # Collect all unique test names (normalized to Class.testMethod)
        test_names = set()
        for line in log.split("\n"):
            line = line.strip()
            for pattern in test_patterns:
                match = pattern.search(line)
                if match:
                    if pattern == test_patterns[0]:
                        method, class_name = match.groups()
                        test_name = f"{class_name}.{method}"
                    else:
                        class_name, method = match.groups()
                        test_name = f"{class_name}.{method}"
                    test_names.add(test_name)
        # Identify failed tests by checking if their name appears in stack traces
        failed_tests = set()
        stack_trace_re = re.compile(
            r"at .*?(" + "|".join(re.escape(test) for test in test_names) + ")"
        )  # Match test names in stack traces (escaped for special chars)
        in_error = False
        for line in log.split("\n"):
            line = line.strip()
            # Detect error start (e.g., exception messages)
            if "java.lang." in line or "NullPointerException" in line:
                in_error = True
            # Check stack trace lines following an error
            if in_error and "at " in line:
                match = stack_trace_re.search(line)
                if match:
                    failed_test = match.group(1)
                    failed_tests.add(failed_test)
                    in_error = False  # Reset after finding the test
        # Passed tests are those not in failed_tests
        passed_tests = test_names - failed_tests
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
