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
        return "node:20-bullseye"
    
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
                """node -v
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
###ACTION_DELIMITER###
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
###ACTION_DELIMITER###
nvm install 10
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
sed -i 's|https://github.com/mattkrick/draft-js/tarball/710c3ea2367953a70d71ac3d8cdf11bcf18f2f9e|git+https://github.com/mattkrick/draft-js.git#710c3ea2367953a70d71ac3d8cdf11bcf18f2f9e|g' package.json
###ACTION_DELIMITER###
yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
nvm install 8.5.0
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
sed -i 's|git+https://github.com/mattkrick/draft-js.git#710c3ea2367953a70d71ac3d8cdf11bcf18f2f9e|https://github.com/mattkrick/draft-js/tarball/710c3ea2367953a70d71ac3d8cdf11bcf18f2f9e|g' package.json
###ACTION_DELIMITER###
sed -i 's|https://github.com/mattkrick/draft-js/tarball/710c3ea2367953a70d71ac3d8cdf11bcf18f2f9e|https://codeload.github.com/mattkrick/draft-js/tar.gz/710c3ea2367953a70d71ac3d8cdf11bcf18f2f9e|g' package.json
###ACTION_DELIMITER###
yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
sed -i 's|https://codeload.github.com/mattkrick/draft-js/tar.gz/710c3ea2367953a70d71ac3d8cdf11bcf18f2f9e|https://api.github.com/repos/mattkrick/draft-js/tarball/710c3ea2367953a70d71ac3d8cdf11bcf18f2f9e|g' package.json
###ACTION_DELIMITER###
sed -i 's|https://api.github.com/repos/mattkrick/draft-js/tarball/710c3ea2367953a70d71ac3d8cdf11bcf18f2f9e|https://github.com/mattkrick/draft-js/archive/710c3ea2367953a70d71ac3d8cdf11bcf18f2f9e.tar.gz|g' package.json
###ACTION_DELIMITER###
yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
sed -i 's|https://github.com/mattkrick/draft-js/archive/710c3ea2367953a70d71ac3d8cdf11bcf18f2f9e.tar.gz|https://codeload.github.com/mattkrick/draft-js/tar.gz/710c3ea2367953a70d71ac3d8cdf11bcf18f2f9e|g' package.json
###ACTION_DELIMITER###
sed -i 's|https://codeload.github.com/mattkrick/draft-js/tar.gz/710c3ea2367953a70d71ac3d8cdf11bcf18f2f9e|^0.10.5|g' package.json
###ACTION_DELIMITER###
yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
rm -f yarn.lock && yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
apt-get update && apt-get install -y jq
###ACTION_DELIMITER###
jq '.resolutions += {"is-retry-allowed": "^1.2.0"}' package.json > temp.json && mv temp.json package.json
###ACTION_DELIMITER###
yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
jq '.resolutions += {"assets-webpack-plugin": "3.5.1"}' package.json > temp.json && mv temp.json package.json && yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
sed -i 's|"assets-webpack-plugin": "^3.5.1"|"assets-webpack-plugin": "3.5.1"|g' package.json && yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
jq '.resolutions += {"semver": "^6.3.0"}' package.json > temp.json && mv temp.json package.json && yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
jq '.resolutions += {"lru-cache": "^5.1.1"}' package.json > temp.json && mv temp.json package.json && yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
jq '.resolutions += {"@noble/hashes": "1.0.0"}' package.json > temp.json && mv temp.json package.json && yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
jq '.resolutions += {"aws-sdk": "2.999.0"}' package.json > temp.json && mv temp.json package.json && yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
jq '.resolutions."aws-sdk" = "2.99.0"' package.json > temp.json && mv temp.json package.json && yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
jq '.resolutions."aws-sdk" = "2.999.0"' package.json > temp.json && mv temp.json package.json && yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
jq '.resolutions."aws-sdk" = "2.800.0"' package.json > temp.json && mv temp.json package.json && yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
sed -i 's|"aws-sdk": "^2.99.0"|"aws-sdk": "2.999.0"|g' package.json && yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
jq '.resolutions += {"cheerio": "^0.22.0"}' package.json > temp.json && mv temp.json package.json && yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
jq '.resolutions += {"graphql-config": "3.4.0"}' package.json > temp.json && mv temp.json package.json && yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
jq '.resolutions += {"graphql-config": "2.2.1"}' package.json > temp.json && mv temp.json package.json && yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
jq '.resolutions += {"chai": "^4.3.7"}' package.json > temp.json && mv temp.json package.json && yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
jq '.resolutions += {"nanoid": "2.1.11"}' package.json > temp.json && mv temp.json package.json && yarn cache clean && rm -rf node_modules && yarn install
###ACTION_DELIMITER###
echo -e '#!/bin/bash
./node_modules/.bin/jest --verbose --no-bail' > test_commands.sh && chmod +x test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
./node_modules/.bin/jest --verbose --no-bail

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
./node_modules/.bin/jest --verbose --no-bail

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
./node_modules/.bin/jest --verbose --no-bail

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
FROM node:20-bullseye

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
RUN git clone https://github.com/ParabolInc/parabol.git /home/parabol

WORKDIR /home/parabol
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("ParabolInc", "parabol_1551_to_1549")
class PARABOL_1551_TO_1549(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re
        import json
        # Define regex patterns for test statuses
        # Account for ANSI escape codes and line structure
        ansi_escape = re.compile(r'\x1B\[[0-9;]*[mK]')  # Regex to remove ANSI codes
        # Patterns to match test status lines with line numbers and escape codes
        # Adjust pattern to match the sample failed test line
        # Increase flexibility with whitespace and ensure symbol matching
        # Simplify pattern to focus on bullet and test name
        failed_pattern = re.compile(r'●\s+(.*?)\s*$')  # Match any line with '●' followed by test name
        passed_pattern = re.compile(r'\[\d+\]\s+✓\s+(.*?)\s*$')  # Adjust for possible space differences
        skipped_pattern = re.compile(r'\[\d+\]\s+[○−]\s+(.*?)\s*$')  # Match skipped test symbols
        # Extract all test names from 'RUNS ...test.js' lines
        # Process log by removing ANSI codes first
        cleaned_log = ansi_escape.sub('', log)
        # Account for line numbers and ANSI codes in RUNS lines
        # Increase flexibility with whitespace and characters after RUNS
        # Explicitly match three dots and handle whitespace
        # Handle both three dots (...) and ellipsis (…) in RUNS lines
        # Simplify to capture any .test.js filename after RUNS
        # Match line number, RUNS, ellipsis, and test file name
        # Simplify to focus on RUNS, dots/ellipsis, and test file
        # Include line number prefix to match log structure
        # Simplify to capture any .test.js filename after RUNS
        # Match line number, RUNS, dots, and test file explicitly
        # Handle both dots and ellipsis, and allow flexibility in line structure
        # Simplify to capture test filename after RUNS
        # Explicitly match dots/ellipsis after RUNS to capture test filename
        # Include line number prefix to match the log structure
        # Allow any characters between RUNS and test filename to increase matching
        # Explicitly match three dots between RUNS and test filename
        # Handle both three dots (...) and ellipsis (…) in RUNS lines
        # Simplify to focus on RUNS, dots/ellipsis, and test filename
        # Include line number prefix to match log structure
        # Simplify to capture test filename after RUNS
        # Handle both three dots (...) and ellipsis (…) in RUNS lines
        # Include line number prefix to match log structure
        # Simplify to focus on RUNS, dots/ellipsis, and test filename
        # Include line number prefix to match log structure
        # Increase flexibility between RUNS and test filename
        # Explicitly match three dots to reliably capture test filenames
        # Handle both three dots and ellipsis to capture test filenames
        # Simplify to focus on RUNS, dots/ellipsis, and test filename
        # Include line number prefix to match log structure
        # Use a more permissive match between RUNS and test filename
        # Explicitly match dots after RUNS to capture test filenames
        # Handle both dots and ellipsis
        # Extract all test names from 'RUNS ...test.js' lines
        ansi_escape = re.compile(r'\x1B\[[0-9;]*[mK]')
        cleaned_log = ansi_escape.sub('', log)
        test_name_pattern = re.compile(r'RUNS\s+[\.…]+\s*([^\s]+\.test\.js)')
        all_tests = set(test_name_pattern.findall(cleaned_log))
        # Patterns to match test status lines
        failed_pattern = re.compile(r'.*●\s+(.*?)\s*$')  # Ignore leading chars before '●'
        skipped_pattern = re.compile(r'.*[○−]\s+(.*?)\s*$')  # Ignore leading chars before '○' or '−'
        # Extract failed tests (capture base name and append .test.js)
        failed_pattern = re.compile(r'.*●\s+([^›]+)›.*')  # Capture part before first '›'
        for line in cleaned_log.split('\n'):
            failed_match = failed_pattern.search(line)
            if failed_match:
                test_file = failed_match.group(1).strip() + ".test.js"
                failed_tests.add(test_file)
        # Extract skipped tests (capture base name and append .test.js)
        skipped_pattern = re.compile(r'.*[○−]\s+([^›]+)›.*')  # Capture part before first '›'
        for line in cleaned_log.split('\n'):
            skipped_match = skipped_pattern.search(line)
            if skipped_match:
                test_file = skipped_match.group(1).strip() + ".test.js"
                skipped_tests.add(test_file)
        # Calculate passed tests as all tests minus failed/skipped
        passed_tests = all_tests - failed_tests - skipped_tests
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
