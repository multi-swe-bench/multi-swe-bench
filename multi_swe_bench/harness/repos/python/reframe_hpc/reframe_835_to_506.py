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
        return "ubuntu:22.04"
    
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
                """echo 'settings = { "site_configuration": { "systems": { "local": { "descr": "Local system", "hostnames": ["localhost"], "modules_system": "lmod", "partitions": { "local": { "scheduler": "local", "environs": ["default"], "descr": "Local partition", "max_jobs": 4 } } } }, "environs": { "default": { "descr": "Default environment", "modules": [], "cc": "gcc", "cxx": "g++", "ftn": "gfortran" } } }, "logging_config": { "version": 1, "disable_existing_loggers": False, "handlers": { "console": { "class": "logging.StreamHandler", "formatter": "standard" } }, "formatters": { "standard": { "format": "%(asctime)s: %(levelname)s: %(name)s: %(message)s" } }, "loggers": { "reframe": { "handlers": ["console"], "level": "INFO" } } } }' > local_config.py
###ACTION_DELIMITER###
echo -e 'source /etc/profile.d/lmod.sh
reframe -C local_config.py --system local -c test_reframe.py -c unittests -r -v' > test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y build-essential
###ACTION_DELIMITER###
pip3 install -r requirements.txt && pip3 install -e .
###ACTION_DELIMITER###
apt-get update && apt-get install -y python3-pip
###ACTION_DELIMITER###
pip3 install -r requirements.txt && pip3 install -e .
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'class Settings:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard"
            }
        },
        "formatters": {
            "standard": {
                "format": "%(asctime)s: %(levelname)s: %(name)s: %(message)s"
            }
        },
        "loggers": {
            "reframe": {
                "handlers": ["console"],
                "level": "INFO"
            }
        }
    }

    site_configuration = {
        "systems": {
            "local": {
                "descr": "Local system",
                "hostnames": ["localhost"],
                "modules_system": "lmod",
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
        "environs": {
            "default": {
                "descr": "Default environment",
                "modules": [],
                "cc": "gcc",
                "cxx": "g++",
                "ftn": "gfortran"
            }
        }
    }

settings = Settings()' > local_config.py
###ACTION_DELIMITER###
echo -e 'source /usr/share/lmod/lmod/init/bash
reframe -C local_config.py --system local -c test_reframe.py -c unittests -r -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
dpkg -L lmod | grep 'init/bash'
###ACTION_DELIMITER###
apt-get update && apt-get install -y lmod
###ACTION_DELIMITER###
dpkg -L lmod | grep 'init/bash'
###ACTION_DELIMITER###
echo -e 'source /usr/share/lmod/6.6/init/bash
reframe -C local_config.py --system local -c test_reframe.py -c unittests -r -v' > test_commands.sh
###ACTION_DELIMITER###
echo 'class Settings:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": [{
            "name": "console",
            "type": "stream",
            "class": "logging.StreamHandler",
            "formatter": "standard"
        }],
        "formatters": {
            "standard": {
                "format": "%(asctime)s: %(levelname)s: %(name)s: %(message)s"
            }
        },
        "loggers": {
            "reframe": {
                "handlers": ["console"],
                "level": "INFO"
            }
        }
    }

    site_configuration = {
        "systems": {
            "local": {
                "descr": "Local system",
                "hostnames": ["localhost"],
                "modules_system": "lmod",
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
        "environs": {
            "default": {
                "descr": "Default environment",
                "modules": [],
                "cc": "gcc",
                "cxx": "g++",
                "ftn": "gfortran"
            }
        }
    }

settings = Settings()' > local_config.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'class Settings:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": [{
            "type": "stream",
            "stream": "ext://sys.stdout",
            "formatter": "standard"
        }],
        "formatters": {
            "standard": {
                "format": "%(asctime)s: %(levelname)s: %(name)s: %(message)s"
            }
        },
        "loggers": {
            "reframe": {
                "handlers": ["stream"],
                "level": "INFO"
            }
        }
    }

    site_configuration = {
        "systems": {
            "local": {
                "descr": "Local system",
                "hostnames": ["localhost"],
                "modules_system": "lmod",
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
        "environs": {
            "default": {
                "descr": "Default environment",
                "modules": [],
                "cc": "gcc",
                "cxx": "g++",
                "ftn": "gfortran"
            }
        }
    }

settings = Settings()' > local_config.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'class Settings:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": [{
            "type": "stream",
            "stream": "ext://sys.stdout",
            "formatter": "standard"
        }],
        "formatters": {
            "standard": {
                "format": "%(asctime)s: %(levelname)s: %(name)s: %(message)s"
            }
        },
        "loggers": {
            "reframe": {
                "handlers": ["stream"],
                "level": "INFO"
            }
        }
    }

    site_configuration = {
        "systems": {
            "local": {
                "descr": "Local system",
                "hostnames": ["localhost"],
                "modules_system": "lmod",
                "partitions": {
                    "local": {
                        "scheduler": "local",
                        "environments": ["default"],
                        "descr": "Local partition",
                        "max_jobs": 4
                    }
                }
            }
        },
        "environments": {
            "default": {
                "descr": "Default environment",
                "modules": [],
                "cc": "gcc",
                "cxx": "g++",
                "ftn": "gfortran"
            }
        }
    }

settings = Settings()' > local_config.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'class Settings:
    reframe_module = None
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": [{
            "type": "stream",
            "stream": "ext://sys.stdout",
            "formatter": "standard"
        }],
        "formatters": {
            "standard": {
                "format": "%(asctime)s: %(levelname)s: %(name)s: %(message)s"
            }
        },
        "loggers": {
            "reframe": {
                "handlers": ["stream"],
                "level": "INFO"
            }
        }
    }

    site_configuration = {
        "systems": {
            "local": {
                "descr": "Local system",
                "hostnames": ["localhost"],
                "modules_system": "lmod",
                "partitions": {
                    "local": {
                        "scheduler": "local",
                        "environments": ["default"],
                        "descr": "Local partition",
                        "max_jobs": 4
                    }
                }
            }
        },
        "environments": {
            "default": {
                "descr": "Default environment",
                "modules": [],
                "cc": "gcc",
                "cxx": "g++",
                "ftn": "gfortran"
            }
        }
    }

settings = Settings()' > local_config.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
ls -l test_reframe.py unittests; find . -name 'test_reframe.py' -o -name 'unittests'
###ACTION_DELIMITER###
echo -e 'source /usr/share/lmod/6.6/init/bash
pytest -v unittests/
reframe -C local_config.py --system local -c test_reframe.py -r -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cat test_reframe.py
###ACTION_DELIMITER###
echo -e 'source /usr/share/lmod/6.6/init/bash
python3 test_reframe.py --rfm-user-config local_config.py -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source /usr/share/lmod/6.6/init/bash
export MODULEPATH=
python3 test_reframe.py --rfm-user-config local_config.py -v' > test_commands.sh
###ACTION_DELIMITER###
echo 'class Settings:
    reframe_module = None
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": [{
            "type": "stream",
            "stream": "ext://sys.stdout",
            "formatter": "standard"
        }],
        "formatters": {
            "standard": {
                "format": "%(asctime)s: %(levelname)s: %(name)s: %(message)s"
            }
        },
        "loggers": {
            "reframe": {
                "handlers": ["stream"],
                "level": "INFO"
            }
        }
    }

    site_configuration = {
        "systems": {
            "local": {
                "descr": "Local system",
                "hostnames": ["*"],
                "modules_system": "lmod",
                "partitions": {
                    "local": {
                        "scheduler": "local",
                        "environments": ["default"],
                        "descr": "Local partition",
                        "max_jobs": 4
                    }
                }
            }
        },
        "environments": {
            "default": {
                "descr": "Default environment",
                "modules": [],
                "cc": "gcc",
                "cxx": "g++",
                "ftn": "gfortran"
            }
        }
    }

settings = Settings()' > local_config.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
hostname
###ACTION_DELIMITER###
echo 'class Settings:
    reframe_module = None
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": [{
            "type": "stream",
            "stream": "ext://sys.stdout",
            "formatter": "standard"
        }],
        "formatters": {
            "standard": {
                "format": "%(asctime)s: %(levelname)s: %(name)s: %(message)s"
            }
        },
        "loggers": {
            "reframe": {
                "handlers": ["stream"],
                "level": "INFO"
            }
        }
    }

    site_configuration = {
        "systems": {
            "local": {
                "descr": "Local system",
                "hostnames": ["fcdefa52c0e7"],
                "modules_system": "lmod",
                "partitions": {
                    "local": {
                        "scheduler": "local",
                        "environments": ["default"],
                        "descr": "Local partition",
                        "max_jobs": 4
                    }
                }
            }
        },
        "environments": {
            "default": {
                "descr": "Default environment",
                "modules": [],
                "cc": "gcc",
                "cxx": "g++",
                "ftn": "gfortran"
            }
        }
    }

settings = Settings()' > local_config.py
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'source /usr/share/lmod/6.6/init/bash
export MODULEPATH=/usr/share/modulefiles
python3 test_reframe.py --rfm-user-config local_config.py -v' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'source /usr/share/lmod/6.6/init/bash
mkdir -p /usr/share/modulefiles
export MODULEPATH=/usr/share/modulefiles
python3 test_reframe.py --rfm-user-config local_config.py -v' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
source /usr/share/lmod/6.6/init/bash
mkdir -p /usr/share/modulefiles
export MODULEPATH=/usr/share/modulefiles
python3 test_reframe.py --rfm-user-config local_config.py -v

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
source /usr/share/lmod/6.6/init/bash
mkdir -p /usr/share/modulefiles
export MODULEPATH=/usr/share/modulefiles
python3 test_reframe.py --rfm-user-config local_config.py -v

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
source /usr/share/lmod/6.6/init/bash
mkdir -p /usr/share/modulefiles
export MODULEPATH=/usr/share/modulefiles
python3 test_reframe.py --rfm-user-config local_config.py -v

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
FROM ubuntu:22.04

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


@Instance.register("reframe-hpc", "reframe_835_to_506")
class REFRAME_835_TO_506(Instance):
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
        import json
        # Regex pattern to match test execution lines (e.g., "test_name PASSED [  0%]")
        execution_pattern = re.compile(
            r'^(.+?)\s+(PASSED|FAILED|SKIPPED)\s+\[\s*\d+%\]$',
            re.MULTILINE
        )
        # Find all matches in the log
        execution_matches = execution_pattern.findall(log)
        for test_name, status in execution_matches:
            if status == 'PASSED':
                passed_tests.add(test_name)
            elif status == 'FAILED':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
        # Regex pattern to match failed test summary lines (e.g., "FAILED test_name - error")
        failed_summary_pattern = re.compile(
            r'^FAILED\s+(.+?)(?:\s+-.*)?$',
            re.MULTILINE
        )
        failed_summary_matches = failed_summary_pattern.findall(log)
        for test_name in failed_summary_matches:
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
