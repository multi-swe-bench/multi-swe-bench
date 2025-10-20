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
        return "node:18"
    
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
                """apt-get update && apt-get install -y build-essential python3
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
npx xo --fix
###ACTION_DELIMITER###
sed -i 's/\.\.\/lib\/fork\.js/\.\.\/lib\/fork/g' test/fork.js test/hooks.js
###ACTION_DELIMITER###
echo -e '#!/bin/bash
xo --quiet && nyc tap --no-cov --timeout=150 test/*.js test/reporters/*.js --verbose' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
npx xo --quiet && nyc tap --no-cov --timeout=150 test/*.js test/reporters/*.js --verbose' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
npx xo --quiet && npx nyc tap --no-cov --timeout=150 test/*.js test/reporters/*.js --verbose' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
npx xo --quiet && npx nyc tap --no-cov --timeout=150 test/*.js test/reporters/*.js' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
npx xo --quiet && npx nyc tap --no-cov --timeout=150 test/*.js test/reporters/*.js

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
npx xo --quiet && npx nyc tap --no-cov --timeout=150 test/*.js test/reporters/*.js

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
npx xo --quiet && npx nyc tap --no-cov --timeout=150 test/*.js test/reporters/*.js

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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:18

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
RUN git clone https://github.com/avajs/ava.git /home/ava

WORKDIR /home/ava
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("avajs", "ava_1179_to_961")
class AVA_1179_TO_961(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        # Removed unused json import
        # Parse passed tests (handles subtests and optional comments)
        passed_pattern = re.compile(r'^ok\s+\d+\s+-\s+(.*?)(?:\s+#.*)?$', re.MULTILINE)
        passed_tests.update([name.strip() for name in passed_pattern.findall(log)])
        # Parse failed tests with post-processing to exclude error messages
        failed_pattern = re.compile(r'^not ok\s+\d+\s+-\s+(.*?)(?:\s+#.*)?$', re.MULTILINE)
        for name in failed_pattern.findall(log):
            cleaned_name = name.strip()
            failed_tests.add(cleaned_name)
        # Parse skipped subtests (1..0 indicates no tests ran)
        skipped_pattern = re.compile(r'^\s*# Subtest: (.*?)\n\s+1..0$', re.MULTILINE)
        skipped_tests.update([name.strip() for name in skipped_pattern.findall(log)])
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
