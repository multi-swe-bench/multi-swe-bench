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
        return "ubuntu:22.04"

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
ls -la .github
###ACTION_DELIMITER###
ls -la .github/workflows
###ACTION_DELIMITER###
echo -e '#!/bin/bash
SUB_BUILD=PLATFORM ./gradlew test --info --continue
SUB_BUILD=PLATFORM ./gradlew newIntegrationTest --info --continue
SUB_BUILD=PLATFORM ./gradlew slowIntegrationTest --info --continue
./tools/bin/e2e_test.sh' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y openjdk-17-jdk nodejs npm python3.9 python3-pip automake build-essential libtool libtool-bin autoconf
###ACTION_DELIMITER###
./gradlew build --scan
###ACTION_DELIMITER###
apt-get install -y docker.io
###ACTION_DELIMITER###
service docker start
###ACTION_DELIMITER###
systemctl start docker
###ACTION_DELIMITER###
docker ps
###ACTION_DELIMITER###
dockerd &
###ACTION_DELIMITER###
docker ps
###ACTION_DELIMITER###
ps aux | grep dockerd
###ACTION_DELIMITER###
./gradlew build -x :airbyte-cdk:python:build --scan
###ACTION_DELIMITER###
dockerd
###ACTION_DELIMITER###
dockerd --iptables=false &
###ACTION_DELIMITER###
docker ps
###ACTION_DELIMITER###
dockerd --storage-driver=vfs --iptables=false &
###ACTION_DELIMITER###
ps aux | grep dockerd
###ACTION_DELIMITER###
sed -i '3s/^/\/\//' airbyte-cdk/python/build.gradle
###ACTION_DELIMITER###
./gradlew build --scan
###ACTION_DELIMITER###
sed -i '2s/^/\/\//' airbyte-integrations/bases/base/build.gradle""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
SUB_BUILD=PLATFORM ./gradlew test --info --continue
SUB_BUILD=PLATFORM ./gradlew newIntegrationTest --info --continue
SUB_BUILD=PLATFORM ./gradlew slowIntegrationTest --info --continue
./tools/bin/e2e_test.sh

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
SUB_BUILD=PLATFORM ./gradlew test --info --continue
SUB_BUILD=PLATFORM ./gradlew newIntegrationTest --info --continue
SUB_BUILD=PLATFORM ./gradlew slowIntegrationTest --info --continue
./tools/bin/e2e_test.sh

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
SUB_BUILD=PLATFORM ./gradlew test --info --continue
SUB_BUILD=PLATFORM ./gradlew newIntegrationTest --info --continue
SUB_BUILD=PLATFORM ./gradlew slowIntegrationTest --info --continue
./tools/bin/e2e_test.sh

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:22.04 with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:22.04

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
RUN git clone https://github.com/airbytehq/airbyte.git /home/airbyte

WORKDIR /home/airbyte
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("airbytehq", "airbyte_14650_to_14251")
class AIRBYTE_14650_TO_14251(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        import json

        # Regex pattern to match test lines
        test_pattern = re.compile(r"(\w+Test) > (\w+)\(\) .*")
        matches = list(test_pattern.finditer(log))
        for i, match in enumerate(matches):
            test_class = match.group(1)
            test_method = match.group(2)
            test_name = f"{test_class}.{test_method}"
            # Determine the end of the current test section
            end = match.end()
            next_start = matches[i + 1].start() if (i + 1) < len(matches) else len(log)
            test_section = log[end:next_start]
            # Check for ERROR in the test section to classify as failed
            if "ERROR" in test_section:
                failed_tests.add(test_name)
            else:
                passed_tests.add(test_name)
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
