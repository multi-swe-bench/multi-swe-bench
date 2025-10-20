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
pip install -e '.[all,dev]'
###ACTION_DELIMITER###
pip install huggingface-hub transformers
###ACTION_DELIMITER###
pytest -vv test/ --document_store_type='memory'
###ACTION_DELIMITER###
pip install -r test/test_requirements.txt
###ACTION_DELIMITER###
pip install spacy && spacy download en_core_web_trf==3.7.3
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip install spacy && spacy download en_core_web_trf==3.7.3
###ACTION_DELIMITER###
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_trf-3.7.3/en_core_web_trf-3.7.3-py3-none-any.whl
###ACTION_DELIMITER###
pip install --upgrade pip && pip install en_core_web_trf==3.8.0
###ACTION_DELIMITER###
pip install spacy==3.7.5 && spacy download en_core_web_trf==3.7.3
###ACTION_DELIMITER###
spacy download en_core_web_trf
###ACTION_DELIMITER###
echo 'pytest -vv test/ --document-store-type=memory' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -vv test/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip install openapi3 'huggingface-hub[inference]' && bash test_commands.sh
###ACTION_DELIMITER###
pip install 'huggingface-hub[inference]==0.19.4' text-generation && bash test_commands.sh
###ACTION_DELIMITER###
pip install pydantic==1.10.12 && bash test_commands.sh
###ACTION_DELIMITER###
pip install 'transformers[torch,sentencepiece]==4.37.2' && bash test_commands.sh
###ACTION_DELIMITER###
pip install 'huggingface-hub[inference]==0.24.0' text-generation && bash test_commands.sh
###ACTION_DELIMITER###
ls /usr/local/lib/python3.9/site-packages/huggingface_hub/ && pip install 'huggingface-hub[inference]==0.28.0' text-generation==0.6.0 && bash test_commands.sh
###ACTION_DELIMITER###
ls /usr/local/lib/python3.9/site-packages/huggingface_hub/inference/ && pip install 'huggingface-hub[inference]==0.19.4' 'text-generation==0.5.1' && bash test_commands.sh
###ACTION_DELIMITER###
pip install 'huggingface-hub[inference]==0.20.0' 'transformers[torch,sentencepiece]==4.37.2' 'text-generation==0.5.1' && bash test_commands.sh
###ACTION_DELIMITER###
pip install 'huggingface-hub[inference]==0.21.0' 'transformers[torch,sentencepiece]==4.37.2' 'text-generation==0.5.1' && bash test_commands.sh
###ACTION_DELIMITER###
pip install langdetect pypdf openai && bash test_commands.sh
###ACTION_DELIMITER###
pip install tika sentence-transformers && bash test_commands.sh
###ACTION_DELIMITER###
pip install 'huggingface-hub[inference]==0.24.0' text-generation && bash test_commands.sh
###ACTION_DELIMITER###
pip install 'huggingface-hub[inference]>=0.34.0' transformers==4.54.1 text-generation && bash test_commands.sh
###ACTION_DELIMITER###
pip install 'huggingface-hub[inference]==0.28.0' text-generation==0.6.0 && bash test_commands.sh
###ACTION_DELIMITER###
pip install 'huggingface-hub[inference]>=0.34.0' transformers==4.54.1 && echo 'pytest -vv test/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip install git+https://github.com/huggingface/huggingface_hub.git@main#egg=huggingface-hub[inference] && bash test_commands.sh
###ACTION_DELIMITER###
pip install 'huggingface-hub[inference]==0.25.0' && bash test_commands.sh
###ACTION_DELIMITER###
pip install 'huggingface-hub[inference]==0.34.0' && bash test_commands.sh
###ACTION_DELIMITER###
pip install 'huggingface-hub[inference]==0.24.0' && bash test_commands.sh
###ACTION_DELIMITER###
pip install 'transformers==4.37.2' 'huggingface-hub[inference]==0.24.0' && bash test_commands.sh
###ACTION_DELIMITER###
pip install 'huggingface-hub[inference]==0.24.0' 'text-generation==0.6.0' 'transformers==4.37.2' && bash test_commands.sh
###ACTION_DELIMITER###
ln -s /usr/local/lib/python3.9/site-packages/text_generation/__init__.py /usr/local/lib/python3.9/site-packages/huggingface_hub/inference/_text_generation.py && bash test_commands.sh
###ACTION_DELIMITER###
echo 'from text_generation.types import TextGenerationStreamResponse, Token, StreamDetails, FinishReason' > /usr/local/lib/python3.9/site-packages/huggingface_hub/inference/_text_generation.py && bash test_commands.sh
###ACTION_DELIMITER###
ls /usr/local/lib/python3.9/site-packages/text_generation/ && cat /usr/local/lib/python3.9/site-packages/text_generation/types.py
###ACTION_DELIMITER###
echo 'from text_generation.types import StreamResponse as TextGenerationStreamResponse, Token, StreamDetails, FinishReason' > /usr/local/lib/python3.9/site-packages/huggingface_hub/inference/_text_generation.py && bash test_commands.sh
###ACTION_DELIMITER###
echo 'from text_generation.types import Response as TextGenerationResponse, StreamResponse as TextGenerationStreamResponse, Token, StreamDetails, FinishReason' > /usr/local/lib/python3.9/site-packages/huggingface_hub/inference/_text_generation.py && bash test_commands.sh
###ACTION_DELIMITER###
pip install jsonref && bash test_commands.sh
###ACTION_DELIMITER###
pip install markdown-it-py mdit_plain && bash test_commands.sh
###ACTION_DELIMITER###
pip install azure-ai-documentintelligence && echo 'pytest -vv test/' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -vv test/

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
pytest -vv test/

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn  /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
pytest -vv test/

""".format(
                    pr=self.pr
                ),
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
RUN git clone https://github.com/deepset-ai/haystack.git /home/haystack

WORKDIR /home/haystack
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("deepset-ai", "haystack_6877_to_6497")
class HAYSTACK_6877_TO_6497(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        # Match inline results (e.g., "test/...::method PASSED [  0%]")
        inline_pattern = re.compile(r'^(test/.*?\.py::(?:\w+::)*\w+)\s+(PASSED|FAILED|SKIPPED)\s+\[\s*\d+%\]')
        # Match summary failures/skips (e.g., "FAILED test/...::method - Error")
        summary_pattern = re.compile(r'^(FAILED|SKIPPED)\s+(test/.*?\.py::(?:\w+::)*\w+)\s+-')
        for line in log.splitlines():
            line = line.strip()
            # Handle inline results
            inline_match = inline_pattern.match(line)
            if inline_match:
                test_name = inline_match.group(1)
                status = inline_match.group(2)
                if status == "PASSED":
                    passed_tests.add(test_name)
                elif status == "FAILED":
                    failed_tests.add(test_name)
                elif status == "SKIPPED":
                    skipped_tests.add(test_name)
                continue
            # Handle summary failures/skips
            summary_match = summary_pattern.match(line)
            if summary_match:
                status = summary_match.group(1)
                test_name = summary_match.group(2)
                if status == "FAILED":
                    failed_tests.add(test_name)
                elif status == "SKIPPED":
                    skipped_tests.add(test_name)
                continue
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
