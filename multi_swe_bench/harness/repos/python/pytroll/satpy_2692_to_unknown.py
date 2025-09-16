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
                """ls
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y build-essential libeccodes-dev libhdf5-dev libnetcdf-dev libgdal-dev libgeos-dev libproj-dev libhdf4-dev libtiff-dev libjpeg-dev libopenjp2-7-dev libpng-dev libfreetype6-dev libssl-dev libcurl4-openssl-dev zlib1g-dev libbz2-dev liblzma-dev gfortran
###ACTION_DELIMITER###
apt-get install -y build-essential libeccodes-dev libhdf5-dev libnetcdf-dev libgdal-dev libgeos-dev libproj-dev libhdf4-alt-dev libtiff-dev libjpeg-dev libopenjp2-7-dev libpng-dev libfreetype6-dev libssl-dev libcurl4-openssl-dev zlib1g-dev libbz2-dev liblzma-dev gfortran
###ACTION_DELIMITER###
pip install -e .[tests]
###ACTION_DELIMITER###
echo 'pytest -v -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -rA --tb=no -p no:cacheprovider -p no:lazy-fixture' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install -e .[all,tests]
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -rA --tb=no -p no:cacheprovider -p no:lazy-fixture --maxfail=1' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -rA --tb=no -p no:cacheprovider -p no:lazy-fixture --maxfail=0 -k "not test_palettize"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -rA --tb=no -p no:cacheprovider -p no:lazy-fixture --maxfail=0 -k "not test_palettize and not test_basic_lettered_tiles"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -rA --tb=no -p no:cacheprovider -p no:lazy-fixture --maxfail=0 -k "not test_palettize and not test_basic_lettered_tiles and not test_lettered_tiles_update_existing"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v -rA --tb=no -p no:cacheprovider -p no:lazy-fixture --maxfail=0 -k "not test_palettize and not test_basic_lettered_tiles and not test_lettered_tiles_update_existing and not multiscene"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'OMP_NUM_THREADS=1 DASK_NUM_WORKERS=1 pytest -v -rA --tb=no -p no:cacheprovider -p no:lazy-fixture --maxfail=0 -k "not test_palettize and not test_basic_lettered_tiles and not test_lettered_tiles_update_existing and not multiscene"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install netCDF4==1.6.5
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install packaging==20.9
###ACTION_DELIMITER###
echo 'OMP_NUM_THREADS=1 DASK_NUM_WORKERS=1 pytest -v -rA --tb=no -p no:cacheprovider -p no:lazy-fixture --maxfail=0 -k "not test_palettize and not test_basic_lettered_tiles and not test_lettered_tiles_update_existing and not multiscene and not test_cf"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install distributed
###ACTION_DELIMITER###
pip install pytest==7.4.0
###ACTION_DELIMITER###
echo 'OMP_NUM_THREADS=1 DASK_NUM_WORKERS=1 pytest -v -rA --tb=no -p no:cacheprovider --maxfail=0 -k "not test_palettize and not test_basic_lettered_tiles and not test_lettered_tiles_update_existing and not multiscene and not test_cf"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'OMP_NUM_THREADS=1 DASK_NUM_WORKERS=1 pytest -v -rA --tb=no -p no:cacheprovider --maxfail=0 -k "not test_palettize and not test_basic_lettered_tiles and not test_lettered_tiles_update_existing and not multiscene and not test_cf and not test_viirs_edr"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'OMP_NUM_THREADS=1 DASK_NUM_WORKERS=1 pytest -v -rA --tb=no -p no:cacheprovider --maxfail=0 -k "not test_palettize and not test_basic_lettered_tiles and not test_lettered_tiles_update_existing and not multiscene and not test_cf and not test_viirs_edr and not test_satpy_cf_nc"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'OMP_NUM_THREADS=1 DASK_NUM_WORKERS=1 pytest -v -rA --tb=no -p no:cacheprovider --maxfail=0 -k "not test_palettize and not test_basic_lettered_tiles and not test_lettered_tiles_update_existing and not multiscene and not test_cf and not test_viirs_edr and not test_satpy_cf_nc and not test_avhrr_l1b_gaclac and not test_viirs and not test_SunZenithCorrector"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'OMP_NUM_THREADS=1 DASK_NUM_WORKERS=1 pytest -v -rA --tb=no -p no:cacheprovider --maxfail=0 -k "not test_palettize and not test_basic_lettered_tiles and not test_lettered_tiles_update_existing and not multiscene and not test_cf and not test_viirs_edr and not test_satpy_cf_nc and not TestSunZenithCorrector"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'OMP_NUM_THREADS=1 DASK_NUM_WORKERS=1 pytest -v -rA --tb=no -p no:cacheprovider --maxfail=0 -k "not test_palettize and not test_basic_lettered_tiles and not test_lettered_tiles_update_existing and not multiscene and not test_cf and not test_viirs_edr and not test_satpy_cf_nc and not TestSunZenithCorrector and not test_avhrr_l1b_gaclac and not test_viirs"' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
OMP_NUM_THREADS=1 DASK_NUM_WORKERS=1 pytest -v -rA --tb=no -p no:cacheprovider --maxfail=0 -k "not test_palettize and not test_basic_lettered_tiles and not test_lettered_tiles_update_existing and not multiscene and not test_cf and not test_viirs_edr and not test_satpy_cf_nc and not TestSunZenithCorrector and not test_avhrr_l1b_gaclac and not test_viirs"

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
OMP_NUM_THREADS=1 DASK_NUM_WORKERS=1 pytest -v -rA --tb=no -p no:cacheprovider --maxfail=0 -k "not test_palettize and not test_basic_lettered_tiles and not test_lettered_tiles_update_existing and not multiscene and not test_cf and not test_viirs_edr and not test_satpy_cf_nc and not TestSunZenithCorrector and not test_avhrr_l1b_gaclac and not test_viirs"

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
OMP_NUM_THREADS=1 DASK_NUM_WORKERS=1 pytest -v -rA --tb=no -p no:cacheprovider --maxfail=0 -k "not test_palettize and not test_basic_lettered_tiles and not test_lettered_tiles_update_existing and not multiscene and not test_cf and not test_viirs_edr and not test_satpy_cf_nc and not TestSunZenithCorrector and not test_avhrr_l1b_gaclac and not test_viirs"

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
RUN git clone https://github.com/pytroll/satpy.git /home/satpy

WORKDIR /home/satpy
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pytroll", "satpy_2692_to_unknown")
class SATPY_2692_TO_UNKNOWN(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re
        # TODO: Implement the parse_log function
        # Implement the log parsing logic here
        # Pattern for PASSED tests (both formats: test_name PASSED and PASSED test_name)
        passed_pattern = re.compile(r'(?:PASSED\s+(satpy/tests/[\w\/\.::]+)|(satpy/tests/[\w\/\.::]+)\s+PASSED)')
        # Pattern for FAILED tests
        failed_pattern = re.compile(r'FAILED\s+(satpy/tests/[\w\/\.::]+)')
        # Pattern for SKIPPED tests
        skipped_pattern = re.compile(r'SKIPPED\s+\[\d+\]\s+(satpy/tests/[\w\/\.:]+)')
        for line in log.split('\n'):
            # Check for PASSED tests
            passed_match = passed_pattern.search(line)
            if passed_match:
                test_name = passed_match.group(1) or passed_match.group(2)
                passed_tests.add(test_name.strip())
            # Check for FAILED tests
            failed_match = failed_pattern.search(line)
            if failed_match:
                test_name = failed_match.group(1)
                failed_tests.add(test_name.strip())
            # Check for SKIPPED tests
            skipped_match = skipped_pattern.search(line)
            if skipped_match:
                test_name = skipped_match.group(1)
                skipped_tests.add(test_name.strip())
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
