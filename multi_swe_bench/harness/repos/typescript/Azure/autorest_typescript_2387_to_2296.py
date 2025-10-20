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
        return "node:18-bookworm"
    
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
                """ls
###ACTION_DELIMITER###
rush help test
###ACTION_DELIMITER###
npm install -g @microsoft/rush
###ACTION_DELIMITER###
rush install
###ACTION_DELIMITER###
rush test --help
###ACTION_DELIMITER###
echo 'rush test --verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'rush test --verbose --except @msinternal/typespec-test' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'rush test -t @autorest/typescript -t @azure-tools/rlc-common -t @azure-tools/typespec-ts --verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
cd packages/autorest.typescript && npm test --verbose && cd -\ncd packages/rlc-common && npm run unit-test --verbose && cd -\ncd packages/typespec-ts && npm test --verbose && cd -' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls packages
###ACTION_DELIMITER###
echo -e '#!/bin/bash
rush link
npm --prefix packages/autorest.typescript test --verbose
npm --prefix packages/rlc-common run unit-test --verbose
npm --prefix packages/typespec-ts test --verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pnpm install
pnpm --prefix packages/autorest.typescript test --verbose
pnpm --prefix packages/rlc-common run unit-test --verbose
pnpm --prefix packages/typespec-ts test --verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
./common/temp/pnpm-local/pnpm install
./common/temp/pnpm-local/pnpm --prefix packages/autorest.typescript test --verbose
./common/temp/pnpm-local/pnpm --prefix packages/rlc-common run unit-test --verbose
./common/temp/pnpm-local/pnpm --prefix packages/typespec-ts test --verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
npm install
npm --prefix packages/autorest.typescript test --verbose
npm --prefix packages/rlc-common run unit-test --verbose
npm --prefix packages/typespec-ts test --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
rush install
cd packages/autorest.typescript && rushx test --verbose && cd -
cd packages/rlc-common && rushx unit-test --verbose && cd -
cd packages/typespec-ts && rushx test --verbose && cd -' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
rush install
(cd packages/autorest.typescript && rushx test --verbose)
(cd packages/rlc-common && rushx unit-test --verbose)
(cd packages/typespec-ts && rushx test --verbose)' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
rush install
rush test --only @autorest/typescript --only @azure-tools/rlc-common --only @azure-tools/typespec-ts --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
rush install
rush test --verbose -T @msinternal/typespec-test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
rush install
rush test --only @autorest/typescript --only @azure-tools/rlc-common --only @azure-tools/typespec-ts -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
rush install
rush test -T @msinternal/typespec-test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
rush install
rush test --only @autorest/typescript --only @azure-tools/rlc-common --only @azure-tools/typespec-ts -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
rush install
rush test -T @msinternal/typespec-test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
rush install
rush test -T @msinternal/typespec-test -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
rush install
cd packages/autorest.typescript && rushx test --verbose && cd -
cd packages/rlc-common && rushx unit-test --verbose && cd -
cd packages/typespec-ts && rushx test --verbose && cd -' > test_commands.sh
###ACTION_DELIMITER###
echo -e '#!/bin/bash
rush install
(cd packages/autorest.typescript && rushx test --verbose)
(cd packages/rlc-common && rushx unit-test --verbose)
(cd packages/typespec-ts && rushx test --verbose)' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
rush install
(cd packages/autorest.typescript && rushx test --verbose)
(cd packages/rlc-common && rushx unit-test --verbose)
(cd packages/typespec-ts && rushx test --verbose)

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
rush install
(cd packages/autorest.typescript && rushx test --verbose)
(cd packages/rlc-common && rushx unit-test --verbose)
(cd packages/typespec-ts && rushx test --verbose)

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
rush install
(cd packages/autorest.typescript && rushx test --verbose)
(cd packages/rlc-common && rushx unit-test --verbose)
(cd packages/typespec-ts && rushx test --verbose)

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

# Choose an appropriate base image based on the project's requirements - replace node:18-bookworm with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM node:18-bookworm

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
RUN git clone https://github.com/Azure/autorest.typescript.git /home/autorest.typescript

WORKDIR /home/autorest.typescript
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Azure", "autorest_typescript_2387_to_2296")
class AUTOREST_TYPESCRIPT_2387_TO_2296(Instance):
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
        # Pattern for passed tests: lines with ✔ followed by test name
        passed_pattern = re.compile(r'^\s*✔\s+(.*)$', re.MULTILINE)
        passed_tests.update(passed_pattern.findall(log))
        # Pattern for failed tests: lines with [number]) followed by test name
        failed_pattern = re.compile(r'^\s*\d+\)\s+(.*)$', re.MULTILINE)
        failed_tests.update(failed_pattern.findall(log))
        # Pattern for skipped tests: lines with − followed by test name (Mocha pending tests)
        skipped_pattern = re.compile(r'^\s*−\s+(.*)$', re.MULTILINE)
        skipped_tests.update(skipped_pattern.findall(log))
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
