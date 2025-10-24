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
        return "python:3.10-slim-bullseye"

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
                """apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && bash miniconda.sh -b -p /opt/conda && rm miniconda.sh
###ACTION_DELIMITER###
source /opt/conda/etc/profile.d/conda.sh
###ACTION_DELIMITER###
conda create -n augur -c conda-forge -c bioconda python=3.10 mafft raxml fasttree iqtree vcftools seqkit sqlite tsv-utils biopython -y
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
###ACTION_DELIMITER###
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
###ACTION_DELIMITER###
conda create -n augur -c conda-forge -c bioconda python=3.10 mafft raxml fasttree iqtree vcftools seqkit sqlite tsv-utils biopython -y
###ACTION_DELIMITER###
conda activate augur
###ACTION_DELIMITER###
pip install .[dev]
###ACTION_DELIMITER###
echo -e '#!/bin/bash
pytest --cov=augur -v
cram -v tests/' > test_commands.sh && chmod +x test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
pytest --cov=augur -v
cram -v tests/

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
pytest --cov=augur -v
cram -v tests/

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
pytest --cov=augur -v
cram -v tests/

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
FROM python:3.10-slim-bullseye

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
RUN git clone https://github.com/nextstrain/augur.git /home/augur

WORKDIR /home/augur
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("nextstrain", "augur_1834_to_1278")
class AUGUR_1834_TO_1278(Instance):
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
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re
        import json

        lines = log.split("\n")
        statuses = {"passed", "failed", "skipped", "PASSED", "FAILED", "SKIPPED"}
        for i in range(len(lines)):
            line = lines[i].strip()
            # Check same-line status
            same_line_match = re.match(
                r"^(.*?)\s*[:\s]\s*(PASSED|FAILED|SKIPPED|passed|failed|skipped)$", line
            )
            if same_line_match:
                test_name = same_line_match.group(1).strip()
                status = same_line_match.group(2).lower()
                if status == "passed":
                    passed_tests.add(test_name)
                elif status == "failed":
                    failed_tests.add(test_name)
                elif status == "skipped":
                    skipped_tests.add(test_name)
                continue
            # Check if current line is a status and previous line has a test name
            if line in statuses:
                status = line.lower()
                if i > 0:
                    prev_line = lines[i - 1].strip()
                    test_name_match = re.search(
                        r"([a-zA-Z0-9/_]+\.py::[a-zA-Z0-9_]+(::[a-zA-Z0-9_]+)?|[a-zA-Z0-9/_]+\.t)",
                        prev_line,
                    )
                    if test_name_match:
                        test_name = test_name_match.group(1)
                        if status == "passed":
                            passed_tests.add(test_name)
                        elif status == "failed":
                            failed_tests.add(test_name)
                        elif status == "skipped":
                            skipped_tests.add(test_name)
                continue
            # Check if current line has a test name and next line is a status
            test_name_match = re.search(
                r"([a-zA-Z0-9/_]+\.py::[a-zA-Z0-9_]+(::[a-zA-Z0-9_]+)?|[a-zA-Z0-9/_]+\.t)",
                line,
            )
            if test_name_match and i < len(lines) - 1:
                next_line = lines[i + 1].strip()
                if next_line in statuses:
                    test_name = test_name_match.group(1)
                    status = next_line.lower()
                    if status == "passed":
                        passed_tests.add(test_name)
                    elif status == "failed":
                        failed_tests.add(test_name)
                    elif status == "skipped":
                        skipped_tests.add(test_name)
                continue
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
