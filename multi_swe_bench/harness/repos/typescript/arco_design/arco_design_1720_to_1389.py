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
                """ls -la
###ACTION_DELIMITER###
npm install -g yarn
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo 'yarn test --verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn build:cjs
 yarn test:client --verbose
 yarn test:node --verbose' > test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
yarn icon
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
yarn add --dev react-sortable-hoc react-sticky react-resizable
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/test:client --verbose/test:client --verbose -u/' test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
yarn add --dev react-dnd react-easy-crop
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo "module.exports = { moduleNameMapper: { '^@arco-design/web-react/(.*)$': '<rootDir>/$1' }, transformIgnorePatterns: [ '/node_modules/(?!(react-dnd|dnd-core|@react-dnd|react-easy-crop)/)' ], transform: { '^.+\\.(ts|tsx)$': 'ts-jest', '^.+\\.(js|jsx)$': 'babel-jest' } };" > jest.config.js
###ACTION_DELIMITER###
echo "module.exports = { moduleNameMapper: { '^@arco-design/web-react/(.*)$': '<rootDir>/$1' }, transformIgnorePatterns: [ '/node_modules/(\?!(react-dnd|dnd-core|@react-dnd|react-easy-crop)/)' ], transform: { '^.+\\.(ts|tsx)$': 'ts-jest', '^.+\\.(js|jsx)$': 'babel-jest' } };" > jest.config.js
###ACTION_DELIMITER###
cat << 'EOF' > jest.config.js
module.exports = {
  moduleNameMapper: {
    '^@arco-design/web-react/(.*)$': '<rootDir>/$1'
  },
  transformIgnorePatterns: [
    '/node_modules/(?!(react-dnd|dnd-core|@react-dnd|react-easy-crop)/)'
  ],
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest',
    '^.+\\.(js|jsx)$': 'babel-jest'
  }
};
EOF
###ACTION_DELIMITER###
cat jest.config.js
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
cat << 'EOF' > jest.config.js
module.exports = {
  moduleNameMapper: {
    '^@arco-design/web-react/(.*)$': '<rootDir>/\$1'
  },
  transformIgnorePatterns: [
    '/node_modules/(?!(react-dnd|dnd-core|@react-dnd|react-easy-crop)/)'
  ],
  transform: {
    '^.+\.(ts|tsx|js|jsx)$': 'babel-jest'
  }
};
EOF
###ACTION_DELIMITER###
sed -i 's/test:client --verbose -u/test:client --verbose -u --config jest.config.js/' test_commands.sh
###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
cat << 'EOF' > .babelrc
{
  "presets": [
    "@babel/preset-env",
    "@babel/preset-react",
    "@babel/preset-typescript"
  ]
}
EOF
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
cat << 'EOF' > jest.config.js
module.exports = {
  moduleNameMapper: {
    '^@arco-design/web-react/(.*)$': '<rootDir>/es/$1'
  },
  transformIgnorePatterns: [
    '/node_modules/(?!(react-dnd|dnd-core|@react-dnd|react-easy-crop)/)'
  ],
  transform: {
    '^.+\.(ts|tsx|js|jsx)$': 'babel-jest'
  }
};
EOF
###ACTION_DELIMITER###
cat << 'EOF' > jest.config.js
module.exports = {
  moduleNameMapper: {
    '^@arco-design/web-react$': '<rootDir>/es',
    '^@arco-design/web-react/(.*)$': '<rootDir>/es/$1'
  },
  transformIgnorePatterns: [
    '/node_modules/(?!(react-dnd|dnd-core|@react-dnd|react-easy-crop)/)'
  ],
  transform: {
    '^.+\.(ts|tsx|js|jsx)$': 'babel-jest'
  },
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node']
};
EOF
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
cat << 'EOF' > jest.config.js
module.exports = {
  moduleNameMapper: {
    '^@arco-design/web-react/(.*)$': '<rootDir>/es/$1',
    '^@arco-design/web-react$': '<rootDir>/es'
  },
  transformIgnorePatterns: [
    '/node_modules/(?!(react-dnd|dnd-core|@react-dnd|react-easy-crop)/)'
  ],
  transform: {
    '^.+\.(ts|tsx|js|jsx)$': 'babel-jest'
  }
};
EOF
###ACTION_DELIMITER###
sed -i 's/yarn build:cjs/yarn build:cjs && yarn build:es/' test_commands.sh
###ACTION_DELIMITER###
cat << 'EOF' > .babelrc
{
  "presets": [
    ["@babel/preset-env", { "modules": "commonjs" }],
    "@babel/preset-react",
    "@babel/preset-typescript"
  ]
}
EOF
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i 's/yarn build:cjs yarn build:cjsyarn build:cjs yarn build:es/yarn build:cjs && yarn build:es/' test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
cat test_commands.sh
###ACTION_DELIMITER###
sed -i '1s/.*/yarn build:cjs && yarn build:es/' test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'yarn build:cjs && yarn build:es
yarn test:client --verbose -u --config jest.config.js
yarn test:node --verbose' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
cat << 'EOF' > jest.config.js
module.exports = {
  moduleNameMapper: {
    '^@arco-design/web-react/(.*)$': '<rootDir>/es/$1',
    '^@arco-design/web-react$': '<rootDir>/es'
  },
  transformIgnorePatterns: [
    '/node_modules/(?!react-dnd|dnd-core|@react-dnd|react-easy-crop)/'
  ],
  transform: {
    '^.+\.(ts|tsx|js|jsx)$': 'babel-jest'
  }
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
yarn build:cjs && yarn build:es
yarn test:client --verbose -u --config jest.config.js
yarn test:node --verbose

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
yarn build:cjs && yarn build:es
yarn test:client --verbose -u --config jest.config.js
yarn test:node --verbose

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
yarn build:cjs && yarn build:es
yarn test:client --verbose -u --config jest.config.js
yarn test:node --verbose

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

# Choose an appropriate base image based on the project's requirements - replace node:20 with actual base image
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
RUN git clone https://github.com/arco-design/arco-design.git /home/arco-design

WORKDIR /home/arco-design
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("arco-design", "arco_design_1720_to_1389")
class ARCO_DESIGN_1720_TO_1389(Instance):
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
        passed_tests: set[str] = set()  # Tests that passed successfully
        failed_tests: set[str] = set()  # Tests that failed
        skipped_tests: set[str] = set()  # Tests that were skipped
        import re
        import json

        # TODO: Implement the parse_log function
        # Parse passed tests
        passed_pattern = re.compile(r"✓ renders (.*?) correctly")
        passed_tests.update(passed_pattern.findall(log))
        # Parse failed tests from test results and error stacks
        # Capture failed tests from '✕ renders ...' lines
        failed_test_pattern = re.compile(
            r"(?:✕|x|FAILED|●|•)\s+renders\s+([^/]+/demo/[^.]+\.md)(?:\s+correctly.*)?\s*",
            re.IGNORECASE,
        )
        failed_matches = failed_test_pattern.findall(log)
        for test_name in failed_matches:
            if test_name:
                failed_tests.add(test_name.strip())
        # Capture failed tests from error stacks (e.g., components/Tabs/__demo__/drag.md:26:17)
        failed_stack_pattern = re.compile(
            r"components/([^:]+?\.md):"
        )  # Capture any .md file under components
        stack_matches = failed_stack_pattern.findall(log)
        for match in stack_matches:
            test_name = match.replace("__demo__", "demo").replace("__test__", "demo")
            failed_tests.add(test_name)
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
