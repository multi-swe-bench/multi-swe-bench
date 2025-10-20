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
        return "node:18-bullseye-slim"
    
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
                """npm install
###ACTION_DELIMITER###
npm run test:unit
###ACTION_DELIMITER###
echo -e '#!/bin/bash
npm run test:unit -- -v
npm run test:snap -- -v' > /home/tdesign-mobile-vue/test_commands.sh && chmod +x /home/tdesign-mobile-vue/test_commands.sh
###ACTION_DELIMITER###
bash /home/tdesign-mobile-vue/test_commands.sh
###ACTION_DELIMITER###
npm run init
###ACTION_DELIMITER###
bash /home/tdesign-mobile-vue/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
npm run test:unit -- -v
npm run test:snap -- -v

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
npm run test:unit -- -v
npm run test:snap -- -v

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
npm run test:unit -- -v
npm run test:snap -- -v

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

# Choose an appropriate base image based on the project's requirements - replace node:18-bullseye-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:18-bullseye-slim

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
RUN git clone https://github.com/Tencent/tdesign-mobile-vue.git /home/tdesign-mobile-vue

WORKDIR /home/tdesign-mobile-vue
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Tencent", "tdesign_mobile_vue_1149_to_unknown")
class TDESIGN_MOBILE_VUE_1149_TO_UNKNOWN(Instance):
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
        # Clean line number prefixes (e.g., [   1] )
        cleaned_lines = [re.sub(r'^\[\s*\d+\]\s*', '', line) for line in log.split('\n')]
        # Remove lines before the first JSON object start
        json_start_line = None
        for i, line in enumerate(cleaned_lines):
            if line.strip().startswith('{'):
                json_start_line = i
                break
        if json_start_line is not None:
            cleaned_lines = cleaned_lines[json_start_line:]
        cleaned_log = '\n'.join(cleaned_lines)
        # Extract JSON by finding first '{' and tracking brace balance
        first_brace = cleaned_log.find('{')
        if first_brace == -1:
            return {
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests
            }
        brace_balance = 1
        json_end = first_brace + 1
        in_string = False
        escape = False
        for i in range(first_brace + 1, len(cleaned_log)):
            char = cleaned_log[i]
            if escape:
                escape = False
            elif char == '"':
                in_string = not in_string
            elif char == '\\':
                escape = True
            if not in_string:
                if char == '{':
                    brace_balance += 1
                elif char == '}':
                    brace_balance -= 1
            if brace_balance == 0:
                json_end = i + 1
                break
        json_content = cleaned_log[first_brace:json_end].strip()
        if not json_content:
            return {
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests
            }
        # Parse the JSON content using raw_decode to handle trailing characters
        try:
            decoder = json.JSONDecoder()
            log_data, _ = decoder.raw_decode(json_content)
        except json.JSONDecodeError:
            return {
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests
            }
        # Iterate through test results and assertion results
        test_results = log_data.get("testResults", [])
        for test_result in test_results:
            assertion_results = test_result.get("assertionResults", [])
            for assertion in assertion_results:
                full_name = assertion.get("fullName", "").strip()
                status = assertion.get("status", "").lower()
                if not full_name:
                    continue  # Skip tests with no name
                if status == "passed":
                    passed_tests.add(full_name)
                elif status == "failed":
                    failed_tests.add(full_name)
                elif status in ("skipped", "pending"):
                    skipped_tests.add(full_name)
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
