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
echo 'deb http://deb.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list.d/backports.list && apt-get update && apt-get install -y -t bullseye-backports python3.10 python3.10-dev python3.10-distutils
###ACTION_DELIMITER###
rm -f /etc/apt/sources.list.d/backports.list && echo 'deb http://deb.debian.org/debian bookworm-backports main' >> /etc/apt/sources.list.d/backports.list && apt-get update && apt-get install -y -t bookworm-backports python3.10 python3.10-dev python3.10-distutils
###ACTION_DELIMITER###
apt-cache search python3.10
###ACTION_DELIMITER###
rm -f /etc/apt/sources.list.d/backports.list && echo 'deb [trusted=yes] http://archive.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list.d/backports.list && apt-get update && apt-get install -y -t bullseye-backports python3.10 python3.10-dev python3.10-distutils
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
###ACTION_DELIMITER###
wget https://www.python.org/ftp/python/3.10.13/Python-3.10.13.tgz && tar -xzf Python-3.10.13.tgz
###ACTION_DELIMITER###
cd Python-3.10.13 && ./configure --enable-optimizations
###ACTION_DELIMITER###
make -j4
###ACTION_DELIMITER###
make install
###ACTION_DELIMITER###
cd /home/xcp_d && pip3.10 install --no-cache-dir .[tests]
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 libopenblas-dev libgomp1
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'pytest -v --no-header -rA --tb=no -p no:cacheprovider xcp_d/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
templateflow pull
###ACTION_DELIMITER###
echo 'from templateflow.api import get; get("MNI152NLin2009cAsym"); get("MNI152NLin6Asym")' > download_templates.py && python3.10 download_templates.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'from templateflow.api import get; get("MNI152NLin2009cAsym"); get("MNI152NLin6Asym"); get("MNI152NLin2009cAsym", atlas="Schaefer2018"); get("MNI152NLin6Asym", atlas="Schaefer2018")' > download_templates.py && python3.10 download_templates.py
###ACTION_DELIMITER###
mkdir -p dummy_bids && echo '{"Name": "Dummy Dataset", "BIDSVersion": "1.8.0"}' > dummy_bids/dataset_description.json && export BIDS_ROOT=$(pwd)/dummy_bids && bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y fsl-core afni && export FSLDIR=/usr/share/fsl/6.0 && export PATH=$FSLDIR/bin:$PATH && bash test_commands.sh
###ACTION_DELIMITER###
export TEMPLATEFLOW_HOME=/home/xcp_d/templateflow && mkdir -p $TEMPLATEFLOW_HOME && templateflow pull && apt-get install -y libssl-dev libffi-dev && bash test_commands.sh
###ACTION_DELIMITER###
export TEMPLATEFLOW_HOME=/home/xcp_d/templateflow && mkdir -p $TEMPLATEFLOW_HOME && python3.10 -c 'from templateflow.api import get; get("MNI152NLin2009cAsym"); get("MNI152NLin6Asym"); get("MNI152NLin2009cAsym", atlas="Schaefer2018")' && git clone https://github.com/OpenNeuroDatasets/ds000001.git dummy_bids && export BIDS_ROOT=$(pwd)/dummy_bids && bash test_commands.sh
###ACTION_DELIMITER###
rm -rf dummy_bids && git clone https://github.com/OpenNeuroDatasets/ds000001.git dummy_bids && export BIDS_ROOT=$(pwd)/dummy_bids && export TEMPLATEFLOW_HOME=/home/xcp_d/templateflow && bash test_commands.sh
###ACTION_DELIMITER###
python3.10 -c 'from templateflow.api import get; get("MNI152NLin2009cAsym", atlas="Schaefer2018", resolution=2); get("MNI152NLin6Asym", atlas="Schaefer2018", resolution=2)' && ln -s $(pwd)/dummy_bids /usr/local/miniconda/lib/python3.10/site-packages/xcp_d/tests/data && bash test_commands.sh
###ACTION_DELIMITER###
mkdir -p tests/data && ln -s $(pwd)/dummy_bids tests/data && export BIDS_ROOT=$(pwd)/dummy_bids && export TEMPLATEFLOW_HOME=/home/xcp_d/templateflow && bash test_commands.sh
###ACTION_DELIMITER###
mkdir -p /usr/local/miniconda/lib/python3.10/site-packages/xcp_d/tests/data && ln -s $(pwd)/dummy_bids /usr/local/miniconda/lib/python3.10/site-packages/xcp_d/tests/data && python3.10 -c 'from templateflow.api import get; get("MNI152NLin2009cAsym", atlas="Schaefer2018", resolution=2); get("MNI152NLin6Asym", atlas="Schaefer2018", resolution=2)' && export TEMPLATEFLOW_HOME=/home/xcp_d/templateflow && export BIDS_ROOT=$(pwd)/dummy_bids && bash test_commands.sh
###ACTION_DELIMITER###
mkdir -p /usr/local/miniconda/lib/python3.10/site-packages/xcp_d/tests/data && ln -sf $(pwd)/dummy_bids /usr/local/miniconda/lib/python3.10/site-packages/xcp_d/tests/data/ds000001 && python3.10 -c 'from templateflow.api import get; get("MNI152NLin2009cAsym", atlas="Schaefer2018", resolution=2); get("MNI152NLin6Asym", atlas="Schaefer2018", resolution=2); get("MNI152NLin2009cAsym", atlas="Schaefer2018", resolution=1)' && export TEMPLATEFLOW_HOME=/home/xcp_d/templateflow && export BIDS_ROOT=$(pwd)/dummy_bids && bash test_commands.sh
###ACTION_DELIMITER###
export TEMPLATEFLOW_HOME=/home/xcp_d/templateflow && export BIDS_ROOT=$(pwd)/dummy_bids && echo 'TemplateFlow contents:' && ls $TEMPLATEFLOW_HOME/tpl-MNI152NLin2009cAsym && echo 'BIDS dataset path:' && ls /usr/local/miniconda/lib/python3.10/site-packages/xcp_d/tests/data && pytest -v --no-header -rA --tb=no -p no:cacheprovider xcp_d/
###ACTION_DELIMITER###
ln -sf $(pwd)/dummy_bids /usr/local/miniconda/lib/python3.10/site-packages/xcp_d/tests/data/ds001419 && apt-get install -y freesurfer && export FREESURFER_HOME=/usr/local/freesurfer && bash test_commands.sh
###ACTION_DELIMITER###
mkdir -p /usr/local/freesurfer && ln -sf $(pwd)/dummy_bids /usr/local/miniconda/lib/python3.10/site-packages/xcp_d/tests/data/ds001419 && export BIDS_ROOT=$(pwd)/dummy_bids && export TEMPLATEFLOW_HOME=/home/xcp_d/templateflow && export FREESURFER_HOME=/usr/local/freesurfer && bash test_commands.sh
###ACTION_DELIMITER###
mkdir -p /usr/local/miniconda/lib/python3.10/site-packages/xcp_d/tests/data && ln -sf $(pwd)/dummy_bids /usr/local/miniconda/lib/python3.10/site-packages/xcp_d/tests/data && python3.10 -c 'from templateflow.api import get; get("MNI152NLin2009cAsym", atlas="Schaefer2018", resolution=2); get("MNI152NLin6Asym", atlas="Schaefer2018", resolution=2); get("MNI152NLin2009cAsym", atlas="Schaefer2018", resolution=1)' && mkdir -p /usr/local/freesurfer/subjects && export BIDS_ROOT=$(pwd)/dummy_bids && export TEMPLATEFLOW_HOME=/home/xcp_d/templateflow && export FREESURFER_HOME=/usr/local/freesurfer && bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
pytest -v --no-header -rA --tb=no -p no:cacheprovider xcp_d/

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider xcp_d/

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
pytest -v --no-header -rA --tb=no -p no:cacheprovider xcp_d/

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
RUN git clone https://github.com/PennLINC/xcp_d.git /home/xcp_d

WORKDIR /home/xcp_d
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("PennLINC", "xcp_d_1061_to_956")
class XCP_D_1061_TO_956(Instance):
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
        # Regular expression pattern to match test cases and their statuses
        test_pattern = re.compile(
            r'(xcp_d/tests/[\w.]+\.py::[\w_]+)\s+(PASSED|FAILED|ERROR)|(PASSED|FAILED|ERROR)\s+(xcp_d/tests/[\w.]+\.py::[\w_]+)'
        )
        for line in log.splitlines():
            match = test_pattern.search(line)
            if match:
                # Extract test name and status from positional groups
                if match.group(1) and match.group(2):
                    test_name = match.group(1).strip()
                    status = match.group(2).strip()
                elif match.group(3) and match.group(4):
                    status = match.group(3).strip()
                    test_name = match.group(4).strip()
                else:
                    continue  # No valid groups matched
                if status == 'PASSED':
                    passed_tests.add(test_name)
                elif status in ('FAILED', 'ERROR'):
                    failed_tests.add(test_name)
                # Handle SKIPPED if present in logs
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
