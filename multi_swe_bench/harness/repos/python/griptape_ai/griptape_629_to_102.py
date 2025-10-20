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
        return "python:3.9-slim"
    
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
                """apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl -sSL https://install.python-poetry.org | python3 -
###ACTION_DELIMITER###
export PATH="/root/.local/bin:$PATH" && poetry --version
###ACTION_DELIMITER###
poetry install --all-extras --with dev --with test
###ACTION_DELIMITER###
echo 'poetry run pytest --no-header -rA --tb=no -p no:cacheprovider -v' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
export AZURE_OPENAI_35_TURBO_DEPLOYMENT_ID=test-deployment && bash test_commands.sh
###ACTION_DELIMITER###
export AZURE_OPENAI_API_BASE=https://dummy.openai.azure.com && export AZURE_OPENAI_API_KEY=dummy-key && export AZURE_OPENAI_API_VERSION=2023-05-15 && bash test_commands.sh
###ACTION_DELIMITER###
export AZURE_OPENAI_35_TURBO_16k_DEPLOYMENT_ID=test-16k-deployment && export AZURE_OPENAI_35_TURBO_DEPLOYMENT_ID=test-deployment && export AZURE_OPENAI_API_BASE=https://dummy.openai.azure.com && export AZURE_OPENAI_API_KEY=dummy-key && export AZURE_OPENAI_API_VERSION=2023-05-15 && bash test_commands.sh
###ACTION_DELIMITER###
export AZURE_OPENAI_4_DEPLOYMENT_ID=test-4-deployment && export AZURE_OPENAI_35_TURBO_16k_DEPLOYMENT_ID=test-16k-deployment && export AZURE_OPENAI_35_TURBO_DEPLOYMENT_ID=test-deployment && export AZURE_OPENAI_API_BASE=https://dummy.openai.azure.com && export AZURE_OPENAI_API_KEY=dummy-key && export AZURE_OPENAI_API_VERSION=2023-05-15 && bash test_commands.sh
###ACTION_DELIMITER###
export AZURE_OPENAI_4_32k_DEPLOYMENT_ID=test-4-32k-deployment && export AZURE_OPENAI_4_DEPLOYMENT_ID=test-4-deployment && export AZURE_OPENAI_35_TURBO_16k_DEPLOYMENT_ID=test-16k-deployment && export AZURE_OPENAI_35_TURBO_DEPLOYMENT_ID=test-deployment && export AZURE_OPENAI_API_BASE=https://dummy.openai.azure.com && export AZURE_OPENAI_API_KEY=dummy-key && export AZURE_OPENAI_API_VERSION=2023-05-15 && bash test_commands.sh
###ACTION_DELIMITER###
export ANTHROPIC_API_KEY=dummy-key && export AZURE_OPENAI_4_32k_DEPLOYMENT_ID=test-4-32k-deployment && export AZURE_OPENAI_4_DEPLOYMENT_ID=test-4-deployment && export AZURE_OPENAI_35_TURBO_16k_DEPLOYMENT_ID=test-16k-deployment && export AZURE_OPENAI_35_TURBO_DEPLOYMENT_ID=test-deployment && export AZURE_OPENAI_API_BASE=https://dummy.openai.azure.com && export AZURE_OPENAI_API_KEY=dummy-key && export AZURE_OPENAI_API_VERSION=2023-05-15 && bash test_commands.sh
###ACTION_DELIMITER###
export COHERE_API_KEY=dummy-key && export ANTHROPIC_API_KEY=dummy-key && export AZURE_OPENAI_4_32k_DEPLOYMENT_ID=test-4-32k-deployment && export AZURE_OPENAI_4_DEPLOYMENT_ID=test-4-deployment && export AZURE_OPENAI_35_TURBO_16k_DEPLOYMENT_ID=test-16k-deployment && export AZURE_OPENAI_35_TURBO_DEPLOYMENT_ID=test-deployment && export AZURE_OPENAI_API_BASE=https://dummy.openai.azure.com && export AZURE_OPENAI_API_KEY=dummy-key && export AZURE_OPENAI_API_VERSION=2023-05-15 && bash test_commands.sh
###ACTION_DELIMITER###
export AWS_REGION=us-east-1 && export COHERE_API_KEY=dummy-key && export ANTHROPIC_API_KEY=dummy-key && export AZURE_OPENAI_4_32k_DEPLOYMENT_ID=test-4-32k-deployment && export AZURE_OPENAI_4_DEPLOYMENT_ID=test-4-deployment && export AZURE_OPENAI_35_TURBO_16k_DEPLOYMENT_ID=test-16k-deployment && export AZURE_OPENAI_35_TURBO_DEPLOYMENT_ID=test-deployment && export AZURE_OPENAI_API_BASE=https://dummy.openai.azure.com && export AZURE_OPENAI_API_KEY=dummy-key && export AZURE_OPENAI_API_VERSION=2023-05-15 && bash test_commands.sh
###ACTION_DELIMITER###
export AWS_DEFAULT_REGION=us-east-1 && export COHERE_API_KEY=dummy-key && export ANTHROPIC_API_KEY=dummy-key && export AZURE_OPENAI_4_32k_DEPLOYMENT_ID=test-4-32k-deployment && export AZURE_OPENAI_4_DEPLOYMENT_ID=test-4-deployment && export AZURE_OPENAI_35_TURBO_16k_DEPLOYMENT_ID=test-16k-deployment && export AZURE_OPENAI_35_TURBO_DEPLOYMENT_ID=test-deployment && export AZURE_OPENAI_API_BASE=https://dummy.openai.azure.com && export AZURE_OPENAI_API_KEY=dummy-key && export AZURE_OPENAI_API_VERSION=2023-05-15 && bash test_commands.sh
###ACTION_DELIMITER###
export SAGEMAKER_LLAMA_ENDPOINT_NAME=test-llama-endpoint && export AWS_DEFAULT_REGION=us-east-1 && export COHERE_API_KEY=dummy-key && export ANTHROPIC_API_KEY=dummy-key && export AZURE_OPENAI_4_32k_DEPLOYMENT_ID=test-4-32k-deployment && export AZURE_OPENAI_4_DEPLOYMENT_ID=test-4-deployment && export AZURE_OPENAI_35_TURBO_16k_DEPLOYMENT_ID=test-16k-deployment && export AZURE_OPENAI_35_TURBO_DEPLOYMENT_ID=test-deployment && export AZURE_OPENAI_API_BASE=https://dummy.openai.azure.com && export AZURE_OPENAI_API_KEY=dummy-key && export AZURE_OPENAI_API_VERSION=2023-05-15 && bash test_commands.sh
###ACTION_DELIMITER###
export SAGEMAKER_FALCON_ENDPOINT_NAME=dummy-falcon-endpoint && export SAGEMAKER_LLAMA_ENDPOINT_NAME=test-llama-endpoint && export AWS_DEFAULT_REGION=us-east-1 && export COHERE_API_KEY=dummy-key && export ANTHROPIC_API_KEY=dummy-key && export AZURE_OPENAI_4_32k_DEPLOYMENT_ID=test-4-32k-deployment && export AZURE_OPENAI_4_DEPLOYMENT_ID=test-4-deployment && export AZURE_OPENAI_35_TURBO_16k_DEPLOYMENT_ID=test-16k-deployment && export AZURE_OPENAI_35_TURBO_DEPLOYMENT_ID=test-deployment && export AZURE_OPENAI_API_BASE=https://dummy.openai.azure.com && export AZURE_OPENAI_API_KEY=dummy-key && export AZURE_OPENAI_API_VERSION=2023-05-15 && bash test_commands.sh
###ACTION_DELIMITER###
echo 'poetry run pytest tests/unit --no-header -rA --tb=no -p no:cacheprovider -v' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
poetry run pytest tests/unit --no-header -rA --tb=no -p no:cacheprovider -v

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
poetry run pytest tests/unit --no-header -rA --tb=no -p no:cacheprovider -v

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
poetry run pytest tests/unit --no-header -rA --tb=no -p no:cacheprovider -v

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

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.9-slim

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
RUN git clone https://github.com/griptape-ai/griptape.git /home/griptape

WORKDIR /home/griptape
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("griptape-ai", "griptape_629_to_102")
class GRIPTAPE_629_TO_102(Instance):
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
        # Compile regex patterns to match test cases
        pattern = re.compile(r'(tests/[^\s]+)\s+(PASSED|FAILED|SKIPPED)|(PASSED|FAILED|SKIPPED)\s+(tests/[^\s]+)')  # Simplified pattern focusing on test path and status
        # Iterate over each line in the log
        for line in log.split('\n'):
            line = line.strip()
            match = pattern.search(line)
            if match:
                # Extract test name and status from the appropriate groups
                if match.group(1) and match.group(2):
                    test_name = match.group(1)
                    status = match.group(2)
                else:
                    test_name = match.group(4)
                    status = match.group(3)
            else:
                continue  # Skip lines that don't match
            # Add test to the appropriate set
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
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
