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
        return "node:20"
    
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
                """ls -la
###ACTION_DELIMITER###
npm run precompile
###ACTION_DELIMITER###
npm run compile
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl && curl -O https://download.clojure.org/install/linux-install-1.11.1.1435.sh && chmod +x linux-install-1.11.1.1435.sh && ./linux-install-1.11.1.1435.sh
###ACTION_DELIMITER###
npm run compile
###ACTION_DELIMITER###
apt-get update && apt-get install -y openjdk-17-jdk
###ACTION_DELIMITER###
npm run compile
###ACTION_DELIMITER###
echo -e '#!/bin/bash
set -e
npm run calva-lib-test
npx mocha -v --reporter spec --require ts-node/register "src/extension-test/unit/**/*-test.ts"
npm run integration-test
npm run e2e-test' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e
npm run calva-lib-test
npx mocha -v --reporter spec --require ts-node/register "src/extension-test/unit/**/*-test.ts"
npm run integration-test
npm run e2e-test

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
set -e
npm run calva-lib-test
npx mocha -v --reporter spec --require ts-node/register "src/extension-test/unit/**/*-test.ts"
npm run integration-test
npm run e2e-test

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
set -e
npm run calva-lib-test
npx mocha -v --reporter spec --require ts-node/register "src/extension-test/unit/**/*-test.ts"
npm run integration-test
npm run e2e-test

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
FROM node:20

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
RUN git clone https://github.com/BetterThanTomorrow/calva.git /home/calva

WORKDIR /home/calva
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("BetterThanTomorrow", "calva_2142_to_2027")
class CALVA_2142_TO_2027(Instance):
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
        import json
        # Parse test suites and cases using indentation and status markers
        test_hierarchy = []
        current_indent = 0
        summary_pattern = re.compile(r'.*\d+ (failures|errors|passing|failing)')  # Ignore summary lines, excluding pending to capture skipped tests
        current_suite = ''
        for line in log.split('\n'):
            line = line.rstrip('\r')
            indent = len(line) - len(line.lstrip())
            stripped_line = line.strip()
            # Skip summary headers
            if summary_pattern.match(stripped_line):
                continue
            # Track top-level test suites
            if stripped_line.startswith('Testing '):
                suite_name = stripped_line.split('Testing ')[1].strip()
                test_hierarchy = [suite_name]
                current_suite = suite_name
                current_indent = indent
                continue
            # Track parent test cases (indented, no status)
            if not stripped_line.startswith(('✔', '1)', 'pending')) and stripped_line:
                if indent > current_indent:
                    test_hierarchy.append(stripped_line)
                    current_indent = indent
                elif indent == current_indent and test_hierarchy:
                    test_hierarchy[-1] = stripped_line
                elif indent < current_indent and test_hierarchy:
                    levels_up = (current_indent - indent) // 4
                    test_hierarchy = test_hierarchy[:-levels_up]
                    if test_hierarchy:
                        test_hierarchy[-1] = stripped_line
                    else:
                        test_hierarchy = [stripped_line]
                else:
                    test_hierarchy = [stripped_line]
                current_indent = indent
                continue
            # Process test results
            if '✔' in stripped_line:
                test_name = stripped_line.lstrip('✔ ').strip()
                full_name = ' > '.join(test_hierarchy + [test_name])
                passed_tests.add(full_name)
            elif '1)' in stripped_line:
                # Map failed tests to full hierarchy
                test_name = stripped_line.lstrip('1) ').strip()
                # Extract parent context from previous lines
                parent_hierarchy = test_hierarchy.copy()
                full_name = ' > '.join(parent_hierarchy + [test_name])
                failed_tests.add(full_name)
            elif 'pending' in stripped_line:
                # Capture pending tests from summary (e.g., '5 pending')
                # Capture pending tests from summary using the current suite
                if current_suite:
                    skipped_tests.add(current_suite)
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
