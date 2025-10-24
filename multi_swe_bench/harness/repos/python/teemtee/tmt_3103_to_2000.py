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
                """cat README.md
###ACTION_DELIMITER###
ls
###ACTION_DELIMITER###
cat README.rst
###ACTION_DELIMITER###
cat Makefile
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y gcc git python3-dev libvirt-dev krb5-multidev libpq-dev jq podman buildah rpm build-essential
###ACTION_DELIMITER###
pip install hatch
###ACTION_DELIMITER###
sed -i 's/sudo dnf install -y hatch python3-devel python3-hatch-vcs rpm-build/sudo apt-get install -y hatch python3-dev rpm-build/' Makefile && sed -i 's/sudo dnf install -y gcc git python3-nitrate {libvirt,krb5,libpq,python3}-devel jq podman buildah \/usr\/bin\/python3.9/sudo apt-get install -y gcc git libvirt-dev krb5-multidev libpq-dev jq podman buildah/' Makefile
###ACTION_DELIMITER###
make develop
###ACTION_DELIMITER###
sed -i 's/sudo //g' Makefile
###ACTION_DELIMITER###
make develop
###ACTION_DELIMITER###
sed -i 's/apt-get install -y hatch python3-dev rpm-build/apt-get install -y python3-dev rpm/' Makefile && sed -i 's/apt-get install -y gcc git libvirt-dev krb5-multidev libpq-dev jq podman buildah/apt-get install -y gcc git libvirt-dev krb5-multidev libpq-dev jq podman buildah/' Makefile
###ACTION_DELIMITER###
make develop
###ACTION_DELIMITER###
echo -e 'hatch run test:unit -v -k "not container"' > /home/tmt/test_commands.sh && chmod +x /home/tmt/test_commands.sh
###ACTION_DELIMITER###
bash /home/tmt/test_commands.sh
###ACTION_DELIMITER###
which krb5-config || dpkg -L krb5-multidev | grep krb5-config
###ACTION_DELIMITER###
ln -s /usr/bin/krb5-config.mit /usr/bin/krb5-config
###ACTION_DELIMITER###
bash /home/tmt/test_commands.sh
###ACTION_DELIMITER###
apt-get install -y clang
###ACTION_DELIMITER###
apt-get install -y python3-gssapi && pip install psycopg2-binary
###ACTION_DELIMITER###
sed -i '/\[tool.hatch.envs.test\]/a system-site-packages = true' pyproject.toml
###ACTION_DELIMITER###
bash /home/tmt/test_commands.sh
###ACTION_DELIMITER###
sed -i '/\[tool.hatch.envs.test\]/a environment-variables = { CFLAGS = "$(krb5-config --cflags gssapi)", LDFLAGS = "$(krb5-config --libs gssapi)" }' pyproject.toml && hatch env prune
###ACTION_DELIMITER###
echo -e 'export CFLAGS=$(krb5-config --cflags gssapi)\nexport LDFLAGS=$(krb5-config --libs gssapi)\nhatch run test:unit -v -k "not container"' > /home/tmt/test_commands.sh && chmod +x /home/tmt/test_commands.sh
###ACTION_DELIMITER###
bash /home/tmt/test_commands.sh
###ACTION_DELIMITER###
sed -i '/\[tool.hatch.envs.test\]/,/\[.*\]/ s/^system-site-packages.*/system-site-packages = true/; t; /\[tool.hatch.envs.test\]/a system-site-packages = true' pyproject.toml && hatch env prune
###ACTION_DELIMITER###
sed -i '/\[tool.hatch.envs.test\]/,/\[.*\]/ { /system-site-packages/d; }; /\[tool.hatch.envs.test\]/a system-site-packages = true' pyproject.toml
###ACTION_DELIMITER###
hatch env prune
###ACTION_DELIMITER###
bash /home/tmt/test_commands.sh
###ACTION_DELIMITER###
echo -e 'export CFLAGS=$(krb5-config --cflags gssapi)\nexport LDFLAGS=$(krb5-config --libs gssapi)\npip install gssapi\nhatch run test:unit -v -k "not container"' > /home/tmt/test_commands.sh && chmod +x /home/tmt/test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH\nexport CFLAGS=$(krb5-config --cflags gssapi)\nexport LDFLAGS=$(krb5-config --libs gssapi)\nhatch run test:unit -v -k "not container"' > /home/tmt/test_commands.sh && chmod +x /home/tmt/test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH\nexport CFLAGS=$(krb5-config --cflags gssapi)\nexport LDFLAGS=$(krb5-config --libs gssapi)\nhatch run test:unit -v -k "not container and not gssapi"' > /home/tmt/test_commands.sh && chmod +x /home/tmt/test_commands.sh
###ACTION_DELIMITER###
bash /home/tmt/test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH\nexport CFLAGS=$(krb5-config --cflags gssapi)\nexport LDFLAGS=$(krb5-config --libs gssapi)\nexport TERM=dumb\nhatch run test:unit -v -k "not (container or gssapi)"' > /home/tmt/test_commands.sh && chmod +x /home/tmt/test_commands.sh
###ACTION_DELIMITER###
bash /home/tmt/test_commands.sh
###ACTION_DELIMITER###
echo -e 'export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH\nexport TERM=dumb\npytest tests/unit -v -k "not (container or gssapi)"' > /home/tmt/test_commands.sh && chmod +x /home/tmt/test_commands.sh
###ACTION_DELIMITER###
bash /home/tmt/test_commands.sh
###ACTION_DELIMITER###
echo -e 'pip install pytest\nexport PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH\nexport TERM=dumb\npytest tests/unit -v -k "not (container or gssapi)"' > /home/tmt/test_commands.sh && chmod +x /home/tmt/test_commands.sh
###ACTION_DELIMITER###
bash /home/tmt/test_commands.sh
###ACTION_DELIMITER###
echo -e 'pip install -e .\npip install pytest\nexport PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH\nexport TERM=dumb\npytest tests/unit -v -k "not (container or gssapi)"' > /home/tmt/test_commands.sh && chmod +x /home/tmt/test_commands.sh
###ACTION_DELIMITER###
bash /home/tmt/test_commands.sh
###ACTION_DELIMITER###
echo -e 'pip install -e .\npip install pytest testcloud pytest-container\nexport PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH\nexport TERM=dumb\npytest tests/unit -v -k "not (container or gssapi)"' > /home/tmt/test_commands.sh && chmod +x /home/tmt/test_commands.sh
###ACTION_DELIMITER###
bash /home/tmt/test_commands.sh
###ACTION_DELIMITER###
echo -e 'pip install -e .\npip install pytest testcloud pytest-container python3-nitrate\nmake nitrateconf\nexport PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH\nexport TERM=dumb\npytest tests/unit -v -k "not (container or gssapi)"' > /home/tmt/test_commands.sh && chmod +x /home/tmt/test_commands.sh
###ACTION_DELIMITER###
bash /home/tmt/test_commands.sh
###ACTION_DELIMITER###
echo -e 'pip install -e .\npip install pytest testcloud pytest-container python3-nitrate pytest-junit\nmake nitrateconf\nexport PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH\nexport PATH=$PATH:/home/tmt/.local/bin\nexport TERM=dumb\npytest tests/unit -v -k "not (container or gssapi or nitrate or cli or junit)"' > /home/tmt/test_commands.sh && chmod +x /home/tmt/test_commands.sh
###ACTION_DELIMITER###
bash /home/tmt/test_commands.sh""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
pip install -e .
pip install pytest testcloud pytest-container python3-nitrate pytest-junit
make nitrateconf
export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH
export PATH=$PATH:/home/tmt/.local/bin
export TERM=dumb
pytest tests/unit -v -k "not (container or gssapi or nitrate or cli or junit)"

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
pip install -e .
pip install pytest testcloud pytest-container python3-nitrate pytest-junit
make nitrateconf
export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH
export PATH=$PATH:/home/tmt/.local/bin
export TERM=dumb
pytest tests/unit -v -k "not (container or gssapi or nitrate or cli or junit)"

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
pip install -e .
pip install pytest testcloud pytest-container python3-nitrate pytest-junit
make nitrateconf
export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH
export PATH=$PATH:/home/tmt/.local/bin
export TERM=dumb
pytest tests/unit -v -k "not (container or gssapi or nitrate or cli or junit)"

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
RUN git clone https://github.com/teemtee/tmt.git /home/tmt

WORKDIR /home/tmt
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("teemtee", "tmt_3103_to_2000")
class TMT_3103_TO_2000(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re

        # Extract passed tests (pattern: line number ] followed by test name and PASSED)
        passed_pattern = re.compile(r"\]\s+(tests/.*?)\s+PASSED", re.MULTILINE)
        for test in passed_pattern.findall(log):
            passed_tests.add(test.strip())
        # Extract failed tests (pattern: FAILED followed by test name)
        failed_pattern = re.compile(r"FAILED\s+(tests/.*)", re.MULTILINE)
        for test in failed_pattern.findall(log):
            failed_tests.add(test.strip())
        # Extract skipped tests (pattern: SKIPPED followed by test name, if present)
        skipped_pattern = re.compile(r"SKIPPED\s+(tests/.*)", re.MULTILINE)
        for test in skipped_pattern.findall(log):
            skipped_tests.add(test.strip())
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
