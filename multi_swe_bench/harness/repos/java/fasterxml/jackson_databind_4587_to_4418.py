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
apt-get update
###ACTION_DELIMITER###
apt-get install -y maven openjdk-8-jdk
###ACTION_DELIMITER###
mvn test -Dstyle.color=never
###ACTION_DELIMITER###
./mvnw -B -ff -ntp clean verify
###ACTION_DELIMITER###
ls -aF
###ACTION_DELIMITER###
ls -l .mvn/wrapper
###ACTION_DELIMITER###
apt-get install -y git
###ACTION_DELIMITER###
cd /home && git clone https://github.com/FasterXML/jackson-base.git
###ACTION_DELIMITER###
ls -F
###ACTION_DELIMITER###
git clone --depth 1 https://github.com/FasterXML/jackson-base.git
###ACTION_DELIMITER###
ls -F
###ACTION_DELIMITER###
wget https://github.com/FasterXML/jackson-base/archive/refs/heads/master.zip
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget https://github.com/FasterXML/jackson-base/archive/refs/heads/master.zip
###ACTION_DELIMITER###
apt-get install -y unzip
###ACTION_DELIMITER###
wget https://github.com/FasterXML/jackson-base/archive/refs/heads/2.18.zip
###ACTION_DELIMITER###
cd /home
###ACTION_DELIMITER###
wget https://raw.githubusercontent.com/FasterXML/jackson-base/2.18/pom.xml
###ACTION_DELIMITER###
wget https://oss.sonatype.org/content/repositories/snapshots/com/fasterxml/jackson/jackson-base/2.18.0-SNAPSHOT/jackson-base-2.18.0-SNAPSHOT.pom
###ACTION_DELIMITER###
git tag
###ACTION_DELIMITER###
cd /home/jackson-databind
###ACTION_DELIMITER###
git tag
###ACTION_DELIMITER###
sed -i '12s/2.18.0-SNAPSHOT/2.17.0/' pom.xml && sed -i '16s/2.18.0-SNAPSHOT/2.17.0/' pom.xml
###ACTION_DELIMITER###
mvn clean install -DskipTests
###ACTION_DELIMITER###
apt-get install -y openjdk-21-jdk
###ACTION_DELIMITER###
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 && export PATH=$JAVA_HOME/bin:$PATH && mvn clean install -DskipTests
###ACTION_DELIMITER###
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 && export PATH=$JAVA_HOME/bin:$PATH && ./mvnw -B -ff -ntp clean verify
###ACTION_DELIMITER###
echo 'export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 && export PATH=$JAVA_HOME/bin:$PATH && ./mvnw -B -ff -ntp clean verify' > /home/jackson-databind/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 && export PATH=$JAVA_HOME/bin:$PATH && ./mvnw -B -ff -ntp clean verify

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
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 && export PATH=$JAVA_HOME/bin:$PATH && ./mvnw -B -ff -ntp clean verify

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
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 && export PATH=$JAVA_HOME/bin:$PATH && ./mvnw -B -ff -ntp clean verify

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
RUN git clone https://github.com/fasterxml/jackson-databind.git /home/jackson-databind

WORKDIR /home/jackson-databind
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("fasterxml", "jackson_databind_4587_to_4418")
class JACKSON_DATABIND_4587_TO_4418(Instance):
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
        # TODO: Implement the parse_log function
        # Implement the log parsing logic here
        # Pattern for compilation failures
        compilation_failure_pattern = re.compile(r'\[ERROR\] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:.*:testCompile')
        test_class_pattern = re.compile(r'src/test(?:-jdk\d+)?/java/(.*)\.java')
        # Patterns for test execution
        running_pattern = re.compile(r'\[INFO\] Running (.*)')
        summary_pattern = re.compile(r'\[INFO\] Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+), Time elapsed: .* s -- in (.*)')
        error_pattern = re.compile(r'\[ERROR\]   (.*):\d+')
        lines = log.split('\n')
        running_tests = {}
        if compilation_failure_pattern.search(log):
            for line in lines:
                if match := test_class_pattern.search(line):
                    test_class = match.group(1).replace('/', '.')
                    failed_tests.add(test_class)
            return {
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests
            }
        for i, line in enumerate(lines):
            if match := running_pattern.search(line):
                test_name = match.group(1)
                running_tests[test_name] = i
            elif match := summary_pattern.search(line):
                _, failures, errors, skipped, test_name = match.groups()
                if test_name in running_tests:
                    if int(failures) > 0 or int(errors) > 0:
                        failed_tests.add(test_name)
                    elif int(skipped) > 0:
                        skipped_tests.add(test_name)
                    else:
                        passed_tests.add(test_name)
                    del running_tests[test_name]
        # Check for tests that started but did not have a summary line
        for test_name in running_tests:
            failed_tests.add(test_name)
        # Second pass for error section
        in_error_section = False
        for line in lines:
            if line.startswith('[ERROR] Errors:'):
                in_error_section = True
            elif in_error_section and line.startswith('[INFO] Tests run:'):
                in_error_section = False
            elif in_error_section:
                if match := error_pattern.search(line):
                    failed_test_name = match.group(1).split('.')[0]
                    # Find the full test name
                    for test in list(passed_tests) + list(failed_tests) + list(skipped_tests):
                        if failed_test_name in test:
                            failed_tests.add(test)
                            if test in passed_tests:
                                passed_tests.remove(test)
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
