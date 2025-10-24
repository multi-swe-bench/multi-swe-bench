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
        return "node:20"

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
                """npm install karma-firefox-launcher --save-dev
###ACTION_DELIMITER###
sed -i 's/browsers: \[.firefox_latest.\]/browsers: ["FirefoxHeadless"]/' tests/karma.conf.js && sed -i '/customLaunchers: {/,/}/c\    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },' tests/karma.conf.js
###ACTION_DELIMITER###
apt-get update && apt-get install -y firefox-esr
###ACTION_DELIMITER###
echo 'xvfb-run -a npm run test:ci -- --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y xvfb
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cat tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/customLaunchers: {/,/}/!b; /}/!b; s/},.*$/,/' tests/karma.conf.js && sed -i '/^      }$/d' tests/karma.conf.js && sed -i '/^    },/d' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/^      }$/d' tests/karma.conf.js && sed -i '/^    },/d' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/^    },$/d' tests/karma.conf.js && sed -i '/^      }$/d' tests/karma.conf.js && sed -i '/^    },$/d' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/^      }$/d' tests/karma.conf.js && sed -i '/^    },$/d' tests/karma.conf.js && sed -i '/^    },$/d' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/^[[:space:]]*}[[:space:]]*,*[[:space:]]*$/d' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '16,17d' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/^[[:space:]]*}[[:space:]]*,*[[:space:]]*$/d' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/customLaunchers: {/,/}/c\    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/customLaunchers: {/,/}/c\    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/customLaunchers: {/,/}/c\    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/customLaunchers: {/,/}/c\    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '16,17d' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/customLaunchers: {/,/}/c\    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/customLaunchers: {/,/}/c\    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/customLaunchers: {/,/}/c\    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/customLaunchers: {/,/client: {/c\    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/customLaunchers: {/,/}/c\    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i 's/browsers: \[.firefox_latest.\]/browsers: ["FirefoxHeadless"],/' tests/karma.conf.js && sed -i '/customLaunchers: {/,/}/c\    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i 's/browsers: \["FirefoxHeadless"\]/browsers: ["FirefoxHeadless"],/' tests/karma.conf.js && sed -i '/customLaunchers: {/,/}/c\    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/^[[:space:]]*}[[:space:]]*}[[:space:]]*,*[[:space:]]*$/d' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/browsers: /,/client: /c\    browsers: ["FirefoxHeadless"],\n    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/browsers: /,/client: /c\    browsers: ["FirefoxHeadless"],\n    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/browsers: /,/client: /c\    browsers: ["FirefoxHeadless"],\n    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/browsers: /,/client: /c\    browsers: ["FirefoxHeadless"],\n    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/browsers: /,/client: /c\    browsers: ["FirefoxHeadless"],\n    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/customLaunchers: {/,/client: /c\    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/browsers: /,/client: /c\    browsers: ["FirefoxHeadless"],\n    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/browsers: /,/client: /c\    browsers: ["FirefoxHeadless"],\n    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/browsers: /,/client: /c\    browsers: ["FirefoxHeadless"],\n    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/browsers: /,/client: /c\    browsers: ["FirefoxHeadless"],\n    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/browsers: /,/client: /c\    browsers: ["FirefoxHeadless"],\n    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/browsers: /,/client: /c\    browsers: ["FirefoxHeadless"],\n    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/browsers: /,/client: /c\    browsers: ["FirefoxHeadless"],\n    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/browsers: /,/client: /c\    browsers: ["FirefoxHeadless"],\n    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/browsers: /,/client: /c\    browsers: ["FirefoxHeadless"],\n    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {' tests/karma.conf.js
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cat tests/karma.conf.js
###ACTION_DELIMITER###
sed -i '/browserify: {/,/paths: \['src'\]/c\    browserify: {\n      debug: true,\n      paths: ['src']\n    },\n    browsers: ["FirefoxHeadless"],\n    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {\n      captureConsole: true,\n      mocha: {"ui": "tdd"}\n    },\n    envPreprocessor: [\n      "TEST_ENV"\n    ],\n    files: [\n      "tests/**/*.test.js",\n      { pattern: "examples/_sounds/click.ogg", included: false, served: true },\n      { pattern: "examples/_images/mozvr.png", included: false, served: true }\n    ],\n    frameworks: ["mocha", "sinon-chai", "chai-shallow-deep-equal", "browserify"],\n    preprocessors: {\n      "tests/**/*.js": ["browserify", "env"]\n    },\n    reporters: ["mocha"]\n  });\n};' tests/karma.conf.js
###ACTION_DELIMITER###
sed -i 's|browserify: {.*|browserify: {\n      debug: true,\n      paths: ["src"]\n    },\n    browsers: ["FirefoxHeadless"],\n    customLaunchers: {\n      FirefoxHeadless: {\n        base: "Firefox",\n        flags: ["--headless", "--no-sandbox", "--disable-gpu"]\n      }\n    },\n    client: {\n      captureConsole: true,\n      mocha: {"ui": "tdd"}\n    },\n    envPreprocessor: [\n      "TEST_ENV"\n    ],\n    files: [\n      "tests/**/*.test.js",\n      { pattern: "examples/_sounds/click.ogg", included: false, served: true },\n      { pattern: "examples/_images/mozvr.png", included: false, served: true }\n    ],\n    frameworks: ["mocha", "sinon-chai", "chai-shallow-deep-equal", "browserify"],\n    preprocessors: {\n      "tests/**/*.js": ["browserify", "env"]\n    },\n    reporters: ["mocha"]\n  });\n};' tests/karma.conf.js
###ACTION_DELIMITER###
cat << 'EOF' > tests/karma.conf.js
'use strict';
module.exports = function (config) {
  config.set({
    basePath: '../',
    browserify: {
      debug: true,
      paths: ['src']
    },
    browsers: ['FirefoxHeadless'],
    customLaunchers: {
      FirefoxHeadless: {
        base: 'Firefox',
        flags: ['--headless', '--no-sandbox', '--disable-gpu']
      }
    },
    client: {
      captureConsole: true,
      mocha: { 'ui': 'tdd' }
    },
    envPreprocessor: [
      'TEST_ENV'
    ],
    files: [
      'tests/**/*.test.js',
      { pattern: 'examples/_sounds/click.ogg', included: false, served: true },
      { pattern: 'examples/_images/mozvr.png', included: false, served: true }
    ],
    frameworks: ['mocha', 'sinon-chai', 'chai-shallow-deep-equal', 'browserify'],
    preprocessors: {
      'tests/**/*.js': ['browserify', 'env']
    },
    reporters: ['mocha']
  });
};
EOF
###ACTION_DELIMITER###
""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
xvfb-run -a npm run test:ci -- --verbose

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
xvfb-run -a npm run test:ci -- --verbose

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
xvfb-run -a npm run test:ci -- --verbose

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
FROM node:20

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
RUN git clone https://github.com/aframevr/aframe.git /home/aframe

WORKDIR /home/aframe
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("aframevr", "aframe_1094_to_843")
class AFRAME_1094_TO_843(Instance):
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

        # Remove ANSI escape codes
        log_clean = re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", log)
        lines = log_clean.split("\n")
        hierarchy = []
        for line in lines:
            # Process test lines with ✔/✖ and optional (skipped)
            test_match = re.match(r"^(\s+)([✔✖])(\s+)(.*?)(\s*\(skipped\))?$", line)
            if test_match:
                leading_spaces = test_match.group(1)
                symbol = test_match.group(2)
                test_name_part = test_match.group(4).strip()
                skipped = test_match.group(5) is not None
                level = len(leading_spaces) // 2  # Assume 2 spaces per hierarchy level
                current_hierarchy = hierarchy[: level - 1]
                full_test_name = " ".join(current_hierarchy + [test_name_part])
                if skipped:
                    skipped_tests.add(full_test_name)
                else:
                    if symbol == "✔":
                        passed_tests.add(full_test_name)
                    elif symbol == "✖":
                        failed_tests.add(full_test_name)
                continue
            # Process group lines to build hierarchy
            group_match = re.match(r"^(\s+)(\w.*)$", line)
            if group_match:
                leading_spaces = group_match.group(1)
                group_name = group_match.group(2).strip()
                level = len(leading_spaces) // 2
                hierarchy = hierarchy[: level - 1] + [group_name]
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
