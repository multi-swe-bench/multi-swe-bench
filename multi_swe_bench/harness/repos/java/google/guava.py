import re
import textwrap
from typing import Optional, Union

from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.instance import Instance, TestResult
from multi_swe_bench.harness.pull_request import PullRequest


class GuavaImageBase(Image):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    @property
    def config(self) -> Config:
        return self._config

    def dependency(self) -> Union[str, "Image"]:
        return "ubuntu:22.04"

    def image_tag(self) -> str:
        return "base"

    def workdir(self) -> str:
        return "base"

    def files(self) -> list[File]:
        return []

    def dockerfile(self) -> str:
        image_name = self.dependency()
        if isinstance(image_name, Image):
            image_name = image_name.image_full_name()

        if self.config.need_clone:
            code = f"RUN git clone https://github.com/{self.pr.org}/{self.pr.repo}.git /home/{self.pr.repo}"
        else:
            code = f"COPY {self.pr.repo} /home/{self.pr.repo}"

        return f"""FROM {image_name}

{self.global_env}

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

WORKDIR /home/
RUN apt-get update && apt-get install -y git openjdk-17-jdk maven
# install swe-rex for sweagent:
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv
RUN pip3 install pipx && \
    pipx ensurepath && \
    pipx install swe-rex

{code}

{self.clear_env}
"""


class GuavaImageDefault(Image):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    @property
    def config(self) -> Config:
        return self._config

    def dependency(self) -> Optional[Image]:
        return GuavaImageBase(self.pr, self._config)

    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:
        return [
            File(".", "fix.patch", f"{self.pr.fix_patch}"),
            File(".", "test.patch", f"{self.pr.test_patch}"),
            File(
                ".", "check_git_changes.sh",
                """#!/bin/bash
set -e
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "check_git_changes: Not inside a git repository"
  exit 1
fi
if [[ -n $(git status --porcelain) ]]; then
  echo "check_git_changes: Uncommitted changes"
  exit 1
fi
echo "check_git_changes: No uncommitted changes"
exit 0
""",
            ),
            File(
                ".", "prepare.sh",
                f"""#!/bin/bash
set -e
cd /home/{self.pr.repo}
git reset --hard
bash /home/check_git_changes.sh
git checkout {self.pr.base.sha}
bash /home/check_git_changes.sh

mvn clean test -DfailIfNoTests=false || true
""",
            ),
            File(
                ".", "run.sh",
                f"""#!/bin/bash
set -e
cd /home/{self.pr.repo}
mvn clean test -DfailIfNoTests=false
""",
            ),
            File(
                ".", "test-run.sh",
                f"""#!/bin/bash
set -e
cd /home/{self.pr.repo}
git apply --whitespace=nowarn /home/test.patch
mvn clean test -DfailIfNoTests=false
""",
            ),
            File(
                ".", "fix-run.sh",
                f"""#!/bin/bash
set -e
cd /home/{self.pr.repo}
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
mvn clean test -DfailIfNoTests=false
""",
            ),
        ]

    def dockerfile(self) -> str:
        image = self.dependency()
        name = image.image_name()
        tag = image.image_tag()

        copy_commands = "\n".join(f"COPY {file.name} /home/" for file in self.files())
        prepare_commands = "RUN bash /home/prepare.sh"

        return f"""FROM {name}:{tag}

{self.global_env}

{copy_commands}

{prepare_commands}

{self.clear_env}
"""


@Instance.register("google", "guava")
class Guava(Instance):
    def __init__(self, pr: PullRequest, config: Config, *args, **kwargs):
        super().__init__()
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    def dependency(self) -> Optional[Image]:
        return GuavaImageDefault(self.pr, self._config)

    def run(self, run_cmd: str = "") -> str:
        return run_cmd or "bash /home/run.sh"

    def test_patch_run(self, test_patch_run_cmd: str = "") -> str:
        return test_patch_run_cmd or "bash /home/test-run.sh"

    def fix_patch_run(self, fix_patch_run_cmd: str = "") -> str:
        return fix_patch_run_cmd or "bash /home/fix-run.sh"

    def parse_log(self, test_log: str) -> TestResult:
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()

        re_pass_tests = [
            re.compile(
                r"Running (.+?)\nTests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+), Time elapsed: [\d\.]+ sec"
            )
        ]
        re_fail_tests = [
            re.compile(
                r"Running (.+?)\nTests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+), Time elapsed: [\d\.]+ sec +<<< FAILURE!"
            )
        ]

        for re_pass_test in re_pass_tests:
            tests = re_pass_test.findall(test_log, re.MULTILINE)
            for test in tests:
                name = test[0]
                run, fail, err, skip = map(int, test[1:])
                if run > 0 and fail == 0 and err == 0 and skip != run:
                    passed_tests.add(name)
                elif fail > 0 or err > 0:
                    failed_tests.add(name)
                elif skip == run:
                    skipped_tests.add(name)

        for re_fail_test in re_fail_tests:
            tests = re_fail_test.findall(test_log, re.MULTILINE)
            for test in tests:
                failed_tests.add(test[0])

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
