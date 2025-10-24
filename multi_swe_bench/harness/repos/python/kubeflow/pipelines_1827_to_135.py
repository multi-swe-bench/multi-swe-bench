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
        return "ubuntu:latest"

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
wget https://dl.google.com/go/go1.11.4.linux-amd64.tar.gz && tar -C /usr/local -xzf go1.11.4.linux-amd64.tar.gz && export PATH=$PATH:/usr/local/go/bin
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget https://dl.google.com/go/go1.11.4.linux-amd64.tar.gz && tar -C /usr/local -xzf go1.11.4.linux-amd64.tar.gz && export PATH=$PATH:/usr/local/go/bin
###ACTION_DELIMITER###
export PATH=$PATH:/usr/local/go/bin && go version
###ACTION_DELIMITER###
wget -O install.sh "https://github.com/bazelbuild/bazel/releases/download/0.23.0/bazel-0.23.0-installer-linux-x86_64.sh" && chmod +x install.sh && ./install.sh --user && rm -f install.sh && export PATH=$PATH:~/bin
###ACTION_DELIMITER###
apt-get install -y unzip
###ACTION_DELIMITER###
wget -O install.sh "https://github.com/bazelbuild/bazel/releases/download/0.23.0/bazel-0.23.0-installer-linux-x86_64.sh" && chmod +x install.sh && ./install.sh --user && rm -f install.sh && export PATH=$PATH:~/bin
###ACTION_DELIMITER###
export PATH=$PATH:~/bin && bazel version
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && nvm install 11.8.0 && nvm use 11.8.0 && npm i -g npm@latest
###ACTION_DELIMITER###
apt-get install -y curl
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && nvm install 11.8.0 && nvm use 11.8.0 && npm i -g npm@latest
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && nvm install 11.8.0 && nvm use 11.8.0
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip python2 python2-pip
###ACTION_DELIMITER###
apt-get install -y python3 python3-pip build-essential
###ACTION_DELIMITER###
cd frontend && npm install
###ACTION_DELIMITER###
cd /home/pipelines && cat << EOF > test_commands.sh
#!/bin/bash
set -e

# Frontend tests
cd frontend
npm run test:coveralls
cd ..

# Backend tests
cd backend/src
bazel test --test_output=all --define=grpc_no_ares=true //backend/...
cd ../../

# Python SDK tests
cd sdk/python
python3 setup.py install
python3 tests/dsl/main.py
python3 tests/compiler/main.py
./tests/run_tests.sh
cd ../../

# Visualization tests
cd backend/src/apiserver/visualization
pip3 install -r requirements-test.txt
python3 test_exporter.py
python3 test_server.py
cd ../../../../../

# Component SDK tests
cd components/gcp/container/component_sdk/python
./run_test.sh
cd ../../../../../

# Test loading all components
./components/test_load_all_components.sh
EOF && chmod +x test_commands.sh
###ACTION_DELIMITER###
cd /home/pipelines && cat << EOF > test_commands.sh
#!/bin/bash
set -e

# Frontend tests
cd frontend
npm run test:coveralls
cd ..

# Backend tests
cd backend/src
bazel test --test_output=all --define=grpc_no_ares=true //backend/...
cd ../../

# Python SDK tests
cd sdk/python
python3 tests/dsl/main.py
python3 tests/compiler/main.py
./tests/run_tests.sh
cd ../../

# Visualization tests
cd backend/src/apiserver/visualization
python3 test_exporter.py
python3 test_server.py
cd ../../../../../

# Component SDK tests
cd components/gcp/container/component_sdk/python
./run_test.sh
cd ../../../../../

# Test loading all components
./components/test_load_all_components.sh
EOF && chmod +x test_commands.sh
###ACTION_DELIMITER###
cd /home/pipelines && echo '#!/bin/bash' > test_commands.sh && echo 'set -e' >> test_commands.sh && echo '' >> test_commands.sh && echo '# Frontend tests' >> test_commands.sh && echo 'cd frontend' >> test_commands.sh && echo 'npm run test:coveralls' >> test_commands.sh && echo 'cd ..' >> test_commands.sh && echo '' >> test_commands.sh && echo '# Backend tests' >> test_commands.sh && echo 'cd backend/src' >> test_commands.sh && echo 'bazel test --test_output=all --define=grpc_no_ares=true //backend/...' >> test_commands.sh && echo 'cd ../../' >> test_commands.sh && echo '' >> test_commands.sh && echo '# Python SDK tests' >> test_commands.sh && echo 'cd sdk/python' >> test_commands.sh && echo 'python3 tests/dsl/main.py' >> test_commands.sh && echo 'python3 tests/compiler/main.py' >> test_commands.sh && echo './tests/run_tests.sh' >> test_commands.sh && echo 'cd ../../' >> test_commands.sh && echo '' >> test_commands.sh && echo '# Visualization tests' >> test_commands.sh && echo 'cd backend/src/apiserver/visualization' >> test_commands.sh && echo 'python3 test_exporter.py' >> test_commands.sh && echo 'python3 test_server.py' >> test_commands.sh && echo 'cd ../../../../' >> test_commands.sh && echo '' >> test_commands.sh && echo '# Component SDK tests' >> test_commands.sh && echo 'cd components/gcp/container/component_sdk/python' >> test_commands.sh && echo './run_test.sh' >> test_commands.sh && echo 'cd ../../../../' >> test_commands.sh && echo '' >> test_commands.sh && echo '# Test loading all components' >> test_commands.sh && echo './components/test_load_all_components.sh' >> test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
ls -l /home/pipelines/test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
set -e

# Frontend tests
cd frontend
npm run test:coveralls
cd ..

# Backend tests
cd backend/src
bazel test --test_output=all --define=grpc_no_ares=true //backend/...
cd ../../

# Python SDK tests
cd sdk/python
python3 tests/dsl/main.py
python3 tests/compiler/main.py
./tests/run_tests.sh
cd ../../

# Visualization tests
cd backend/src/apiserver/visualization
python3 test_exporter.py
python3 test_server.py
cd ../../../../

# Component SDK tests
cd components/gcp/container/component_sdk/python
./run_test.sh
cd ../../../../

# Test loading all components
./components/test_load_all_components.sh

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
set -e

# Frontend tests
cd frontend
npm run test:coveralls
cd ..

# Backend tests
cd backend/src
bazel test --test_output=all --define=grpc_no_ares=true //backend/...
cd ../../

# Python SDK tests
cd sdk/python
python3 tests/dsl/main.py
python3 tests/compiler/main.py
./tests/run_tests.sh
cd ../../

# Visualization tests
cd backend/src/apiserver/visualization
python3 test_exporter.py
python3 test_server.py
cd ../../../../

# Component SDK tests
cd components/gcp/container/component_sdk/python
./run_test.sh
cd ../../../../

# Test loading all components
./components/test_load_all_components.sh

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
set -e

# Frontend tests
cd frontend
npm run test:coveralls
cd ..

# Backend tests
cd backend/src
bazel test --test_output=all --define=grpc_no_ares=true //backend/...
cd ../../

# Python SDK tests
cd sdk/python
python3 tests/dsl/main.py
python3 tests/compiler/main.py
./tests/run_tests.sh
cd ../../

# Visualization tests
cd backend/src/apiserver/visualization
python3 test_exporter.py
python3 test_server.py
cd ../../../../

# Component SDK tests
cd components/gcp/container/component_sdk/python
./run_test.sh
cd ../../../../

# Test loading all components
./components/test_load_all_components.sh

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

# Choose an appropriate base image based on the project's requirements - replace ubuntu:latest with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:latest

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
RUN git clone https://github.com/kubeflow/pipelines.git /home/pipelines

WORKDIR /home/pipelines
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("kubeflow", "pipelines_1827_to_135")
class PIPELINES_1827_TO_135(Instance):
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

        # Parse log lines to extract test statuses
        lines = log.split("\n")
        pattern = re.compile(r"^(PASS|FAIL|SKIPPED)\s+([^\(]+)")
        for line in lines:
            stripped_line = line.strip()
            match = pattern.match(stripped_line)
            if match:
                status = match.group(1)
                test_name = match.group(2).strip()
                if status == "PASS":
                    passed_tests.add(test_name)
                elif status == "FAIL":
                    failed_tests.add(test_name)
                elif status == "SKIPPED":
                    skipped_tests.add(test_name)
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
