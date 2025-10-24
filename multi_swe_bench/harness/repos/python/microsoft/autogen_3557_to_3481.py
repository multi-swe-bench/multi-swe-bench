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
        return "python:3.10-slim"

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
                """ls -la /home/autogen
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
pip install -e ".[test]"
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --asyncio-mode=auto ./test' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
tail -n +5 OAI_CONFIG_LIST_sample > notebook/OAI_CONFIG_LIST
###ACTION_DELIMITER###
python -m json.tool notebook/OAI_CONFIG_LIST
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install llama-index
###ACTION_DELIMITER###
pip install sentence-transformers
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install llama-index-agent
###ACTION_DELIMITER###
pip install llama-index-agent-runner
###ACTION_DELIMITER###
pip install llama-index==0.10.0
###ACTION_DELIMITER###
pip install 'llama-index[agent]'
###ACTION_DELIMITER###
pip install --upgrade llama-index
###ACTION_DELIMITER###
pip install llama-index-agents
###ACTION_DELIMITER###
pip install llama-index==0.13.6
###ACTION_DELIMITER###
pip install llama-index-agent-react
###ACTION_DELIMITER###
pip install git+https://github.com/run-llama/llama_index.git@v0.13.6#egg=llama-index-core
###ACTION_DELIMITER###
pip install llama-index-core==0.10.0
###ACTION_DELIMITER###
pip install llama-index-core==0.13.6
###ACTION_DELIMITER###
pip install --force-reinstall llama-index-core==0.13.6
###ACTION_DELIMITER###
pip install llama-index-agent-openai
###ACTION_DELIMITER###
pip uninstall -y llama-index llama-index-core llama-index-llms-openai llama-index-embeddings-openai llama-index-agent-openai && pip install llama-index==0.10.0 llama-index-core==0.10.0
###ACTION_DELIMITER###
pip uninstall -y llama-index llama-index-core && pip install llama-index==0.10.0 llama-index-core==0.10.0
###ACTION_DELIMITER###
pip install llama-index-agent
###ACTION_DELIMITER###
pip install llama-index-core==0.11.0
###ACTION_DELIMITER###
pip install llama-index-core==0.13.0
###ACTION_DELIMITER###
pip install 'llama-index[agent]==0.13.0'
###ACTION_DELIMITER###
pip install llama-index-agents
###ACTION_DELIMITER###
pip uninstall -y llama-index llama-index-core llama-index-llms-openai llama-index-embeddings-openai llama-index-agent-openai && pip install llama-index-core==0.13.6 && pip install -e ".[test, retrievechat]"
###ACTION_DELIMITER###
pip install --force-reinstall llama-index-core==0.13.6 && pip install -e ".[test, retrievechat]"
###ACTION_DELIMITER###
pip install llama-index==0.13.6 llama-index-core==0.13.6 && bash test_commands.sh
###ACTION_DELIMITER###
pip install llama-index-core==0.10.68.post1 && bash test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pytest -v --no-header -rA --asyncio-mode=auto ./test

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
pytest -v --no-header -rA --asyncio-mode=auto ./test

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
pytest -v --no-header -rA --asyncio-mode=auto ./test

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

# Choose an appropriate base image based on the project's requirements - replace python:3.10-slim with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.10-slim

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
RUN git clone https://github.com/microsoft/autogen.git /home/autogen

WORKDIR /home/autogen
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("microsoft", "autogen_3557_to_3481")
class AUTOGEN_3557_TO_3481(Instance):
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
        passed_tests: set[str] = set()
        failed_tests: set[str] = set()
        skipped_tests: set[str] = set()
        import re
        import json

        # Pattern to match test lines with their status
        pattern = re.compile(
            r"(test/[^ ]+) (PASSED|FAILED|SKIPPED)|(PASSED|FAILED|SKIPPED) (test/[^ ]+)",
            re.MULTILINE,
        )
        matches = pattern.findall(log)
        for match in matches:
            test1, status1, status2, test2 = match
            if test1 and status1:
                test_name = test1
                status = status1
            elif status2 and test2:
                test_name = test2
                status = status2
            else:
                continue
            if status == "PASSED":
                passed_tests.add(test_name)
            elif status == "FAILED":
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
