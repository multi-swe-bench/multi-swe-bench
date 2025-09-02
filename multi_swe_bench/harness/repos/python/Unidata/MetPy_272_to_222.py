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
                """pip install matplotlib==2.2.5
###ACTION_DELIMITER###
pip install .
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install pytest
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install pint==0.18
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
pip install numpy==1.21.0
###ACTION_DELIMITER###
pip install numpy==1.21.0 matplotlib==3.5.3 scipy==1.10.1 pint==0.18
###ACTION_DELIMITER###
pytest -v
###ACTION_DELIMITER###
cat << 'EOF' > test_commands.sh
#!/bin/bash
python - <<END
import matplotlib.cbook as cbook
if not hasattr(cbook, 'Bunch'):
    class Bunch:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    cbook.Bunch = Bunch
END
pytest -v
EOF
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cat << 'EOF' > test_commands.sh
#!/bin/bash
python - <<END
import matplotlib.cbook as cbook
if not hasattr(cbook, 'Bunch'):
    class Bunch:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    cbook.Bunch = Bunch
import pytest
pytest.main(['-v'])
END
EOF
###ACTION_DELIMITER###
cat << 'EOF' > test_commands.sh
#!/bin/bash
python - <<END
import matplotlib.cbook as cbook
from collections.abc import Iterable

# Inject missing Bunch class
if not hasattr(cbook, 'Bunch'):
    class Bunch:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    cbook.Bunch = Bunch

# Inject missing is_string_like function
if not hasattr(cbook, 'is_string_like'):
    cbook.is_string_like = lambda x: isinstance(x, (str, bytes))

# Ensure iterable is available (Matplotlib 3.5+ may rename it)
if not hasattr(cbook, 'iterable'):
    cbook.iterable = lambda x: isinstance(x, Iterable)

import pytest
pytest.main(['-v'])
END
EOF
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip install .[cdm]
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
pip install pint==0.19
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cat << 'EOF' > test_commands.sh
#!/bin/bash
python - <<END
import matplotlib.cbook as cbook
import matplotlib as mpl
import numpy as np
from collections.abc import Iterable

# Configure matplotlib to avoid text.hinting errors
mpl.rcParams['text.hinting'] = 'auto'

# Inject missing Bunch class
if not hasattr(cbook, 'Bunch'):
    class Bunch:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    cbook.Bunch = Bunch

# Inject missing is_string_like function
if not hasattr(cbook, 'is_string_like'):
    cbook.is_string_like = lambda x: isinstance(x, (str, bytes))

# Ensure iterable is available
if not hasattr(cbook, 'iterable'):
    cbook.iterable = lambda x: isinstance(x, Iterable)

# Make numpy available as np globally (for tests)
globals()['np'] = np

import pytest
pytest.main(['-v'])
END
EOF
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
cat << 'EOF' > test_commands.sh
#!/bin/bash
python - <<END
import matplotlib.cbook as cbook
import matplotlib as mpl
import numpy as np
from collections.abc import Iterable

# Fix text.hinting error by setting to valid value
mpl.rcParams['text.hinting'] = 'auto'

# Inject missing Bunch class
if not hasattr(cbook, 'Bunch'):
    class Bunch:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    cbook.Bunch = Bunch

# Inject missing is_string_like function
if not hasattr(cbook, 'is_string_like'):
    cbook.is_string_like = lambda x: isinstance(x, (str, bytes))

# Ensure iterable is available
if not hasattr(cbook, 'iterable'):
    cbook.iterable = lambda x: isinstance(x, Iterable)

# Make numpy available as np globally
import builtins
builtins.np = np

import pytest
pytest.main(['-v'])
END
EOF
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cat << 'EOF' > test_commands.sh
#!/bin/bash
python - <<END
import matplotlib.cbook as cbook
import matplotlib as mpl
import matplotlib.transforms as transforms
import numpy as np
from collections.abc import Iterable

# Fix text.hinting error
mpl.rcParams['text.hinting'] = 'auto'

# Inject missing Bunch class
if not hasattr(cbook, 'Bunch'):
    class Bunch:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    cbook.Bunch = Bunch

# Inject missing is_string_like function
if not hasattr(cbook, 'is_string_like'):
    cbook.is_string_like = lambda x: isinstance(x, (str, bytes))

# Ensure iterable is available
if not hasattr(cbook, 'iterable'):
    cbook.iterable = lambda x: isinstance(x, Iterable)

# Make numpy and transforms available globally
import builtins
builtins.np = np
builtins.transforms = transforms

import pytest
pytest.main(['-v'])
END
EOF"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
#!/bin/bash
python - <<END
import matplotlib.cbook as cbook
import matplotlib as mpl
import matplotlib.transforms as transforms
import numpy as np
from collections.abc import Iterable

# Fix text.hinting error
mpl.rcParams['text.hinting'] = 'auto'

# Inject missing Bunch class
if not hasattr(cbook, 'Bunch'):
    class Bunch:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    cbook.Bunch = Bunch

# Inject missing is_string_like function
if not hasattr(cbook, 'is_string_like'):
    cbook.is_string_like = lambda x: isinstance(x, (str, bytes))

# Ensure iterable is available
if not hasattr(cbook, 'iterable'):
    cbook.iterable = lambda x: isinstance(x, Iterable)

# Make numpy and transforms available globally
import builtins
builtins.np = np
builtins.transforms = transforms

import pytest
pytest.main(['-v'])
END

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
python - <<END
import matplotlib.cbook as cbook
import matplotlib as mpl
import matplotlib.transforms as transforms
import numpy as np
from collections.abc import Iterable

# Fix text.hinting error
mpl.rcParams['text.hinting'] = 'auto'

# Inject missing Bunch class
if not hasattr(cbook, 'Bunch'):
    class Bunch:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    cbook.Bunch = Bunch

# Inject missing is_string_like function
if not hasattr(cbook, 'is_string_like'):
    cbook.is_string_like = lambda x: isinstance(x, (str, bytes))

# Ensure iterable is available
if not hasattr(cbook, 'iterable'):
    cbook.iterable = lambda x: isinstance(x, Iterable)

# Make numpy and transforms available globally
import builtins
builtins.np = np
builtins.transforms = transforms

import pytest
pytest.main(['-v'])
END

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
python - <<END
import matplotlib.cbook as cbook
import matplotlib as mpl
import matplotlib.transforms as transforms
import numpy as np
from collections.abc import Iterable

# Fix text.hinting error
mpl.rcParams['text.hinting'] = 'auto'

# Inject missing Bunch class
if not hasattr(cbook, 'Bunch'):
    class Bunch:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    cbook.Bunch = Bunch

# Inject missing is_string_like function
if not hasattr(cbook, 'is_string_like'):
    cbook.is_string_like = lambda x: isinstance(x, (str, bytes))

# Ensure iterable is available
if not hasattr(cbook, 'iterable'):
    cbook.iterable = lambda x: isinstance(x, Iterable)

# Make numpy and transforms available globally
import builtins
builtins.np = np
builtins.transforms = transforms

import pytest
pytest.main(['-v'])
END

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
RUN git clone https://github.com/Unidata/MetPy.git /home/MetPy

WORKDIR /home/MetPy
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("Unidata", "MetPy_272_to_222")
class METPY_272_TO_222(Instance):
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
        passed_tests = set()  # type: set[str]
        failed_tests = set()  # type: set[str]
        skipped_tests = set()  # type: set[str]
        import re
        # Parse test lines using regex
        pattern = r'(?:(PASSED|FAILED|SKIPPED)\s+([\w\/]+\.py::\w+))|(?:([\w\/]+\.py::\w+)\s+(PASSED|FAILED|SKIPPED))'
        matches = re.findall(pattern, log)
        for match in matches:
            status_before, test_after, test_before, status_after = match
            if status_before:
                test_name = test_after
                status = status_before
            elif status_after:
                test_name = test_before
                status = status_after
            else:
                continue
            status = status.upper()
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
