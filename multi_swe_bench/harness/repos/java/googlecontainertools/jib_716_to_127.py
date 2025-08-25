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
                """ls -F
###ACTION_DELIMITER###
ls -F
###ACTION_DELIMITER###
apt-get update && apt-get install -y maven
###ACTION_DELIMITER###
apt-get install -y gradle
###ACTION_DELIMITER###
cd jib-core && ./gradlew googleJavaFormat build
###ACTION_DELIMITER###
java -version
###ACTION_DELIMITER###
ls -F
###ACTION_DELIMITER###
sed -i 's/gradle-4.6-bin.zip/gradle-7.6-bin.zip/' gradle/wrapper/gradle-wrapper.properties
###ACTION_DELIMITER###
./gradlew googleJavaFormat build
###ACTION_DELIMITER###
sed -i 's/gradle-7.6-bin.zip/gradle-8.4-bin.zip/' gradle/wrapper/gradle-wrapper.properties
###ACTION_DELIMITER###

###ACTION_DELIMITER###
./gradlew googleJavaFormat build
###ACTION_DELIMITER###
cd ..
###ACTION_DELIMITER###
apt-get install -y openjdk-8-jdk
###ACTION_DELIMITER###
update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java
###ACTION_DELIMITER###
git status
###ACTION_DELIMITER###
git restore jib-core/gradle/wrapper/gradle-wrapper.properties
###ACTION_DELIMITER###
cd jib-core && ./gradlew googleJavaFormat build
###ACTION_DELIMITER###
cd jib-core && ./gradlew build -x javadoc
###ACTION_DELIMITER###
cd ..
###ACTION_DELIMITER###
cd jib-core && ./gradlew build -x javadoc
###ACTION_DELIMITER###
cd ..
###ACTION_DELIMITER###
cd jib-gradle-plugin && ./gradlew googleJavaFormat build install -x javadoc
###ACTION_DELIMITER###
cd ../jib-maven-plugin && ./mvnw fmt:format install -U
###ACTION_DELIMITER###
echo "set -e
(cd jib-core && ./gradlew build -x javadoc)
(cd jib-gradle-plugin && ./gradlew build install -x javadoc)
(cd jib-maven-plugin && ./mvnw install -U)" > /home/jib/test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
set -e
(cd jib-core && ./gradlew build -x javadoc)
(cd jib-gradle-plugin && ./gradlew build install -x javadoc)
(cd jib-maven-plugin && ./mvnw install -U)

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
set -e
(cd jib-core && ./gradlew build -x javadoc)
(cd jib-gradle-plugin && ./gradlew build install -x javadoc)
(cd jib-maven-plugin && ./mvnw install -U)

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
set -e
(cd jib-core && ./gradlew build -x javadoc)
(cd jib-gradle-plugin && ./gradlew build install -x javadoc)
(cd jib-maven-plugin && ./mvnw install -U)

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
RUN git clone https://github.com/googlecontainertools/jib.git /home/jib

WORKDIR /home/jib
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("googlecontainertools", "jib_716_to_127")
class JIB_716_TO_127(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re
        # Pattern for Maven test results summary line
        maven_result_pattern = re.compile(
            r"Tests run: \d+, Failures: (\d+), Errors: (\d+), Skipped: (\d+).* in ([\w\.]+)"
        )
        # Pattern to identify a line indicating a test class is starting in Maven
        maven_running_pattern = re.compile(r"Running ([\w\.]+)")
        # Pattern for Gradle test failures. Example: "com.google.cloud.tools.jib.api.ContainerizerTest > testTo_dockerDaemon FAILED"
        gradle_failure_pattern = re.compile(r"([\w\.]+) > [\w\s\d_]+ FAILED")
        # Find all tests that were started
        running_tests = set(maven_running_pattern.findall(log))
        # Find all tests that have a result line (passed, failed, or skipped) in Maven
        tests_with_results = set()
        for line in log.splitlines():
            maven_match = maven_result_pattern.search(line)
            if maven_match:
                failures, errors, skipped, name = maven_match.groups()
                tests_with_results.add(name)
                if int(failures) > 0 or int(errors) > 0:
                    failed_tests.add(name)
                elif int(skipped) > 0:
                    skipped_tests.add(name)
                else:
                    passed_tests.add(name)
            gradle_match = gradle_failure_pattern.search(line)
            if gradle_match:
                failed_tests.add(gradle_match.group(1))
        # Identify tests that started but did not finish (implies failure)
        unfinished_tests = running_tests - tests_with_results
        failed_tests.update(unfinished_tests)
        # Handle Gradle tests for successful builds
        if "BUILD SUCCESSFUL" in log:
            # A simple pattern for any gradle test line.
            #gradle_test_line = re.compile(r"^([\w\.]+) > .*$", re.MULTILINE)
            gradle_test_line = re.compile(r"^([a-zA-Z0-9\-_\.]+) > ([a-zA-Z0-9\-_]+) .+$", re.MULTILINE)
            all_gradle_tests = set(gradle_test_line.findall(log))
            for test in all_gradle_tests:
                # check the test is a valid test name format.
                if re.match(r'^(com|org)\..*Test$', test[0]):
                     if test[0] not in failed_tests and test[0] not in skipped_tests:
                        passed_tests.add(test[0])
        # If build fails, we might not have 'Running...' lines for tests that failed during compilation
        if "BUILD FAILED" in log:
            # Look for compilation errors and extract class names
            compilation_error_pattern = re.compile(r"([a-zA-Z0-9\.\/]+)\.java:\d+:\serror:")
            matches = compilation_error_pattern.findall(log)
            for match in matches:
                # convert path to class name
                class_name = match.replace('/', '.')
                #find the first occurrence of a test class name
                m = re.search(r'((?:com|org)\.(?:[a-zA-Z0-9]+\.)+[a-zA-Z0-9]+Test)', class_name)
                if(m):
                    failed_tests.add(m.group(1))
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
