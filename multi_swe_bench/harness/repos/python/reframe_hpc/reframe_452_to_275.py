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
pip install -r requirements.txt
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
./bin/reframe -C config/cscs.py -r -v
###ACTION_DELIMITER###
./bin/reframe --help
###ACTION_DELIMITER###
./bin/reframe -C config/cscs.py -r --save-log-files --nocolor
###ACTION_DELIMITER###
./bin/reframe -C config/cscs.py --system daint -r --save-log-files --nocolor
###ACTION_DELIMITER###
apt-get update && apt-get install -y environment-modules
###ACTION_DELIMITER###
source /etc/profile.d/modules.sh
###ACTION_DELIMITER###
./bin/reframe -C config/cscs.py --system daint -r --save-log-files --nocolor
###ACTION_DELIMITER###
module --version
###ACTION_DELIMITER###
which modulecmd && echo 'modulecmd found' || echo 'modulecmd not found'
###ACTION_DELIMITER###
export MODULESHOME=/usr/share/modules && source /etc/profile.d/modules.sh && ./bin/reframe -C config/cscs.py --system daint -r --save-log-files --nocolor
###ACTION_DELIMITER###
./bin/reframe -C config/cscs.py --system daint -r --save-log-files --nocolor --debug
###ACTION_DELIMITER###
./bin/reframe -C tutorial/config/settings.py --system generic -r --save-log-files --nocolor
###ACTION_DELIMITER###
./bin/reframe -C tutorial/config/settings.py --system daint --partition login -r --save-log-files --nocolor
###ACTION_DELIMITER###
./bin/reframe -C tutorial/config/settings.py --system daint --partition login -r --force-local --save-log-files --nocolor
###ACTION_DELIMITER###
./bin/reframe -C tutorial/config/settings.py --system daint --partition login -r --force-local --skip-system-check --save-log-files --nocolor
###ACTION_DELIMITER###
export REFRAME_MODULES_SYSTEM=nomod && ./bin/reframe -C tutorial/config/settings.py --system daint --partition login -r --force-local --skip-system-check --save-log-files --nocolor
###ACTION_DELIMITER###
bash -c 'source /etc/profile.d/modules.sh && ./bin/reframe -C tutorial/config/settings.py --system daint --partition login -r --force-local --save-log-files --nocolor'
###ACTION_DELIMITER###
echo 'class ReframeSettings:
    site_configuration = {
        "systems": {
            "docker": {
                "descr": "Docker container",
                "hostnames": ["docker"],
                "modules_system": "nomod",
                "partitions": {
                    "local": {
                        "scheduler": "local",
                        "environs": ["default"],
                        "descr": "Local partition",
                        "max_jobs": 4
                    }
                }
            }
        },
        "environments": {
            "*": {
                "default": {
                    "type": "ProgEnvironment",
                    "modules": []
                }
            }
        }
    }' > minimal_config.py && ./bin/reframe -C minimal_config.py --system docker --partition local -r --force-local --save-log-files --nocolor
###ACTION_DELIMITER###
echo 'class ReframeSettings:
    site_configuration = {
        "systems": {
            "docker": {
                "descr": "Docker container",
                "hostnames": ["docker"],
                "modules_system": "nomod",
                "partitions": {
                    "local": {
                        "scheduler": "local",
                        "environs": ["default"],
                        "descr": "Local partition",
                        "max_jobs": 4
                    }
                }
            }
        },
        "environments": {
            "*": {
                "default": {
                    "type": "ProgEnvironment",
                    "modules": []
                }
            }
        }
    }
settings = ReframeSettings()' > minimal_config.py && ./bin/reframe -C minimal_config.py --system docker --partition local -r --force-local --save-log-files --nocolor
###ACTION_DELIMITER###
echo 'class ReframeSettings:
    site_configuration = {
        "systems": {
            "docker": {
                "descr": "Docker container",
                "hostnames": ["docker"],
                "modules_system": "nomod",
                "partitions": {
                    "local": {
                        "scheduler": "local",
                        "environs": ["default"],
                        "descr": "Local partition",
                        "max_jobs": 4
                    }
                }
            }
        },
        "environments": {
            "*": {
                "default": {
                    "type": "ProgEnvironment",
                    "modules": []
                }
            }
        },
        "logging_config": {
            "level": "INFO",
            "handlers": [
                {
                    "type": "stream",
                    "name": "stdout",
                    "level": "INFO",
                    "format": "%(message)s"
                }
            ]
        }
    }
settings = ReframeSettings()' > minimal_config.py && ./bin/reframe -C minimal_config.py --system docker --partition local -r --force-local --save-log-files --nocolor
###ACTION_DELIMITER###
echo 'class ReframeSettings:
    site_configuration = {
        "systems": {
            "docker": {
                "descr": "Docker container",
                "hostnames": ["docker"],
                "modules_system": "nomod",
                "partitions": {
                    "local": {
                        "scheduler": "local",
                        "environs": ["default"],
                        "descr": "Local partition",
                        "max_jobs": 4
                    }
                }
            }
        },
        "environments": {
            "*": {
                "default": {
                    "type": "ProgEnvironment",
                    "modules": []
                }
            }
        }
    }
    logging_config = {
        "level": "INFO",
        "handlers": [
            {
                "type": "stream",
                "name": "stdout",
                "level": "INFO",
                "format": "%(message)s"
            }
        ]
    }
settings = ReframeSettings()' > minimal_config.py && ./bin/reframe -C minimal_config.py --system docker --partition local -r --force-local --save-log-files --nocolor
###ACTION_DELIMITER###
echo 'class ReframeSettings:
    site_configuration = {
        "systems": {
            "docker": {
                "descr": "Docker container",
                "hostnames": ["docker"],
                "modules_system": "tmod",
                "partitions": {
                    "local": {
                        "scheduler": "local",
                        "environs": ["default"],
                        "descr": "Local partition",
                        "max_jobs": 4
                    }
                }
            }
        },
        "environments": {
            "*": {
                "default": {
                    "type": "ProgEnvironment",
                    "modules": []
                }
            }
        }
    }
    logging_config = {
        "level": "INFO",
        "handlers": [
            {
                "type": "stream",
                "name": "stdout",
                "level": "INFO",
                "format": "%(message)s"
            }
        ]
    }
settings = ReframeSettings()' > minimal_config.py && ./bin/reframe -C minimal_config.py --system docker --partition local -r --force-local --skip-system-check --save-log-files --nocolor
###ACTION_DELIMITER###
echo 'class ReframeSettings:
    site_configuration = {
        "systems": {
            "docker": {
                "descr": "Docker container",
                "hostnames": ["docker"],
                "modules_system": "none",
                "partitions": {
                    "local": {
                        "scheduler": "local",
                        "environs": ["default"],
                        "descr": "Local partition",
                        "max_jobs": 4
                    }
                }
            }
        },
        "environments": {
            "*": {
                "default": {
                    "type": "ProgEnvironment",
                    "modules": []
                }
            }
        }
    }
    logging_config = {
        "level": "INFO",
        "handlers": [
            {
                "type": "stream",
                "name": "stdout",
                "level": "INFO",
                "format": "%(message)s"
            }
        ]
    }
settings = ReframeSettings()' > minimal_config.py && ./bin/reframe -C minimal_config.py --system docker --partition local -r --force-local --skip-system-check --save-log-files --nocolor
###ACTION_DELIMITER###
echo 'class ReframeSettings:
    site_configuration = {
        "systems": {
            "docker": {
                "descr": "Docker container",
                "hostnames": ["docker"],
                "partitions": {
                    "local": {
                        "scheduler": "local",
                        "environs": ["default"],
                        "descr": "Local partition",
                        "max_jobs": 4
                    }
                }
            }
        },
        "environments": {
            "*": {
                "default": {
                    "type": "ProgEnvironment",
                    "modules": []
                }
            }
        }
    }
    logging_config = {
        "level": "INFO",
        "handlers": [
            {
                "type": "stream",
                "name": "stdout",
                "level": "INFO",
                "format": "%(message)s"
            }
        ]
    }
settings = ReframeSettings()' > minimal_config.py && ./bin/reframe -C minimal_config.py --system docker --partition local -r --force-local --skip-system-check --save-log-files --nocolor
###ACTION_DELIMITER###

###ACTION_DELIMITER###
echo 'class ReframeSettings:
    checks_path = ["checks/"]
    checks_path_recurse = True
    site_configuration = {
        "systems": {
            "docker": {
                "descr": "Docker container",
                "hostnames": ["docker"],
                "partitions": {
                    "local": {
                        "scheduler": "local",
                        "environs": ["default"],
                        "descr": "Local partition",
                        "max_jobs": 4
                    }
                }
            }
        },
        "environments": {
            "*": {
                "default": {
                    "type": "ProgEnvironment",
                    "modules": []
                }
            }
        }
    }
    logging_config = {
        "level": "INFO",
        "handlers": [
            {
                "type": "stream",
                "name": "stdout",
                "level": "INFO",
                "format": "%(message)s"
            }
        ]
    }
settings = ReframeSettings()' > minimal_config.py && ./bin/reframe -C minimal_config.py --system docker --partition local -r --force-local --skip-system-check --save-log-files --nocolor
###ACTION_DELIMITER###
echo 'class ReframeSettings:
    reframe_module = "reframe"
    checks_path = ["checks/"]
    checks_path_recurse = True
    site_configuration = {
        "systems": {
            "docker": {
                "descr": "Docker container",
                "hostnames": ["docker"],
                "partitions": {
                    "local": {
                        "scheduler": "local",
                        "environs": ["default"],
                        "descr": "Local partition",
                        "max_jobs": 4
                    }
                }
            }
        },
        "environments": {
            "*": {
                "default": {
                    "type": "ProgEnvironment",
                    "modules": []
                }
            }
        }
    }
    logging_config = {
        "level": "INFO",
        "handlers": [
            {
                "type": "stream",
                "name": "stdout",
                "level": "INFO",
                "format": "%(message)s"
            }
        ]
    }
settings = ReframeSettings()' > minimal_config.py && ./bin/reframe -C minimal_config.py --system docker --partition local -r --force-local --skip-system-check --save-log-files --nocolor
###ACTION_DELIMITER###
echo 'class ReframeSettings:
    reframe_module = "reframe"
    checks_path = ["unittests/", "tutorial/checks/"]
    checks_path_recurse = True
    site_configuration = {
        "systems": {
            "docker": {
                "descr": "Docker container",
                "hostnames": ["docker"],
                "partitions": {
                    "local": {
                        "scheduler": "local",
                        "environs": ["default"],
                        "descr": "Local partition",
                        "max_jobs": 4
                    }
                }
            }
        },
        "environments": {
            "*": {
                "default": {
                    "type": "ProgEnvironment",
                    "modules": []
                }
            }
        }
    }
    logging_config = {
        "level": "INFO",
        "handlers": [
            {
                "type": "stream",
                "name": "stdout",
                "level": "INFO",
                "format": "%(message)s"
            }
        ]
    }
settings = ReframeSettings()' > minimal_config.py && ./bin/reframe -C minimal_config.py --system docker --partition local -r --force-local --skip-system-check --save-log-files --nocolor
###ACTION_DELIMITER###
echo 'class ReframeSettings:
    reframe_module = "reframe"
    checks_path = ["unittests/", "tutorial/checks/"]
    checks_path_recurse = True
    site_configuration = {
        "systems": {
            "docker": {
                "descr": "Docker container",
                "hostnames": ["docker"],
                "partitions": {
                    "local": {
                        "scheduler": "local",
                        "environs": ["default"],
                        "descr": "Local partition",
                        "max_jobs": 4
                    }
                }
            }
        },
        "environments": {
            "*": {
                "default": {
                    "type": "ProgEnvironment",
                    "modules": []
                }
            }
        }
    }
    logging_config = {
        "level": "INFO",
        "handlers": [
            {
                "type": "stream",
                "name": "stdout",
                "level": "INFO",
                "format": "%(message)s"
            }
        ]
    }
settings = ReframeSettings()' > minimal_config.py && ./bin/reframe -C minimal_config.py --system docker --partition local -r --force-local --skip-system-check --save-log-files --nocolor --ignore-check-conflicts
###ACTION_DELIMITER###
echo 'class ReframeSettings:
    reframe_module = "reframe"
    checks_path = ["tutorial/checks/"]
    checks_path_recurse = True
    site_configuration = {
        "systems": {
            "docker": {
                "descr": "Docker container",
                "hostnames": ["docker"],
                "partitions": {
                    "local": {
                        "scheduler": "local",
                        "environs": ["default"],
                        "descr": "Local partition",
                        "max_jobs": 4
                    }
                }
            }
        },
        "environments": {
            "*": {
                "default": {
                    "type": "ProgEnvironment",
                    "modules": []
                }
            }
        }
    }
    logging_config = {
        "level": "INFO",
        "handlers": [
            {
                "type": "stream",
                "name": "stdout",
                "level": "INFO",
                "format": "%(message)s"
            }
        ]
    }
settings = ReframeSettings()' > minimal_config.py && ./bin/reframe -C minimal_config.py --system docker --partition local -r --force-local --skip-system-check --save-log-files --nocolor --ignore-check-conflicts
###ACTION_DELIMITER###
echo '#!/bin/bash
pytest -v' > test_commands.sh && chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
pytest -v

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
pytest -v

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
pytest -v

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
RUN git clone https://github.com/reframe-hpc/reframe.git /home/reframe

WORKDIR /home/reframe
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("reframe-hpc", "reframe_452_to_275")
class REFRAME_452_TO_275(Instance):
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
        import re
        # Regex patterns to match test lines (execution and summary)
        # Pattern 1: Execution lines (test name first, e.g., "test_name PASSED [ 0%]")
        pattern_exec = r'^(.+?)\s+(PASSED|FAILED|SKIPPED)(?:\s*\(.*?\))?\s+\[\s*\d+%\]'
        # Pattern 2: Summary lines (status first, e.g., "FAILED test_name")
        pattern_sum = r'^(PASSED|FAILED|SKIPPED)\s+(.+?)(?:\s*\(.*?\))?$'
        regex_exec = re.compile(pattern_exec)
        regex_sum = re.compile(pattern_sum)
        for line in log.split('\n'):
            stripped_line = line.strip()
            # Check execution line pattern
            match = regex_exec.match(stripped_line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
            else:
                # Check summary line pattern
                match = regex_sum.match(stripped_line)
                if match:
                    status = match.group(1)
                    test_name = match.group(2)
                else:
                    continue  # No match
            # Add to appropriate set
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
