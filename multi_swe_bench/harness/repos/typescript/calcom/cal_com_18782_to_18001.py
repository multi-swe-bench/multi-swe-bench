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
apt-get update
###ACTION_DELIMITER###
apt-get install -y postgresql
###ACTION_DELIMITER###
service postgresql start
###ACTION_DELIMITER###
echo -e '#!/bin/bash

yarn test -- --verbose

yarn e2e -- --verbose' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
yarn --version || npm install -g yarn
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
sudo -u postgres psql -c "CREATE DATABASE calendso;"
###ACTION_DELIMITER###
su postgres -c 'psql -c "CREATE DATABASE calendso;"'
###ACTION_DELIMITER###
cp .env.example .env
###ACTION_DELIMITER###
sed -i 's/DATABASE_URL=.*/DATABASE_URL=postgresql:\/\/postgres@localhost:5432\/calendso?schema=public/' .env
###ACTION_DELIMITER###
yarn prisma migrate deploy
###ACTION_DELIMITER###
cat .env | grep DATABASE_URL
###ACTION_DELIMITER###
ls packages
###ACTION_DELIMITER###
ls packages/prisma
###ACTION_DELIMITER###
sed -i 's/DATABASE_DIRECT_URL=.*/DATABASE_DIRECT_URL=postgresql:\/\/postgres@localhost:5432\/calendso?schema=public/' .env
###ACTION_DELIMITER###
yarn prisma migrate deploy
###ACTION_DELIMITER###
sed -i 's/local   all             postgres                                peer/local   all             postgres                                trust/' /etc/postgresql/15/main/pg_hba.conf && service postgresql restart
###ACTION_DELIMITER###
yarn prisma migrate deploy
###ACTION_DELIMITER###
cat /etc/postgresql/15/main/pg_hba.conf | grep 'postgres'
###ACTION_DELIMITER###
psql -U postgres -d calendso -c 'SELECT 1;'
###ACTION_DELIMITER###
sed -i 's/localhost/127.0.0.1/g' .env
###ACTION_DELIMITER###
psql -U postgres -c "ALTER USER postgres PASSWORD 'password';" && sed -i 's/postgres@/postgres:password@/g' .env
###ACTION_DELIMITER###
cat .env | grep DATABASE_URL
###ACTION_DELIMITER###
echo 'DATABASE_DIRECT_URL=$(grep DATABASE_URL .env | cut -d'=' -f2)' >> .env
###ACTION_DELIMITER###
yarn prisma migrate deploy
###ACTION_DELIMITER###
sed -i '/DATABASE_DIRECT_URL/d' .env && echo 'DATABASE_DIRECT_URL=$(grep ^DATABASE_URL .env | cut -d= -f2)' >> .env
###ACTION_DELIMITER###
sed -i '/DATABASE_DIRECT_URL/d' .env && grep '^DATABASE_URL' .env | sed 's/DATABASE_URL/DATABASE_DIRECT_URL/' >> .env
###ACTION_DELIMITER###
yarn prisma migrate deploy
###ACTION_DELIMITER###
yarn prisma db seed
###ACTION_DELIMITER###
bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash

yarn test -- --verbose

yarn e2e -- --verbose

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

yarn test -- --verbose

yarn e2e -- --verbose

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

yarn test -- --verbose

yarn e2e -- --verbose

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

# Choose an appropriate base image based on the project's requirements - replace node:20-bookworm with actual base image
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
RUN git clone https://github.com/calcom/cal.com.git /home/cal.com

WORKDIR /home/cal.com
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("calcom", "cal_com_18782_to_18001")
class CAL_COM_18782_TO_18001(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        import json

        # Extract individual test names from stdout lines and determine status by checking subsequent lines
        test_name_pattern = re.compile(r"stdout \| (.*)")
        lines = log.split("\n")
        for match in test_name_pattern.finditer(log):
            full_test_name = match.group(1)
            # Find the line number of the stdout line
            line_num = -1
            for i, line in enumerate(lines):
                if f"stdout | {full_test_name}" in line:
                    line_num = i
                    break
            if line_num == -1:
                continue
            # Check next 5 lines for ERROR or SKIPPED
            has_error = False
            is_skipped = False
            for j in range(line_num + 1, min(line_num + 6, len(lines))):
                if re.search(r"\[ERROR[^]]*\]", lines[j], re.IGNORECASE):
                    has_error = True
                    break
                if "SKIPPED" in lines[j]:
                    is_skipped = True
                    break
            if is_skipped:
                skipped_tests.add(full_test_name)
            elif has_error:
                failed_tests.add(full_test_name)
            else:
                passed_tests.add(full_test_name)
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
