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
                """ls -la
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo -e '#!/bin/bash
TZ=UTC react-scripts test --testURL http://example.com/MAAS/r --watchAll=false --verbose
yarn test-cypress' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
TZ=UTC npx react-scripts test --testURL http://example.com/MAAS/r --watchAll=false --verbose
# Start server for Cypress tests
yarn start &
SERVER_PID=$!
# Wait for server to be ready
npx wait-on http://localhost:8401
# Run Cypress tests
yarn cypress-run
# Stop the server
kill $SERVER_PID' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
# Run unit tests with verbose output
TZ=UTC npx react-scripts test --testURL http://example.com/MAAS/r --watchAll=false --verbose
# Start server for E2E tests (simplified)
yarn serve-react &
SERVER_PID=$!
# Wait for React server to be ready on port 8401
npx wait-on http://localhost:8401
# Run Cypress tests in headless mode (faster) with verbose output
yarn cypress-run --headless --verbose
# Stop the server
kill $SERVER_PID' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
TZ=UTC npx react-scripts test --testURL http://example.com/MAAS/r --watchAll=false --verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
TZ=UTC npx react-scripts test --testURL http://example.com/MAAS/r --watchAll=false --verbose --runInBand --forceExit' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
TZ=UTC npx react-scripts test tests/ --testURL http://example.com/MAAS/r --watchAll=false --verbose --runInBand --forceExit' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
TZ=UTC react-scripts test tests/ --testURL http://example.com/MAAS/r --watchAll=false --verbose --forceExit' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
yarn test-ui --verbose --forceExit' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
TZ=UTC npx react-scripts test --testURL http://example.com/MAAS/r --watchAll=false --verbose --forceExit --maxWorkers=1' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
TZ=UTC CI=true npx react-scripts test tests/ --testURL http://example.com/MAAS/r --watchAll=false --verbose --forceExit --maxWorkers=1' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
TZ=UTC CI=true npx react-scripts test src/ --testURL http://example.com/MAAS/r --watchAll=false --verbose --forceExit --maxWorkers=2' > test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
apt-get update && apt-get install -y libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 libxtst6 xauth xvfb
###ACTION_DELIMITER###
echo -e '#!/bin/bash
# Start virtual display for headless testing
Xvfb :99 -screen 0 1024x768x16 &
DISPLAY=:99
# Run tests in CI mode with verbose output and forced exit
TZ=UTC CI=true npx react-scripts test --testURL http://example.com/MAAS/r --watchAll=false --verbose --runInBand --forceExit
# Stop virtual display
kill $!' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
# Use project's predefined test script with verbose output and forced exit
Xvfb :99 -screen 0 1024x768x16 &
DISPLAY=:99
yarn test-ui --verbose --forceExit
kill $!' > test_commands.sh
###ACTION_DELIMITER###
echo -e "#!/bin/bash\n# Start virtual display for headless testing\nXvfb :99 -screen 0 1024x768x16 &\nDISPLAY=:99\n# Run tests in CI mode with verbose output and forced exit\nTZ=UTC CI=true npx react-scripts test --testURL http://example.com/MAAS/r --watchAll=false --verbose --runInBand --forceExit\n# Stop virtual display\nkill \$!" > test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
# Start virtual display for headless testing
Xvfb :99 -screen 0 1024x768x16 &
DISPLAY=:99
# Run tests with verbose output and forced exit
TZ=UTC CI=true npx react-scripts test --testURL http://example.com/MAAS/r --watchAll=false --verbose --runInBand --forceExit
# Stop virtual display
kill $!' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
TZ=UTC CI=true npx react-scripts test --testURL http://example.com/MAAS/r --watchAll=false --verbose --runInBand --forceExit' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
TZ=UTC CI=true npx react-scripts test src/ --testURL http://example.com/MAAS/r --watchAll=false --verbose --runInBand --forceExit --maxWorkers=1' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nset -x\n# Verify test directory\nls -la tests/\n# Run tests with debugging and early exit\nTZ=UTC CI=true npx react-scripts test tests/ --testURL http://example.com/MAAS/r --watchAll=false --verbose --runInBand --forceExit --bail\nset +x' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -x
# Verify test directory
ls -la tests/
# Run tests with debugging and early exit
TZ=UTC CI=true npx react-scripts test tests/ --testURL http://example.com/MAAS/r --watchAll=false --verbose --runInBand --forceExit --bail
set +x

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
set -x
# Verify test directory
ls -la tests/
# Run tests with debugging and early exit
TZ=UTC CI=true npx react-scripts test tests/ --testURL http://example.com/MAAS/r --watchAll=false --verbose --runInBand --forceExit --bail
set +x

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
set -x
# Verify test directory
ls -la tests/
# Run tests with debugging and early exit
TZ=UTC CI=true npx react-scripts test tests/ --testURL http://example.com/MAAS/r --watchAll=false --verbose --runInBand --forceExit --bail
set +x

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
RUN git clone https://github.com/canonical/maas-ui.git /home/maas-ui

WORKDIR /home/maas-ui
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("canonical", "maas_ui_4766_to_unknown")
class MAAS_UI_4766_TO_UNKNOWN(Instance):
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
        passed_tests: set[str] = set() # Tests that passed successfully
        failed_tests: set[str] = set() # Tests that failed
        skipped_tests: set[str] = set() # Tests that were skipped
        import re
        # Parse passed tests
        passed_pattern = re.compile(r'\s*✓ (.*?) \(\d+ ms\)')
        passed_tests.update(passed_pattern.findall(log))
        # Parse failed tests
        failed_pattern = re.compile(r'> \d+ \| it\("(.*?)"')
        failed_tests.update(failed_pattern.findall(log))
        # TODO: Parse skipped tests (pattern not identified in sampled logs)
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
