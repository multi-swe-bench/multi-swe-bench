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
        return "node:20-bookworm"
    
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
                """apt-get update
###ACTION_DELIMITER###
apt-get install -y xvfb libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libnss3 libcups2 libxss1 libxrandr2 libgconf-2-4 libasound2 libpangocairo-1.0-0 libatk1.0-0 libatk-bridge2.0-0 libgtk-3-0
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
echo -e '#!/bin/bash
xvfb-run --auto-servernum npm test -- --verbose' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libgbm1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PUPPETEER_LAUNCH_ARGS="--no-sandbox --disable-setuid-sandbox"
xvfb-run --auto-servernum npm test -- --verbose' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
xvfb-run --auto-servernum env PUPPETEER_ARGS="--no-sandbox --disable-setuid-sandbox" npm test -- --verbose' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PUPPETEER_LAUNCH_ARGS="--no-sandbox --disable-setuid-sandbox"
xvfb-run --auto-servernum npm test -- --verbose' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PUPPETEER_DEFAULT_ARGS="--no-sandbox --disable-setuid-sandbox"
xvfb-run --auto-servernum npm test -- --verbose' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export PUPPETEER_ARGS="--no-sandbox --disable-setuid-sandbox"
xvfb-run --auto-servernum npm test -- --verbose' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export CHROME_FLAGS="--no-sandbox --disable-setuid-sandbox"
xvfb-run --auto-servernum npm test -- --verbose' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
PUPPETEER_CHROME_PATH=$(node -p "require(\'puppeteer\').executablePath()")
echo -e "#!/bin/bash\n\"$PUPPETEER_CHROME_PATH\" --no-sandbox --disable-setuid-sandbox \"\$@\"" > chrome-wrapper
chmod +x chrome-wrapper
export PUPPETEER_EXECUTABLE_PATH="$PWD/chrome-wrapper"
xvfb-run --auto-servernum npm test -- --verbose' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
echo -e '#!/bin/bash\nexport PUPPETEER_LAUNCH_ARGS="--no-sandbox --disable-setuid-sandbox"\nxvfb-run --auto-servernum npm test -- --verbose' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e 'module.exports = { launch: { args: ["--no-sandbox", "--disable-setuid-sandbox"] } };' > .puppeteerrc.cjs
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
npx puppeteer browsers install chrome
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
echo -e '#!/bin/bash
/root/.cache/puppeteer/chrome/linux-130.0.6723.58/chrome-linux64/chrome --no-sandbox --disable-setuid-sandbox "$@"' > /usr/local/bin/chrome-wrapper && chmod +x /usr/local/bin/chrome-wrapper
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nexport PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chrome-wrapper\nxvfb-run --auto-servernum npm test -- --verbose' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nexport PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chrome-wrapper\nxvfb-run --auto-servernum -s "-screen 0 1920x1080x24" npm test -- --verbose --testTimeout=60000' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nexport PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chrome-wrapper\nxvfb-run --auto-servernum -s "-screen 0 1920x1080x24" npm test -- --verbose --testTimeout=60000 --maxWorkers=1' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i '264s/page.goto(href)/page.goto(href, { timeout: 60000 })' shared/helpers/puppeteer.js
###ACTION_DELIMITER###
sed -i '264s/page.goto(href)/page.goto(href, { timeout: 60000 })/' shared/helpers/puppeteer.js
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i '264s/60000/90000/' shared/helpers/puppeteer.js
###ACTION_DELIMITER###

###ACTION_DELIMITER###
echo "jest.setTimeout(90000);" > jest.setup.js
###ACTION_DELIMITER###
sed -i 's/npm test -- --verbose/npm test -- --verbose --setupFilesAfterEnv=jest.setup.js/' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/jest.setup.js/\/home\/govuk-frontend\/jest.setup.js/' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
export PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chrome-wrapper
xvfb-run --auto-servernum -s "-screen 0 1920x1080x24" npm test -- --verbose --setupFilesAfterEnv=/home/govuk-frontend/jest.setup.js --testTimeout=60000 --maxWorkers=1

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
export PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chrome-wrapper
xvfb-run --auto-servernum -s "-screen 0 1920x1080x24" npm test -- --verbose --setupFilesAfterEnv=/home/govuk-frontend/jest.setup.js --testTimeout=60000 --maxWorkers=1

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
export PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chrome-wrapper
xvfb-run --auto-servernum -s "-screen 0 1920x1080x24" npm test -- --verbose --setupFilesAfterEnv=/home/govuk-frontend/jest.setup.js --testTimeout=60000 --maxWorkers=1

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
FROM node:20-bookworm

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
RUN git clone https://github.com/alphagov/govuk-frontend.git /home/govuk-frontend

WORKDIR /home/govuk-frontend
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("alphagov", "govuk_frontend_5627_to_unknown")
class GOVUK_FRONTEND_5627_TO_UNKNOWN(Instance):
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
        # Remove ANSI escape codes from log content
        log_clean = re.sub(r'\x1b\[[0-9;]*m', '', log)
        # Pattern for passed tests: matches lines like "✓ shows the navigation (25 ms)"
        pass_pattern = re.compile(r'^(?:\[\s*\d+\s*\]\s*)?\s*(✓|PASS)\s+(.*)', re.IGNORECASE)
        # Pattern for failed tests: matches lines like "● Input › when it includes a prefix › renders the prefix inside the wrapper"
        fail_pattern_case = re.compile(r'.*●\s+(.*)')
        fail_pattern_suite = re.compile(r'.*FAIL\s+(.*)')
        for line in log_clean.split('\n'):
            # Check for passed tests
            pass_match = pass_pattern.search(line)
            if pass_match:
                test_name = pass_match.group(2).strip()
                passed_tests.add(test_name)
            # Check for failed tests
            # Check for failed test cases
            fail_match_case = fail_pattern_case.search(line)
            if fail_match_case:
                test_name = fail_match_case.group(1).strip()
                failed_tests.add(test_name)
            # Check for failed test suites
            fail_match_suite = fail_pattern_suite.search(line)
            if fail_match_suite:
                test_name = fail_match_suite.group(1).strip()
                failed_tests.add(test_name)
            # Check for skipped tests (placeholder)
            # skip_pattern = re.compile(r'^\s*SKIPPED\s+(.*?)\s*$')
            # skip_match = skip_pattern.search(line)
            # if skip_match:
            #     test_name = skip_match.group(1).strip()
            #     skipped_tests.add(test_name)
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
