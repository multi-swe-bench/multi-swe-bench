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
cat package.json
###ACTION_DELIMITER###
yarn install
###ACTION_DELIMITER###
echo -e '#!/bin/bash\nyarn test --verbose' > test_commands.sh
###ACTION_DELIMITER###
chmod +x test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
yarn build
###ACTION_DELIMITER###
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && source ~/.bashrc && nvm install 10 && nvm use 10
###ACTION_DELIMITER###
rm -rf node_modules yarn.lock && yarn install
###ACTION_DELIMITER###
yarn install --ignore-engines
###ACTION_DELIMITER###
yarn build
###ACTION_DELIMITER###
nvm use 20 && rm -rf node_modules yarn.lock && yarn install && yarn build
###ACTION_DELIMITER###
jq '.resolutions["tslib"] = "2.6.2"' package.json > temp.json && mv temp.json package.json && rm -rf node_modules && yarn install --ignore-engines && yarn build
###ACTION_DELIMITER###
apt-get update && apt-get install -y jq
###ACTION_DELIMITER###
jq '.resolutions["tslib"] = "2.6.2"' package.json > temp.json && mv temp.json package.json && rm -rf node_modules yarn.lock && yarn install --ignore-engines && yarn build
###ACTION_DELIMITER###
cd packages/vue && jq '.scripts["build:cjs"] = "tsc --project tsconfig.build.json --skipLibCheck"' package.json > temp.json && mv temp.json package.json && cd ../../ && yarn build
###ACTION_DELIMITER###
sed -i 's/name: string;//' packages/vue/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i '/name:.*,/d' packages/vue/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/Partial<ComponentProps<T>>/PropsWithoutRef<ComponentProps<T>>/' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/Partial<ComponentProps<T>>/Partial<Omit<ComponentProps<T>, '\''ref'\''>>/' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/Partial<ComponentProps<T>>/PropsWithoutRef<ComponentProps<T>>/' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/Partial<ComponentProps<T>>/Omit<ComponentProps<T>, \'ref\'>/' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i "s/Partial<ComponentProps<T>>/Partial<Omit<ComponentProps<T>, 'ref'>>/" packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i "s/Partial<ComponentProps<T>>/Partial<Omit<ComponentProps<T>, 'ref'>>/" packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i "s/Partial<ComponentProps<T>>/Partial<Omit<ComponentProps<T>, 'ref'>>/" packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/Partial<ComponentProps<T>>/PropsWithoutRef<ComponentProps<T>>/' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/Partial<ComponentProps<T>>/PropsWithoutRef<ComponentProps<T>>/' packages/react/src/shared/connect.ts && cat packages/react/src/shared/connect.ts | grep 'PropsWithoutRef' && yarn build
###ACTION_DELIMITER###
sed -i 's/Partial<ComponentProps<T>>/PropsWithoutRef<ComponentProps<T>>/' packages/react/src/shared/connect.ts && grep 'PropsWithoutRef<ComponentProps<T>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/\(props:\s*\)Partial<ComponentProps<T>>/\1PropsWithoutRef<ComponentProps<T>>/' packages/react/src/shared/connect.ts && grep 'PropsWithoutRef<ComponentProps<T>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/\(props:\s*\)Partial<ComponentProps<T>>/\1PropsWithoutRef<ComponentProps<T>>/' packages/react/src/shared/connect.ts && grep 'PropsWithoutRef<ComponentProps<T>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
cat packages/react/src/shared/connect.ts | grep 'Partial<ComponentProps<T>>' && sed -i 's/Partial<ComponentProps<T>>/PropsWithoutRef<ComponentProps<T>>/' packages/react/src/shared/connect.ts && grep 'PropsWithoutRef<ComponentProps<T>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i '5s/Partial<ComponentProps<T>>/PropsWithoutRef<ComponentProps<T>>/' packages/react/src/shared/connect.ts && sed -n '5p' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/(props:\s*Partial<ComponentProps<T>>)/(props: PropsWithoutRef<ComponentProps<T>>)/' packages/react/src/shared/connect.ts && grep 'PropsWithoutRef<ComponentProps<T>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/Partial<ComponentProps<T>>/Partial<PropsWithoutRef<ComponentProps<T>>>/g' packages/react/src/shared/connect.ts && grep 'Partial<PropsWithoutRef<ComponentProps<T>>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/\(props:\s*\)Partial<ComponentProps<T>>/\1PropsWithoutRef<ComponentProps<T>>/' packages/react/src/shared/connect.ts && grep 'PropsWithoutRef<ComponentProps<T>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/Partial<ComponentProps<T>>/PropsWithoutRef<ComponentProps<T>>/' packages/react/src/shared/connect.ts && grep 'PropsWithoutRef<ComponentProps<T>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###

###ACTION_DELIMITER###

###ACTION_DELIMITER###
sed -i 's/Partial<ComponentProps<T>>/PropsWithoutRef<ComponentProps<T>>/' packages/react/src/shared/connect.ts && grep 'PropsWithoutRef<ComponentProps<T>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/\(props:\s*\)Partial<ComponentProps<T>>/\1PropsWithoutRef<ComponentProps<T>>/' packages/react/src/shared/connect.ts && grep 'PropsWithoutRef<ComponentProps<T>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i '/forwardRef/ s/\(props\s*:\s*\)Partial<ComponentProps<T>>/\1PropsWithoutRef<ComponentProps<T>>/' packages/react/src/shared/connect.ts && grep 'PropsWithoutRef<ComponentProps<T>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/\(forwardRef.*props:\s*\)Partial<ComponentProps<T>>/\1Partial<PropsWithoutRef<ComponentProps<T>>>/g' packages/react/src/shared/connect.ts && grep 'Partial<PropsWithoutRef<ComponentProps<T>>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/Partial<ComponentProps<T>>/Partial<PropsWithoutRef<ComponentProps<T>>>/g' packages/react/src/shared/connect.ts && grep 'Partial<PropsWithoutRef<ComponentProps<T>>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/\(props:\s*\)Partial<ComponentProps<T>>/\1Partial<PropsWithoutRef<ComponentProps<T>>>/g' packages/react/src/shared/connect.ts && grep 'Partial<PropsWithoutRef<ComponentProps<T>>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/.*props:\s*Partial<ComponentProps<T>>/  props: Partial<PropsWithoutRef<ComponentProps<T>>>/' packages/react/src/shared/connect.ts && grep 'Partial<PropsWithoutRef<ComponentProps<T>>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/\(forwardRef.*props:\s*\)Partial<ComponentProps<T>>/\1Partial<PropsWithoutRef<ComponentProps<T>>>/g' packages/react/src/shared/connect.ts && grep 'Partial<PropsWithoutRef<ComponentProps<T>>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/Partial<ComponentProps<T>>/Partial<PropsWithoutRef<ComponentProps<T>>>/g' packages/react/src/shared/connect.ts && grep 'Partial<PropsWithoutRef<ComponentProps<T>>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
cat packages/react/src/shared/connect.ts | grep 'props:' && sed -i 's/\(props:\s*\)Partial<ComponentProps<T>>/\1PropsWithoutRef<Partial<ComponentProps<T>>>/g' packages/react/src/shared/connect.ts && grep 'PropsWithoutRef<Partial<ComponentProps<T>>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
sed -i 's/Partial<React.ComponentProps<T>>/PropsWithoutRef<React.ComponentProps<T>>/' packages/react/src/shared/connect.ts && grep 'PropsWithoutRef<React.ComponentProps<T>>' packages/react/src/shared/connect.ts && yarn build
###ACTION_DELIMITER###
""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
yarn test --verbose

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
#!/bin/bash
yarn test --verbose

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
#!/bin/bash
yarn test --verbose

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
RUN git clone https://github.com/alibaba/formily.git /home/formily

WORKDIR /home/formily
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("alibaba", "formily_3481_to_3305")
class FORMILY_3481_TO_3305(Instance):
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

        # Pattern to remove log numbers (e.g., [   16])
        log_number_pattern = re.compile(r"^\[\s*\d+\]\s*")
        test_suite_pattern = re.compile(r"^(PASS|FAIL|SKIP) (.*)$")
        lines = log.split("\n")
        current_test = None  # (status, indent_level, parts)
        current_groups = []  # List of (indent_level, group_name) to track test groups
        current_suite = ""  # Current test suite path
        status_map = {"✓": "passed", "✔": "passed", "✕": "failed", "○": "skipped"}
        for line in lines:
            # Remove leading log number
            line = log_number_pattern.sub("", line)
            # Check for test suite lines
            suite_match = test_suite_pattern.match(line)
            if suite_match:
                current_suite = suite_match.group(2)
                current_groups = []  # Reset groups for new suite
                continue
            # Check for test markers
            marker_found = False
            for marker in status_map.keys():
                # Use regex to find marker with whitespace around it
                match = re.search(rf"(^|\s){re.escape(marker)}(?=\s|$|[:(])", line)
                if match:
                    marker_pos = match.start()
                    # Found a test line
                    if current_test:
                        # Add previous test
                        status, _, parts = current_test
                        group_names = [g[1] for g in current_groups]
                        test_name = " ".join(group_names + parts).strip()
                        if test_name:
                            if status == "passed":
                                passed_tests.add(test_name)
                            elif status == "failed":
                                failed_tests.add(test_name)
                            elif status == "skipped":
                                skipped_tests.add(test_name)
                        current_test = None
                    # Calculate indent level (spaces before the marker)
                    indent_level = (
                        marker_pos + 1
                    )  # +1 because marker is preceded by a space
                    # Extract test part (after marker, before duration)
                    test_part = line[match.end() :]
                    # Remove leading punctuation/whitespace after marker
                    test_part = re.sub(r"^[✓✔✕○\s:(]+", "", test_part)
                    # Remove duration info
                    test_part = re.sub(r"\s*\(\d+\s*ms\)$", "", test_part)
                    test_part = test_part.strip()
                    # Filter out test parts with file patterns
                    if re.search(
                        r"[\*\.\/\\]|(\.less$)|(\.scss$)|(\.js$)|(\*\*)", test_part
                    ):
                        current_test = None
                        marker_found = False
                        continue
                    current_test = (status_map[marker], indent_level, [test_part])
                    marker_found = True
                    break
            if not marker_found:
                # Check if line is a test group (no marker but has indentation)
                stripped_line = line.lstrip()
                # Filter out non-test group lines (e.g., file patterns)
                if re.search(r"[✓✔✕○]", stripped_line) or re.match(
                    r"[\*\.\/\\]|(\.less$)|(\.scss$)|(\.js$)|(\*\*)", stripped_line
                ):
                    continue
                if stripped_line and not current_test:
                    group_indent = len(line) - len(stripped_line)
                    # Update current_groups by removing groups with higher indent
                    while current_groups and current_groups[-1][0] >= group_indent:
                        current_groups.pop()
                    current_groups.append((group_indent, stripped_line))
            if not marker_found and current_test:
                # Check if current line is part of the test name
                status, indent_level, parts = current_test
                # Calculate current line's indent level
                stripped_line = line.lstrip()
                # Filter out non-test group lines (e.g., file patterns)
                if re.search(r"[✓✔✕○]", stripped_line) or re.match(
                    r"[\*\.\/\\]|(\.less$)|(\.scss$)|(\.js$)|(\*\*)", stripped_line
                ):
                    continue
                current_indent = len(line) - len(stripped_line)
                if current_indent >= indent_level:
                    # Part of the test name
                    test_part = stripped_line
                    if " (" in test_part:
                        test_part = test_part.split(" (")[0]
                    test_part = test_part.strip()
                    # Filter out test parts with file patterns
                    if re.search(
                        r"[\*\.\/\\]|(\.less$)|(\.scss$)|(\.js$)|(\*\*)", test_part
                    ):
                        current_test = None
                        marker_found = False
                        continue
                    parts.append(test_part)
                else:
                    # End of test name
                    group_names = [g[1] for g in current_groups]
                    test_name = " ".join(group_names + parts).strip()
                    if test_name:
                        if status == "passed":
                            passed_tests.add(test_name)
                        elif status == "failed":
                            failed_tests.add(test_name)
                        elif status == "skipped":
                            skipped_tests.add(test_name)
                    current_test = None
        # Add the last test if any
        if current_test:
            status, _, parts = current_test
            group_names = [g[1] for g in current_groups]
            test_name = " ".join(group_names + parts).strip()
            if test_name:
                if status == "passed":
                    passed_tests.add(test_name)
                elif status == "failed":
                    failed_tests.add(test_name)
                elif status == "skipped":
                    skipped_tests.add(test_name)
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
