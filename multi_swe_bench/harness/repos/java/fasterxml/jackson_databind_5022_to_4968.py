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
                """ls
###ACTION_DELIMITER###
apt-get update && apt-get install -y maven openjdk-8-jdk
###ACTION_DELIMITER###
mvn clean install
###ACTION_DELIMITER###
ls -a ..
###ACTION_DELIMITER###
cd /home
###ACTION_DELIMITER###
git clone https://github.com/FasterXML/jackson.git /home/jackson
###ACTION_DELIMITER###
ls /home/jackson
###ACTION_DELIMITER###
cd /home/jackson-databind && mvn clean install -DskipTests
###ACTION_DELIMITER###
cd /home/jackson && mvn clean install -DskipTests
###ACTION_DELIMITER###
git clone https://github.com/FasterXML/jackson-base.git /home/jackson-base
###ACTION_DELIMITER###
mvn dependency:list
###ACTION_DELIMITER###
cd /home/jackson-databind
###ACTION_DELIMITER###
mvn clean install -U
###ACTION_DELIMITER###
git clone https://github.com/FasterXML/jackson-base.git /home/jackson-base
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget https://oss.sonatype.org/content/repositories/snapshots/com/fasterxml/jackson/jackson-base/2.19.0-SNAPSHOT/jackson-base-2.19.0-SNAPSHOT.pom
###ACTION_DELIMITER###
ls /home/jackson
###ACTION_DELIMITER###
ls /home
###ACTION_DELIMITER###
apt-get install -y unzip
###ACTION_DELIMITER###
wget https://github.com/FasterXML/jackson-base/archive/refs/heads/main.zip
###ACTION_DELIMITER###
git clone https://github.com/FasterXML/jackson-bom.git /home/jackson-bom
###ACTION_DELIMITER###
cd /home/jackson-bom && mvn clean install -DskipTests
###ACTION_DELIMITER###

###ACTION_DELIMITER###
cd /home/jackson-databind && mvn clean install -DskipTests
###ACTION_DELIMITER###

###ACTION_DELIMITER###
cd /home/jackson-bom && git checkout 2.19
###ACTION_DELIMITER###
cd /home/jackson-bom && mvn clean install -DskipTests
###ACTION_DELIMITER###
sed -i 's|<version>2.19.0-SNAPSHOT</version>|<version>2.19.3-SNAPSHOT</version>|g' /home/jackson-databind/pom.xml
###ACTION_DELIMITER###
cd /home/jackson-databind && mvn clean install -DskipTests
###ACTION_DELIMITER###
java -version
###ACTION_DELIMITER###
update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java
###ACTION_DELIMITER###
update-alternatives --set javac /usr/lib/jvm/java-8-openjdk-amd64/bin/javac
###ACTION_DELIMITER###
cd /home/jackson-databind && mvn clean install -DskipTests
###ACTION_DELIMITER###
cd /home/jackson-databind && mvn clean install
###ACTION_DELIMITER###
echo "mvn test -Dstyle.color=never" > /home/jackson-databind/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
mvn test -Dstyle.color=never

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
mvn test -Dstyle.color=never

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
mvn test -Dstyle.color=never

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


@Instance.register("fasterxml", "jackson_databind_5022_to_4968")
class JACKSON_DATABIND_5022_TO_4968(Instance):
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
        import json
        pattern = re.compile(r"Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+), Time elapsed: .* s(?: <<< FAILURE!)? -- in (.*)")
        for line in log.splitlines():
            match = pattern.search(line)
            if match:
                _, failures, errors, skipped, test_name = match.groups()
                test_name = test_name.strip()
                if int(failures) > 0 or int(errors) > 0:
                    failed_tests.add(test_name)
                elif int(skipped) > 0:
                    skipped_tests.add(test_name)
                else:
                    passed_tests.add(test_name)
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
