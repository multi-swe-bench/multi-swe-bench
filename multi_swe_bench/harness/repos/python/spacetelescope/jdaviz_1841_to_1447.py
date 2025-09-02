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
                """ls
###ACTION_DELIMITER###
pip install -e .[test]
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgl1-mesa-glx libgomp1 libjpeg62-turbo zlib1g
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
sed -i '/filterwarnings =/a \    ignore:Jupyter is migrating its paths to use standard platformdirs:DeprecationWarning:jupyter_core.utils' setup.cfg
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
export JUPYTER_PLATFORM_DIRS=1 && pytest -v
###ACTION_DELIMITER###
sed -i '/filterwarnings =/a \    ignore:Sentinel is not a public part of the traitlets API:DeprecationWarning:traitlets.utils.warnings' setup.cfg
###ACTION_DELIMITER###
export JUPYTER_PLATFORM_DIRS=1 && pytest -v
###ACTION_DELIMITER###
sed -i '/filterwarnings =/a \    ignore:Sentinel is not a public part of the traitlets API:DeprecationWarning:traitlets' setup.cfg
###ACTION_DELIMITER###
export JUPYTER_PLATFORM_DIRS=1 && pytest -v
###ACTION_DELIMITER###
sed -i '/filterwarnings =/a \    ignore:Sentinel is not a public part of the traitlets API:DeprecationWarning:traitlets.utils.warnings' setup.cfg
###ACTION_DELIMITER###
sed -i '/filterwarnings =/a \    ignore:Sentinel is not a public part of the traitlets API:DeprecationWarning:traitlets.utils.warnings' setup.cfg
###ACTION_DELIMITER###
sed -i '/filterwarnings =/a \    ignore:^Sentinel is not a public part of the traitlets API:DeprecationWarning:traitlets' setup.cfg
###ACTION_DELIMITER###
sed -i '/filterwarnings =/a \    ignore:Sentinel is not a public part of the traitlets API.*:DeprecationWarning:traitlets.utils.warnings' setup.cfg
###ACTION_DELIMITER###
sed -i '/^    error/a \    ignore:Sentinel is not a public part of the traitlets API:DeprecationWarning:traitlets.utils.warnings' setup.cfg
###ACTION_DELIMITER###
sed -i '/^    error/a \    ignore:.*Sentinel is not a public part of the traitlets API.*:DeprecationWarning:traitlets.utils.warnings' setup.cfg && export JUPYTER_PLATFORM_DIRS=1 && pytest -v
###ACTION_DELIMITER###
sed -i '/^    error/a \    ignore:Sentinel is not a public part of the traitlets API:DeprecationWarning:traitlets.utils.warnings' setup.cfg && export JUPYTER_PLATFORM_DIRS=1 && pytest -v
###ACTION_DELIMITER###
sed -i '/^    error/a \    ignore:.*Sentinel is not a public part of the traitlets API.*:DeprecationWarning:traitlets.utils.warnings' setup.cfg && export JUPYTER_PLATFORM_DIRS=1 && pytest -v
###ACTION_DELIMITER###
export JUPYTER_PLATFORM_DIRS=1 && export PYTHONWARNINGS='ignore:Sentinel is not a public part of the traitlets API:DeprecationWarning:traitlets.utils.warnings' && pytest -v
###ACTION_DELIMITER###
export JUPYTER_PLATFORM_DIRS=1 && pytest -v -W ignore:"Sentinel is not a public part of the traitlets API":DeprecationWarning:traitlets
###ACTION_DELIMITER###
export PYTHONWARNINGS='ignore:Sentinel is not a public part of the traitlets API.*:DeprecationWarning:traitlets.utils.warnings' && export JUPYTER_PLATFORM_DIRS=1 && pytest -v
###ACTION_DELIMITER###
sed -i '/^    error/a \    ignore:Sentinel is not a public part of the traitlets API:DeprecationWarning:traitlets.utils.warnings' setup.cfg && export JUPYTER_PLATFORM_DIRS=1 && pytest -v
###ACTION_DELIMITER###
export JUPYTER_PLATFORM_DIRS=1 && pytest -v -W 'ignore:Sentinel is not a public part of the traitlets API:DeprecationWarning:traitlets.utils.warnings'
###ACTION_DELIMITER###
export JUPYTER_PLATFORM_DIRS=1 && pytest -v -W 'ignore:Sentinel is not a public part of the traitlets API.*:DeprecationWarning:traitlets.utils.warnings'
###ACTION_DELIMITER###
export JUPYTER_PLATFORM_DIRS=1 && pytest -v -W ignore::DeprecationWarning
###ACTION_DELIMITER###
pip install astropy && export JUPYTER_PLATFORM_DIRS=1 && pytest -v -W ignore::DeprecationWarning
###ACTION_DELIMITER###
pip install 'asdf>=2.7.4' && export JUPYTER_PLATFORM_DIRS=1 && pytest -v -W ignore::DeprecationWarning
###ACTION_DELIMITER###
pip install 'asdf[fits]>=2.7.4' && export JUPYTER_PLATFORM_DIRS=1 && pytest -v -W ignore::DeprecationWarning
###ACTION_DELIMITER###
pip install 'asdf==2.14.3' && export JUPYTER_PLATFORM_DIRS=1 && pytest -v -W ignore::DeprecationWarning
###ACTION_DELIMITER###
pip install 'lxml[html_clean]' && export JUPYTER_PLATFORM_DIRS=1 && pytest -v -W ignore::DeprecationWarning
###ACTION_DELIMITER###
pip install lxml-html-clean && export JUPYTER_PLATFORM_DIRS=1 && pytest -v -W ignore::DeprecationWarning
###ACTION_DELIMITER###
echo 'export JUPYTER_PLATFORM_DIRS=1 && pytest -v -W ignore::DeprecationWarning -W ignore::astropy.units.core.UnitsWarning' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo '#!/bin/bash
 export JUPYTER_PLATFORM_DIRS=1 && pytest -v -W ignore::DeprecationWarning -W ignore::astropy.units.core.UnitsWarning' > test_commands.sh && chmod +x test_commands.sh && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
 export JUPYTER_PLATFORM_DIRS=1 && pytest -v -W ignore::DeprecationWarning -W ignore::astropy.units.core.UnitsWarning

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
 export JUPYTER_PLATFORM_DIRS=1 && pytest -v -W ignore::DeprecationWarning -W ignore::astropy.units.core.UnitsWarning

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
 export JUPYTER_PLATFORM_DIRS=1 && pytest -v -W ignore::DeprecationWarning -W ignore::astropy.units.core.UnitsWarning

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
RUN git clone https://github.com/spacetelescope/jdaviz.git /home/jdaviz

WORKDIR /home/jdaviz
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("spacetelescope", "jdaviz_1841_to_1447")
class JDAVIZ_1841_TO_1447(Instance):
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
        import json
        # Define regex patterns to match test cases and their statuses
        pattern1 = re.compile(r'^(?:\[\s*\d+\]\s+)?(.+::.+?)\s+(PASSED|FAILED|SKIPPED)\s+\[\s*\d+%?\s*\]')  # Capture test names with :: separators
        pattern2 = re.compile(r'^(?:\[\s*\d+\]\s+)?(PASSED|FAILED|SKIPPED)\s+(.+::.+?)(?::|\s+-|$)')      # Capture test names with :: separators
        # Split log content into lines and process each line
        for line in log.split('\n'):
            line = line.strip()
            match = pattern1.match(line)
            if match:
                test_name = match.group(1).strip()
                status = match.group(2).strip()
            else:
                match = pattern2.match(line)
                if match:
                    status = match.group(1).strip()
                    test_name = match.group(2).strip()
                else:
                    continue  # Skip lines that don't match
            # Add test to the appropriate set based on status
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
