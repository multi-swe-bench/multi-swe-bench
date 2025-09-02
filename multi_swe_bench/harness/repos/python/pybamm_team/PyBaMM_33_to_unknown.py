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
echo 'python run-tests.py --quick --allbooks' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
pip install -e .[dev,docs]
###ACTION_DELIMITER###
sed -i '/url=/a packages=['\''pybamm'\'', '\''input'\''], ' setup.py
###ACTION_DELIMITER###
pip install -e .[dev,docs]
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
pip install anytree
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/    url=/    url=/' setup.py; sed -i 's/  extras_require=/    extras_require=/' setup.py; sed -i 's/  ]/    ]/' setup.py; sed -i 's/)$/    )/' setup.py
###ACTION_DELIMITER###
flake8 setup.py
###ACTION_DELIMITER###
sed -i 's/open( /open(/; s/ )/)/' setup.py; sed -i 's/^  packages=/    packages=/' setup.py; sed -i 's/[[:space:]]*$//' setup.py; sed -i 's/^       /    /' setup.py; sed -i 's/^  ]/    ]/' setup.py; sed -i 's/^)$/    )/' setup.py
###ACTION_DELIMITER###
flake8 setup.py
###ACTION_DELIMITER###
sed -i 's/open( /open(/; s/ )/)/' setup.py; sed -i 's/^  packages=/    packages=/' setup.py; sed -i 's/^      /    /' setup.py; sed -i 's/^    ]/  ]/' setup.py; sed -i 's/^  )/)/' setup.py
###ACTION_DELIMITER###
sed -i 's/open( /open(/; s/ )/)/' setup.py; sed -i 's/^  install_requires=/    install_requires=/' setup.py; sed -i 's/^    \[/  \[/' setup.py; sed -i 's/^      "/    "/' setup.py; sed -i 's/^    ]/  ]/' setup.py; sed -i 's/^  extras_require=/    extras_require=/' setup.py; sed -i 's/^  )/)/' setup.py
###ACTION_DELIMITER###
sed -i '8s/open( /open(/; 8s/ )/)/' setup.py; sed -i 's/^  packages=/    packages=/' setup.py; sed -i 's/^      "/    "/' setup.py; sed -i 's/^        "/    "/' setup.py; sed -i 's/^  ]/    ]/' setup.py
###ACTION_DELIMITER###
sed -i '8s/open( /open(/; 8s/ )/)/' setup.py; sed -i 's/[[:space:]]*$//' setup.py; sed -i 's/^  packages=/    packages=/' setup.py; sed -i 's/^      "/    "/' setup.py; sed -i 's/^  ]/    ]/' setup.py; sed -i 's/^  )/)/' setup.py
###ACTION_DELIMITER###
sed -i '8s/open( /open(/; 8s/ )/)/' setup.py; sed -i 's/^  install_requires=/    install_requires=/' setup.py; sed -i 's/^    \[/      [/' setup.py; sed -i 's/^      "/        "/' setup.py; sed -i 's/^    ]/      ]/' setup.py; sed -i 's/^  extras_require=/    extras_require=/' setup.py; sed -i 's/^  )/)/' setup.py
###ACTION_DELIMITER###
sed -i -e '8s/open( /open(/' -e '8s/ )/)/' -e 's/[[:space:]]*$//' -e 's/^  packages=/    packages=/' -e 's/^    \[/      [/' -e 's/^      "/        "/' -e 's/^    ]/      ]/' setup.py
###ACTION_DELIMITER###
sed -i -e '8s/open( /open(/' -e '8s/ )/)/' -e 's/^  packages=/    packages=/' -e 's/^      "/        "/' -e 's/^    ]/      ]/' -e 's/^  )/)/' setup.py
###ACTION_DELIMITER###
sed -i -e 's/open( /open(/' -e 's/ )/)/' -e 's/[[:space:]]*$//' -e 's/^  packages=/    packages=/' -e 's/^    "/        "/' -e 's/^  ]/    ]/' -e 's/^  )/)/' setup.py
###ACTION_DELIMITER###
sed -i -e 's/open( /open(/' -e 's/ )/)/' -e 's/[[:space:]]*$//' -e 's/^  packages=/    packages=/' -e 's/^    "/        "/' -e 's/^    ]/    ]/' -e 's/^    extras_require=/    extras_require=/' -e 's/^        "/            "/' -e 's/^    }/    }/' setup.py
###ACTION_DELIMITER###
sed -i -e 's/open( /open(/' -e 's/ )/)/' -e 's/[[:space:]]*$//' -e 's/^  packages=/    packages=/' -e 's/^    "/        "/' -e 's/^  ]/    ]/' -e 's/^  }/    }/' -e 's/^  )/)/' setup.py
###ACTION_DELIMITER###
sed -i -e 's/open( "README.md" )/open("README.md")/' -e 's/^  packages=/    packages=/' -e 's/^    "/        "/' -e 's/^  ]/    ]/' -e 's/^  }/    }/' setup.py
###ACTION_DELIMITER###
sed -i -e 's/open( "README.md" )/open("README.md")/' -e 's/^  packages=/    packages=/' -e 's/^    "/        "/' -e 's/^  ]/    ]/' -e 's/^      "/            "/' -e 's/^  }/    }/' -e 's/[[:space:]]*$//' setup.py
###ACTION_DELIMITER###
sed -i -e 's/open( "README.md" )/open("README.md")/' -e 's/^  packages=/    packages=/' -e 's/^    "/        "/' -e 's/^  ]/    ]/' -e 's/^      "/        "/' -e 's/[[:space:]]*$//' setup.py
###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i -e 's/open( "README.md" )/open("README.md")/' -e 's/^  packages=/    packages=/' -e 's/^    "/        "/' -e 's/^  ]/    ]/' -e 's/^      "/        "/' -e 's/[[:space:]]*$//' setup.py
###ACTION_DELIMITER###
sed -i -e 's/open( "README.md" )/open("README.md")/' -e 's/^  packages=/    packages=/' -e 's/^    "/        "/' -e 's/^      "/        "/' -e 's/^  ]/    ]/' -e 's/^  }/    }/' -e 's/^  )/)/' -e 's/[[:space:]]*$//' setup.py
###ACTION_DELIMITER###
sed -i -e 's/open( "README.md" )/open("README.md")/' -e 's/^  packages=/    packages=/' -e 's/^      "/        "/' -e 's/^  ]/    ]/' -e 's/^        "/            "/' -e 's/^  }/    }/' -e 's/[[:space:]]*$//' setup.py
###ACTION_DELIMITER###
sed -i -e 's/open( "README.md" )/open("README.md")/' -e 's/[[:space:]]*$//' -e 's/^  packages=/    packages=/' -e 's/^    "/        "/' -e 's/^      "/        "/' -e 's/^  ]/    ]/' -e 's/^  }/    }/' setup.py
###ACTION_DELIMITER###
sed -i -e 's/open( "README.md" )/open("README.md")/' -e 's/[[:space:]]*$//' -e 's/^  packages=/    packages=/' -e 's/^    "/        "/' -e 's/^      "/        "/' -e 's/^  ]/    ]/' -e 's/^  }/    }/' setup.py
###ACTION_DELIMITER###
sed -i -e 's/open( "README.md" )/open("README.md")/' -e 's/[[:space:]]*$//' -e 's/^  packages=/    packages=/' -e 's/^    "/        "/' -e 's/^      "/            "/' -e 's/^  ]/    ]/' -e 's/^  }/    }/' setup.py
###ACTION_DELIMITER###
sed -i -e 's/open( "README.md" )/open("README.md")/' -e 's/[[:space:]]*$//' -e 's/^  packages=/    packages=/' -e 's/^    "/        "/' -e 's/^      "/            "/' -e 's/^  ]/    ]/' -e 's/^  }/    }/' setup.py
###ACTION_DELIMITER###
sed -i -e 's/open( "README.md" )/open("README.md")/' -e 's/[[:space:]]*$//' -e 's/^  packages=/    packages=/' -e 's/^    "/        "/' -e 's/^      "/        "/' -e 's/^  ]/    ]/' -e 's/^  }/    }/' setup.py
###ACTION_DELIMITER###
echo 'python run-tests.py --unit --allbooks' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install scipy==1.10.1
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python run-tests.py --unit --allbooks

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
python run-tests.py --unit --allbooks

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
python run-tests.py --unit --allbooks

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
RUN git clone https://github.com/pybamm-team/PyBaMM.git /home/PyBaMM

WORKDIR /home/PyBaMM
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pybamm-team", "PyBaMM_33_to_unknown")
class PYBAMM_33_TO_UNKNOWN(Instance):
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
        # Line-by-line parsing to handle test names and statuses
        previous_line = None
        for line in log.split('\n'):
            line = line.strip()
            if not line:
                continue
            # Check if line contains status indicator '...'
            if '...' in line:
                # Split into test part (before '...') and status part (after '...')
                test_part, status_part = line.rsplit('...', 1)
                test_part = test_part.strip()
                status_part = status_part.strip()
                # Extract test name (remove line number prefix)
                test_name = test_part.split(']', 1)[-1].strip() if ']' in test_part else test_part
                # Determine status
                status = None
                if status_part.startswith('ok'):
                    status = 'passed'
                elif status_part.startswith('skipped'):
                    status = 'skipped'
                elif status_part.startswith(('FAIL', 'ERROR')):
                    status = 'failed'
                # Handle multi-line tests (use previous line's test name if current test_part is not a test)
                if not test_name.startswith('test_') and previous_line:
                    test_name = previous_line.split(']', 1)[-1].strip() if ']' in previous_line else previous_line
                # Add to appropriate set if valid test name and status
                if test_name.startswith('test_') and status:
                    if status == 'passed':
                        passed_tests.add(test_name)
                    elif status == 'skipped':
                        skipped_tests.add(test_name)
                    elif status == 'failed':
                        failed_tests.add(test_name)
            else:
                # Track previous line for multi-line test names
                previous_line = line if line.startswith('[') else previous_line
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
