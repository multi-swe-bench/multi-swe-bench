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
apt-get update && apt-get install -y postgresql postgresql-contrib
###ACTION_DELIMITER###
pg_ctlcluster 15 main start
###ACTION_DELIMITER###
yarn
###ACTION_DELIMITER###
cp .env.example .env && sed -i "s/^NEXTAUTH_SECRET=.*/NEXTAUTH_SECRET=$(openssl rand -base64 32)/" .env && sed -i "s/^CALENDSO_ENCRYPTION_KEY=.*/CALENDSO_ENCRYPTION_KEY=$(openssl rand -base64 32)/" .env
###ACTION_DELIMITER###
cp .env.example .env && sed -i "s|^NEXTAUTH_SECRET=.*|NEXTAUTH_SECRET=$(openssl rand -base64 32)|" .env && sed -i "s|^CALENDSO_ENCRYPTION_KEY=.*|CALENDSO_ENCRYPTION_KEY=$(openssl rand -base64 32)|" .env
###ACTION_DELIMITER###
sudo -u postgres createdb calcom && sudo -u postgres psql -c "CREATE USER calcom WITH PASSWORD 'calcom';" && sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE calcom TO calcom;"
###ACTION_DELIMITER###
su - postgres -c 'createdb calcom' && su - postgres -c 'psql -c "CREATE USER calcom WITH PASSWORD \'calcom\';"' && su - postgres -c 'psql -c "GRANT ALL PRIVILEGES ON DATABASE calcom TO calcom;"'
###ACTION_DELIMITER###
su - postgres -c "createdb calcom && psql -c \"CREATE USER calcom WITH PASSWORD 'calcom';\" && psql -c \"GRANT ALL PRIVILEGES ON DATABASE calcom TO calcom;\""
###ACTION_DELIMITER###
sed -i "s|^DATABASE_URL=.*|DATABASE_URL=postgresql://calcom:calcom@localhost:5432/calcom|" .env
###ACTION_DELIMITER###
yarn prisma migrate dev --name init
###ACTION_DELIMITER###
sed -i "s|^DATABASE_URL=.*|DATABASE_URL=postgresql://calcom:calcom@localhost:5432/calcom|" .env
###ACTION_DELIMITER###
yarn prisma migrate dev --name init
###ACTION_DELIMITER###
find . -name 'schema.prisma'
###ACTION_DELIMITER###
sed -i "s|^DATABASE_DIRECT_URL=.*|DATABASE_DIRECT_URL=postgresql://calcom:calcom@localhost:5432/calcom|" .env
###ACTION_DELIMITER###
yarn prisma migrate dev --name init
###ACTION_DELIMITER###
su - postgres -c "psql -c \"ALTER USER calcom CREATEDB;\""
###ACTION_DELIMITER###
yarn prisma migrate dev --name init
###ACTION_DELIMITER###
su - postgres -c "psql -d calcom -c \"GRANT USAGE, CREATE ON SCHEMA public TO calcom;\""
###ACTION_DELIMITER###
yarn prisma migrate dev --name init
###ACTION_DELIMITER###
cat package.json
###ACTION_DELIMITER###
echo 'yarn vitest run --verbose --reporter json' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'yarn vitest run --reporter json' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
yarn vitest run --reporter json

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
yarn vitest run --reporter json

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
yarn vitest run --reporter json

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


@Instance.register("calcom", "cal_com_14272_to_unknown")
class CAL_COM_14272_TO_UNKNOWN(Instance):
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
        # Implement the log parsing logic here
        # Extract JSON part from log (skip leading non-JSON lines)
        lines = log.split('\n')
        json_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                json_start = i
                break
        if json_start is None:
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
