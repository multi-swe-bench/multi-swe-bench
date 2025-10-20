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
                """apt-get update && apt-get install -y libsndfile1 ffmpeg
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
venv/bin/pip install -e .
###ACTION_DELIMITER###
venv/bin/pip install -e ".[test]"
###ACTION_DELIMITER###
venv/bin/pip install pytest
###ACTION_DELIMITER###
echo -e '#!/bin/bash
venv/bin/pytest -v test/' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install -e ".[audio,tracing,openapi,embedders,generators]"
###ACTION_DELIMITER###
venv/bin/pip install torch openapi3 huggingface-hub transformers ddtrace opentelemetry-api opentelemetry-sdk flaky
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install isort huggingface-hub==0.20.0 ddtrace==1.15.0
###ACTION_DELIMITER###
venv/bin/pip install isort huggingface-hub==0.19.0 ddtrace==1.20.0
###ACTION_DELIMITER###
apt-get install -y build-essential
###ACTION_DELIMITER###
venv/bin/pip install isort huggingface-hub==0.19.0 ddtrace==1.20.0
###ACTION_DELIMITER###
apt-get install -y python3.12-dev
###ACTION_DELIMITER###
venv/bin/pip install isort huggingface-hub==0.19.0 ddtrace==1.20.0
###ACTION_DELIMITER###
venv/bin/pip install huggingface-hub==0.34.0
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install toml huggingface-hub==0.39.0
###ACTION_DELIMITER###
venv/bin/pip install toml huggingface-hub==0.34.3
###ACTION_DELIMITER###
sed -i 's/venv\/bin\/pytest -v test\//venv\/bin\/pytest -v test\/ --ignore=test\/components\/generators\/chat\/test_hugging_face_tgi.py --ignore=test\/components\/generators\/test_hugging_face_tgi.py/' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
venv/bin/pip install pyproject-parser
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
venv/bin/pytest -v test/ --ignore=test/components/generators/chat/test_hugging_face_tgi.py --ignore=test/components/generators/test_hugging_face_tgi.py

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
#!/bin/bash
venv/bin/pytest -v test/ --ignore=test/components/generators/chat/test_hugging_face_tgi.py --ignore=test/components/generators/test_hugging_face_tgi.py

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
#!/bin/bash
venv/bin/pytest -v test/ --ignore=test/components/generators/chat/test_hugging_face_tgi.py --ignore=test/components/generators/test_hugging_face_tgi.py

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
RUN git clone https://github.com/deepset-ai/haystack.git /home/haystack

WORKDIR /home/haystack
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("deepset-ai", "haystack_7319_to_6888")
class HAYSTACK_7319_TO_6888(Instance):
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
        passed_tests: set[str] = set()
        failed_tests: set[str] = set()
        skipped_tests: set[str] = set()
        import re
        import json
        # Regex patterns to match test lines and error lines
        test_pattern = re.compile(r'^(.+?)\s+(PASSED|FAILED|SKIPPED)\s+\[\s*\d+%\s*\]$')
        error_pattern = re.compile(r'^ERROR\s+(.+)$')
        for line in log.splitlines():
            line = line.strip()
            # Check for PASSED/FAILED/SKIPPED tests
            match = test_pattern.match(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status == 'FAILED':
                    failed_tests.add(test_name)
                elif status == 'SKIPPED':
                    skipped_tests.add(test_name)
            # Check for ERROR tests (treated as failed)
            error_match = error_pattern.match(line)
            if error_match:
                test_name = error_match.group(1)
                failed_tests.add(test_name)
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
