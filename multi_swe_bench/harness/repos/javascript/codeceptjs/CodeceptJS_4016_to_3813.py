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
                """npm install
###ACTION_DELIMITER###
echo -e '#!/bin/bash
mocha test/unit --recursive --timeout 10000 --verbose --reporter json
mocha test/runner --recursive --timeout 10000 --verbose --reporter json' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
# Start required test services
npm run json-server &
JSON_SERVER_PID=$!
npm run json-server:graphql &
GRAPHQL_SERVER_PID=$!
# Run tests with verbose and JSON reporter
npm test -- --verbose --reporter json
# Stop services
kill $JSON_SERVER_PID $GRAPHQL_SERVER_PID' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
# Start test services
npm run json-server &
JSON_SERVER_PID=$!
npm run json-server:graphql &
GRAPHQL_SERVER_PID=$!
# Wait for services to initialize
sleep 5
# Run unit tests with verbose and JSON reporter
mocha test/unit --recursive --timeout 10000 --verbose --reporter json
# Run runner tests with verbose and JSON reporter
mocha test/runner --recursive --timeout 10000 --verbose --reporter json
# Stop services
kill $JSON_SERVER_PID $GRAPHQL_SERVER_PID' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
# Start test services
npm run json-server &
JSON_SERVER_PID=$!
npm run json-server:graphql &
GRAPHQL_SERVER_PID=$!
# Wait for services to initialize
sleep 5
# Run unit tests with verbose and JSON reporter
npx mocha test/unit --recursive --timeout 10000 --verbose --reporter json
# Run runner tests with verbose and JSON reporter
npx mocha test/runner --recursive --timeout 10000 --verbose --reporter json
# Stop services
kill $JSON_SERVER_PID $GRAPHQL_SERVER_PID' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash

cleanup() {
  if [ -n "$JSON_SERVER_PID" ]; then
    kill $JSON_SERVER_PID 2>/dev/null
    wait $JSON_SERVER_PID 2>/dev/null
  fi
  if [ -n "$GRAPHQL_SERVER_PID" ]; then
    kill $GRAPHQL_SERVER_PID 2>/dev/null
    wait $GRAPHQL_SERVER_PID 2>/dev/null
  fi
  lsof -ti:8010 | xargs kill -9 2>/dev/null
  lsof -ti:8020 | xargs kill -9 2>/dev/null
}

trap cleanup EXIT

# Kill existing processes on required ports
lsof -ti:8010 | xargs kill -9 2>/dev/null
lsof -ti:8020 | xargs kill -9 2>/dev/null

# Start test services
npm run json-server &
JSON_SERVER_PID=$!
npm run json-server:graphql &
GRAPHQL_SERVER_PID=$!

# Wait for services to initialize
sleep 5

# Verify services are running
if ! lsof -i:8010; then
  echo "json-server failed to start" >&2
  exit 1
fi
if ! lsof -i:8020; then
  echo "json-server:graphql failed to start" >&2
  exit 1
fi

# Run tests with verbose and JSON reporter
npx mocha test/unit --recursive --timeout 10000 --verbose --reporter json
npx mocha test/runner --recursive --timeout 10000 --verbose --reporter json' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y lsof
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash

cleanup() {
  if [ -n "$JSON_SERVER_PID" ]; then
    kill $JSON_SERVER_PID 2>/dev/null
    wait $JSON_SERVER_PID 2>/dev/null
  fi
  if [ -n "$GRAPHQL_SERVER_PID" ]; then
    kill $GRAPHQL_SERVER_PID 2>/dev/null
    wait $GRAPHQL_SERVER_PID 2>/dev/null
  fi
  lsof -ti:8010 | xargs kill -9 2>/dev/null
  lsof -ti:8020 | xargs kill -9 2>/dev/null
}

trap cleanup EXIT

# Kill existing processes on required ports
lsof -ti:8010 | xargs kill -9 2>/dev/null
lsof -ti:8020 | xargs kill -9 2>/dev/null

# Start test services
npm run json-server &
JSON_SERVER_PID=$!
npm run json-server:graphql &
GRAPHQL_SERVER_PID=$!

# Wait for services to initialize
sleep 5

# Verify services are running
if ! lsof -i:8010; then
  echo "json-server failed to start" >&2
  exit 1
fi
if ! lsof -i:8020; then
  echo "json-server:graphql failed to start" >&2
  exit 1
fi

# Run tests with verbose and JSON reporter
npx mocha test/unit --recursive --timeout 10000 --verbose --reporter json
npx mocha test/runner --recursive --timeout 10000 --verbose --reporter json

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

cleanup() {
  if [ -n "$JSON_SERVER_PID" ]; then
    kill $JSON_SERVER_PID 2>/dev/null
    wait $JSON_SERVER_PID 2>/dev/null
  fi
  if [ -n "$GRAPHQL_SERVER_PID" ]; then
    kill $GRAPHQL_SERVER_PID 2>/dev/null
    wait $GRAPHQL_SERVER_PID 2>/dev/null
  fi
  lsof -ti:8010 | xargs kill -9 2>/dev/null
  lsof -ti:8020 | xargs kill -9 2>/dev/null
}

trap cleanup EXIT

# Kill existing processes on required ports
lsof -ti:8010 | xargs kill -9 2>/dev/null
lsof -ti:8020 | xargs kill -9 2>/dev/null

# Start test services
npm run json-server &
JSON_SERVER_PID=$!
npm run json-server:graphql &
GRAPHQL_SERVER_PID=$!

# Wait for services to initialize
sleep 5

# Verify services are running
if ! lsof -i:8010; then
  echo "json-server failed to start" >&2
  exit 1
fi
if ! lsof -i:8020; then
  echo "json-server:graphql failed to start" >&2
  exit 1
fi

# Run tests with verbose and JSON reporter
npx mocha test/unit --recursive --timeout 10000 --verbose --reporter json
npx mocha test/runner --recursive --timeout 10000 --verbose --reporter json

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

cleanup() {
  if [ -n "$JSON_SERVER_PID" ]; then
    kill $JSON_SERVER_PID 2>/dev/null
    wait $JSON_SERVER_PID 2>/dev/null
  fi
  if [ -n "$GRAPHQL_SERVER_PID" ]; then
    kill $GRAPHQL_SERVER_PID 2>/dev/null
    wait $GRAPHQL_SERVER_PID 2>/dev/null
  fi
  lsof -ti:8010 | xargs kill -9 2>/dev/null
  lsof -ti:8020 | xargs kill -9 2>/dev/null
}

trap cleanup EXIT

# Kill existing processes on required ports
lsof -ti:8010 | xargs kill -9 2>/dev/null
lsof -ti:8020 | xargs kill -9 2>/dev/null

# Start test services
npm run json-server &
JSON_SERVER_PID=$!
npm run json-server:graphql &
GRAPHQL_SERVER_PID=$!

# Wait for services to initialize
sleep 5

# Verify services are running
if ! lsof -i:8010; then
  echo "json-server failed to start" >&2
  exit 1
fi
if ! lsof -i:8020; then
  echo "json-server:graphql failed to start" >&2
  exit 1
fi

# Run tests with verbose and JSON reporter
npx mocha test/unit --recursive --timeout 10000 --verbose --reporter json
npx mocha test/runner --recursive --timeout 10000 --verbose --reporter json

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
RUN git clone https://github.com/codeceptjs/CodeceptJS.git /home/CodeceptJS

WORKDIR /home/CodeceptJS
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("codeceptjs", "CodeceptJS_4016_to_3813")
class CODECEPTJS_4016_TO_3813(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re
        import json

        # Regex pattern to capture test cases with fullTitle and err fields
        pattern = re.compile(
            r'"title":\s*"[^"]+",\s*'
            r'"fullTitle":\s*"([^"]+)",\s*'
            r'"file":\s*"[^"]+",\s*'
            r'"duration":\s*\d+,\s*'
            r'"currentRetry":\s*\d+,\s*'
            r'(?:"speed":\s*"[^"]+",\s*)?'  # Optional speed field
            r'"err":\s*(\{.*?\})',
            re.DOTALL,
        )
        # Find all matches in the log content
        matches = pattern.findall(log)
        for full_title, err in matches:
            # Check if the test is marked as skipped (based on fullTitle)
            if "skip" in full_title.lower():
                skipped_tests.add(full_title)
            else:
                # Determine if the test passed or failed based on err field
                if err.strip() == "{}":
                    passed_tests.add(full_title)
                else:
                    failed_tests.add(full_title)
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
