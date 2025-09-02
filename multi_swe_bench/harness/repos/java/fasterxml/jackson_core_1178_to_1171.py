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
java -version
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y openjdk-8-jdk maven
###ACTION_DELIMITER###
echo "mvn clean test -Dstyle.color=never" > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cd .. && ls -F
###ACTION_DELIMITER###
ls -F jackson-core/
###ACTION_DELIMITER###
cd jackson-core
###ACTION_DELIMITER###
chmod +x mvnw
###ACTION_DELIMITER###
./mvnw clean test -Dstyle.color=never
###ACTION_DELIMITER###
mvn -N io.takari:maven:wrapper
###ACTION_DELIMITER###
echo "mvn clean test -U -Dstyle.color=never" > test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -e 's|<artifactId>jackson-base</artifactId>|<artifactId>jackson-parent</artifactId>|' pom.xml > pom.xml.new && mv pom.xml.new pom.xml
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls -aF
###ACTION_DELIMITER###
ls -F .github/
###ACTION_DELIMITER###
ls -F .github/workflows/
###ACTION_DELIMITER###
git checkout pom.xml
###ACTION_DELIMITER###
./mvnw -B -q -ff -ntp verify
###ACTION_DELIMITER###
mvn -N io.takari:maven:wrapper -Dmaven=3.8.7
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
cat .mvn/wrapper/maven-wrapper.properties
###ACTION_DELIMITER###
sed -i "s/3.9.3/3.8.7/g" .mvn/wrapper/maven-wrapper.properties
###ACTION_DELIMITER###

###ACTION_DELIMITER###
./mvnw -B -q -ff -ntp verify
###ACTION_DELIMITER###
cd /home/ && git clone https://github.com/FasterXML/jackson-base.git
###ACTION_DELIMITER###
cd /home/ && git clone --depth 1 https://github.com/FasterXML/jackson-base.git
###ACTION_DELIMITER###
ls -l
###ACTION_DELIMITER###
cd jackson-core
###ACTION_DELIMITER###
wget https://raw.githubusercontent.com/FasterXML/jackson-base/2.17/pom.xml -O jackson-base-pom.xml
###ACTION_DELIMITER###
mkdir -p ../jackson-base
###ACTION_DELIMITER###
wget https://raw.githubusercontent.com/FasterXML/jackson-base/master/pom.xml -O ../jackson-base/pom.xml
###ACTION_DELIMITER###
wget https://oss.sonatype.org/content/repositories/snapshots/com/fasterxml/jackson/jackson-base/2.17.0-SNAPSHOT/jackson-base-2.17.0-20240227.012829-3.pom -O ../jackson-base/pom.xml
###ACTION_DELIMITER###
mkdir -p ../jackson-parent
###ACTION_DELIMITER###

###ACTION_DELIMITER###
wget https://repo1.maven.org/maven2/com/fasterxml/jackson/jackson-parent/36/jackson-parent-36.pom -O ../jackson-parent/pom.xml
###ACTION_DELIMITER###
sed -i 's/2.17.0-SNAPSHOT/2.16.1/g' pom.xml
###ACTION_DELIMITER###
echo "mvn clean test -U -Dstyle.color=never" > test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
mvn clean test -U -Dstyle.color=never

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
mvn clean test -U -Dstyle.color=never

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
mvn clean test -U -Dstyle.color=never

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
RUN git clone https://github.com/fasterxml/jackson-core.git /home/jackson-core

WORKDIR /home/jackson-core
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("fasterxml", "jackson_core_1178_to_1171")
class JACKSON_CORE_1178_TO_1171(Instance):
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
        import json
        # TODO: Implement the parse_log function
        passed_tests_pattern = re.compile(r"Tests run: (\d+), Failures: 0, Errors: 0, Skipped: (\d+), Time elapsed: .* s -- in (.*)")
        failed_tests_pattern = re.compile(r"/home/jackson-core/src/test/java/(.*).java")
        for line in log.split("\n"):
            passed_match = passed_tests_pattern.search(line)
            if passed_match:
                test_name = passed_match.group(3)
                passed_tests.add(test_name)
                continue
            failed_match = failed_tests_pattern.search(line)
            if failed_match:
                test_name = failed_match.group(1).replace("/", ".")
                failed_tests.add(test_name)
                continue
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
