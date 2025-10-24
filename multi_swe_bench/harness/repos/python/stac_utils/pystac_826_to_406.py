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
                """pip install -e ".[validation]"
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3 python3-pip
###ACTION_DELIMITER###
pip install -e ".[validation]"
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
apt-get install -y python3.12-venv
###ACTION_DELIMITER###
python3 -m venv venv
###ACTION_DELIMITER###
source venv/bin/activate && pip install -e ".[validation]"
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install jsonschema==4.17.3
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
./scripts/test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install pre-commit
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install black codespell doc8 flake8 mypy
###ACTION_DELIMITER###
source venv/bin/activate && pre-commit install
###ACTION_DELIMITER###
source venv/bin/activate && pre-commit run --all-files
###ACTION_DELIMITER###
source venv/bin/activate && pip install types-python-dateutil
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -c "import pystac.validation; pystac.validation.set_validator(pystac.validation.LocalSchemaValidator())"
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -c "import pystac.validation; from pystac.schemas import get_schema_uri_map; pystac.validation.set_validator(pystac.validation.Validator(schema_uri_map=get_schema_uri_map()))"
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -c "import pystac.validation; from pystac.validation.stac_validator import LocalSchemaValidator; pystac.validation.set_validator(LocalSchemaValidator())"
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -c "import pystac.validation; from pystac.validation.stac_validator import schema_uri_map; pystac.validation.set_validator(pystac.validation.Validator(schema_uri_map=schema_uri_map))"
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -c "import pystac.validation; from pystac.validation.stac_validator import SchemaUriMap; pystac.validation.set_validator(pystac.validation.Validator(schema_uri_map=SchemaUriMap()))"
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -c "import pystac.validation; from pystac.validation.stac_validator import STACValidator, SchemaUriMap; pystac.validation.set_validator(STACValidator(schema_uri_map=SchemaUriMap()))"
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -c "import pystac.validation; from pystac.validation import LocalSchemaValidator; pystac.validation.set_validator(LocalSchemaValidator())"
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -c "import pystac.validation; from pystac.validation.stac_validator import STACValidator; pystac.validation.set_validator(STACValidator())"
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -c "import pystac.validation; from pystac.validation import LocalSchemaValidator; pystac.validation.set_validator(LocalSchemaValidator())"
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -c "import pystac.validation; from pystac.validation.stac_validator import JsonSchemaSTACValidator; from pystac.schemas import get_schema_uri_map; pystac.validation.set_validator(JsonSchemaSTACValidator(schema_uri_map=get_schema_uri_map()))"
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -c "import pystac.validation; from pystac.validation.stac_validator import JsonSchemaSTACValidator, SchemaUriMap; pystac.validation.set_validator(JsonSchemaSTACValidator(schema_uri_map=SchemaUriMap()))"
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -c "import pystac.validation; from pystac.validation import get_schema_uri_map; from pystac.validation.stac_validator import JsonSchemaSTACValidator; pystac.validation.set_validator(JsonSchemaSTACValidator(schema_uri_map=get_schema_uri_map()))"
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -c "import pystac.validation; from pystac.validation.stac_validator import JsonSchemaSTACValidator, schema_uri_map; pystac.validation.set_validator(JsonSchemaSTACValidator(schema_uri_map=schema_uri_map))"
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -c "import pystac.validation; from pystac.validation.stac_validator import JsonSchemaSTACValidator; pystac.validation.set_validator(JsonSchemaSTACValidator())"
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -c "import pystac.validation; from pystac.validation.stac_validator import JsonSchemaSTACValidator, schema_uri_map; pystac.validation.set_validator(JsonSchemaSTACValidator(schema_uri_map=schema_uri_map))"
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -c "import pystac.validation; from pystac.validation.stac_validator import LocalSchemaValidator; pystac.validation.set_validator(LocalSchemaValidator())"
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'source venv/bin/activate
python -c "import pystac.validation; from pystac.validation.stac_validator import JsonSchemaSTACValidator; from pystac.validation.schema_uri_map import DefaultSchemaUriMap; pystac.validation.set_validator(JsonSchemaSTACValidator(schema_uri_map=DefaultSchemaUriMap()))"
python -m unittest discover -v -s tests/' > test_commands.sh
###ACTION_DELIMITER###
""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
source venv/bin/activate
python -c "import pystac.validation; from pystac.validation.stac_validator import JsonSchemaSTACValidator; from pystac.validation.schema_uri_map import DefaultSchemaUriMap; pystac.validation.set_validator(JsonSchemaSTACValidator(schema_uri_map=DefaultSchemaUriMap()))"
python -m unittest discover -v -s tests/

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
source venv/bin/activate
python -c "import pystac.validation; from pystac.validation.stac_validator import JsonSchemaSTACValidator; from pystac.validation.schema_uri_map import DefaultSchemaUriMap; pystac.validation.set_validator(JsonSchemaSTACValidator(schema_uri_map=DefaultSchemaUriMap()))"
python -m unittest discover -v -s tests/

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
source venv/bin/activate
python -c "import pystac.validation; from pystac.validation.stac_validator import JsonSchemaSTACValidator; from pystac.validation.schema_uri_map import DefaultSchemaUriMap; pystac.validation.set_validator(JsonSchemaSTACValidator(schema_uri_map=DefaultSchemaUriMap()))"
python -m unittest discover -v -s tests/

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
RUN git clone https://github.com/stac-utils/pystac.git /home/pystac

WORKDIR /home/pystac
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("stac-utils", "pystac_826_to_406")
class PYSTAC_826_TO_406(Instance):
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

        # Pattern for passed tests: lines starting with [number], then test name, (test_id), ... ok
        passed_pattern = re.compile(r"\(([^)]+)\)\s*\.\.\.\s*ok", re.MULTILINE)
        # Pattern for failed tests: lines starting with [number], FAIL: ... (test_id)
        failed_pattern = re.compile(r"FAIL:\s*[^(]+\s*\(([^)]+)\)", re.MULTILINE)
        # Pattern for error tests: lines starting with [number], ERROR: ... (test_id)
        error_pattern = re.compile(r"ERROR:\s*[^(]+\s*\(([^)]+)\)", re.MULTILINE)
        # Pattern for skipped tests: lines starting with [number], ... skipped
        skipped_pattern = re.compile(r"\(([^)]+)\)\s*\.\.\.\s*skipped", re.MULTILINE)
        # Find all passed tests
        passed_tests.update(passed_pattern.findall(log))
        # Find all failed tests
        failed_tests.update(failed_pattern.findall(log))
        # Find all error tests (consider as failed)
        failed_tests.update(error_pattern.findall(log))
        # Find all skipped tests
        skipped_tests.update(skipped_pattern.findall(log))
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
