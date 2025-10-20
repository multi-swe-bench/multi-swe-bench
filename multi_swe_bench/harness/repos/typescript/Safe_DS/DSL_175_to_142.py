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
                """ls
###ACTION_DELIMITER###
npm install
###ACTION_DELIMITER###
ls -a
###ACTION_DELIMITER###
ls .github
###ACTION_DELIMITER###
ls .github/workflows
###ACTION_DELIMITER###
cat << EOF > test_commands.sh && chmod +x test_commands.sh
#!/bin/bash

# Test DSL component
 echo "Running DSL tests..."
(cd DSL && ./gradlew check --info --continue)

# Test Runtime Runner component
 echo "Running Runtime Runner tests..."
(cd Runtime/safe-ds-runner && poetry run pytest --doctest-modules -v)

# Test Runtime Stdlib component
 echo "Running Runtime Stdlib tests..."
(cd Runtime/safe-ds && poetry run pytest --doctest-modules -v)
EOF
###ACTION_DELIMITER###
echo '#!/bin/bash' > test_commands.sh && echo '' >> test_commands.sh && echo '# Test DSL component' >> test_commands.sh && echo 'echo "Running DSL tests..."' >> test_commands.sh && echo '(cd DSL && ./gradlew check --info --continue)' >> test_commands.sh && echo '' >> test_commands.sh && echo '# Test Runtime Runner component' >> test_commands.sh && echo 'echo "Running Runtime Runner tests..."' >> test_commands.sh && echo '(cd Runtime/safe-ds-runner && poetry run pytest --doctest-modules -v)' >> test_commands.sh && echo '' >> test_commands.sh && echo '# Test Runtime Stdlib component' >> test_commands.sh && echo 'echo "Running Runtime Stdlib tests..."' >> test_commands.sh && echo '(cd Runtime/safe-ds && poetry run pytest --doctest-modules -v)' >> test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y openjdk-17-jdk
###ACTION_DELIMITER###
apt-get install -y python3.10 python3.10-pip
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python3.10 python3-pip
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3.10 && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.10 get-pip.py
###ACTION_DELIMITER###
sed -i '$ d' /etc/apt/sources.list && echo 'deb https://deb.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y -t bullseye-backports python3.10
###ACTION_DELIMITER###
sed -i '$ d' /etc/apt/sources.list && echo 'deb http://deb.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y -t bullseye-backports python3.10
###ACTION_DELIMITER###
sed -i '$ d' /etc/apt/sources.list && echo 'deb [trusted=yes] http://archive.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list && apt-get update && apt-get install -y -t bullseye-backports python3.10
###ACTION_DELIMITER###
wget http://archive.debian.org/debian/pool/main/p/python3.10/python3.10_3.10.12-1~bpo11+1_amd64.deb && dpkg -i python3.10_3.10.12-1~bpo11+1_amd64.deb && apt-get install -f -y && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.10 get-pip.py
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev tk-dev libffi-dev && wget https://www.python.org/ftp/python/3.10.14/Python-3.10.14.tgz && tar -xf Python-3.10.14.tgz && cd Python-3.10.14 && ./configure --prefix=/usr/local --enable-optimizations && make -j 4 && make install && cd .. && rm -rf Python-3.10.14* && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.10 get-pip.py
###ACTION_DELIMITER###
pip3.10 install poetry
###ACTION_DELIMITER###
cd DSL && ./gradlew build
###ACTION_DELIMITER###
ls com.larsreimann.safeds.vscode
###ACTION_DELIMITER###
sed -i 's/16.15.1/18.20.4/' com.larsreimann.safeds.vscode/build.gradle.kts
###ACTION_DELIMITER###
./gradlew build
###ACTION_DELIMITER###
sed -i 's/"@types\/node": "^16.11.41"/"@types\/node": "^18.19.0"/' com.larsreimann.safeds.vscode/package.json && sed -i 's/"vscode-languageclient": "^8.0.2"/"vscode-languageclient": "^8.10.0"/' com.larsreimann.safeds.vscode/package.json && sed -i 's/"esbuild": "^0.15.12"/"esbuild": "^0.20.2"/' com.larsreimann.safeds.vscode/package.json && sed -i 's/"typescript": "^4.8.4"/"typescript": "^5.3.3"/' com.larsreimann.safeds.vscode/package.json && echo '"vsce": "^2.26.0"' >> com.larsreimann.safeds.vscode/package.json
###ACTION_DELIMITER###
cd com.larsreimann.safeds.vscode && npm install vsce@latest && npm install && cd ..
###ACTION_DELIMITER###
sed -i '$ d' package.json && sed -i 's/"vscode-test": "^1.6.1"/"vscode-test": "^1.6.1", "vsce": "^2.26.0"/' package.json && npm install
###ACTION_DELIMITER###
sed -i 's/"vsce": "^2.26.0"/"vsce": "^2.18.0"/' package.json && npm install
###ACTION_DELIMITER###
sed -i 's/"vsce": "^2.18.0"/"@vscode\/vsce": "^2.26.0"/' package.json && npm install
###ACTION_DELIMITER###
sed -i 's/"vscode-languageclient": "^8.10.0"/"vscode-languageclient": "^8.1.0"/' package.json && npm install
###ACTION_DELIMITER###
cd ../../ && ./gradlew build
###ACTION_DELIMITER###
cd DSL && ./gradlew check
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cd .. && bash test_commands.sh
###ACTION_DELIMITER###
cd Runtime/safe-ds-runner && poetry install && cd ../../Runtime/safe-ds && poetry install && cd ../../
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash

# Test DSL component
echo "Running DSL tests..."
(cd DSL && ./gradlew check --info --continue)

# Test Runtime Runner component
echo "Running Runtime Runner tests..."
(cd Runtime/safe-ds-runner && poetry run pytest --doctest-modules -v)

# Test Runtime Stdlib component
echo "Running Runtime Stdlib tests..."
(cd Runtime/safe-ds && poetry run pytest --doctest-modules -v)

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

# Test DSL component
echo "Running DSL tests..."
(cd DSL && ./gradlew check --info --continue)

# Test Runtime Runner component
echo "Running Runtime Runner tests..."
(cd Runtime/safe-ds-runner && poetry run pytest --doctest-modules -v)

# Test Runtime Stdlib component
echo "Running Runtime Stdlib tests..."
(cd Runtime/safe-ds && poetry run pytest --doctest-modules -v)

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

# Test DSL component
echo "Running DSL tests..."
(cd DSL && ./gradlew check --info --continue)

# Test Runtime Runner component
echo "Running Runtime Runner tests..."
(cd Runtime/safe-ds-runner && poetry run pytest --doctest-modules -v)

# Test Runtime Stdlib component
echo "Running Runtime Stdlib tests..."
(cd Runtime/safe-ds && poetry run pytest --doctest-modules -v)

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
RUN git clone https://github.com/Safe-DS/DSL.git /home/DSL

WORKDIR /home/DSL
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Safe-DS", "DSL_175_to_142")
class DSL_175_TO_142(Instance):
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
        passed_matches = re.findall(r'(tests/[^:]+::[^ ]+) PASSED', log)
        for test in passed_matches:
            passed_tests.add(test)
        # Parse failed tests
        failed_matches = re.findall(r'FAILED (tests/[^:]+::[^ ]+)', log)
        for test in failed_matches:
            failed_tests.add(test)
        # Parse skipped tests (placeholder)
        skipped_matches = re.findall(r'SKIPPED (\S+)', log)
        for test in skipped_matches:
            skipped_tests.add(test)
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
