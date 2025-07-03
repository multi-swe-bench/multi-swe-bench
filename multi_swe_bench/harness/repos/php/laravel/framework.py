import re
from typing import Optional, Union

from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.instance import Instance, TestResult
from multi_swe_bench.harness.pull_request import PullRequest


class ImageBase(Image):
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
        return "php:8.2-cli"

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



WORKDIR /home/

{self.global_env}
{code}

RUN apt-get update && apt-get install -y \
    git \
    unzip \
    libpq-dev \
    libgmp-dev \
    && docker-php-ext-install pdo_mysql pdo_pgsql gmp ftp

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

{code}
{self.clear_env}

"""

class ImageBase7(Image):
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
        return "php:7.2-cli"

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



WORKDIR /home/

{self.global_env}

RUN apt-get update && apt-get install -y \
    git \
    unzip \
    libpq-dev \
    libgmp-dev \
    libssl-dev  \
    && docker-php-ext-install pdo_mysql pdo_pgsql gmp ftp

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

{code}
{self.clear_env}

"""

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

    def dependency(self) -> Image | None:
        if self.pr.number <= 34640:
            return ImageBase7(self.pr, self.config)
        else:
            return ImageBase(self.pr, self.config)

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
                "check_git_changes.sh",
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

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "prepare.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git reset --hard
bash /home/check_git_changes.sh
git checkout {pr.base.sha}
bash /home/check_git_changes.sh
composer install --prefer-dist --no-progress --no-suggest --ansi

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
php -d memory_limit=256M vendor/bin/phpunit  --testdox

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git apply /home/test.patch
php -d memory_limit=256M vendor/bin/phpunit  --testdox

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git apply /home/test.patch /home/fix.patch
php -d memory_limit=256M vendor/bin/phpunit  --testdox

""".format(
                    pr=self.pr
                ),
            ),
        ]

    def dockerfile(self) -> str:
        image = self.dependency()
        name = image.image_name()
        tag = image.image_tag()

        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        prepare_commands = "RUN bash /home/prepare.sh"

        return f"""FROM {name}:{tag}

{self.global_env}

{copy_commands}

{prepare_commands}

{self.clear_env}

"""


@Instance.register("laravel", "framework")
class framework(Instance):
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

    def parse_log(self, test_log: str) -> TestResult:
            passed_tests = set()
            failed_tests = set()
            skipped_tests = set()

            current_suite = None

            for line in test_log.splitlines():
                stripped_line = line.strip()

                if re.match(r"^[.s]+\s+\d+\s*/\s*\d+\s*\(\s*\d+%\)$", stripped_line):
                    continue

                suite_match = re.match(r"^(.*?) \((.*?)\)$", stripped_line)
                if suite_match:
                    current_suite = f"{suite_match.group(2)}::{suite_match.group(1).strip()}"
                    continue

                passed_match = re.match(r"^\u2714\s+(.*)$", stripped_line)
                if passed_match and current_suite:
                    test_name = passed_match.group(1).strip()
                    passed_tests.add(f"{current_suite}::{test_name}")
                    continue

                failed_match = re.match(r"^\u2718\s+(.*)$", stripped_line)
                if failed_match and current_suite:
                    test_name = failed_match.group(1).strip()
                    failed_tests.add(f"{current_suite}::{test_name}")
                    continue

                skipped_match = re.match(r"^\u21A9\s+(.*)$", stripped_line)
                if skipped_match and current_suite:
                    test_name = skipped_match.group(1).strip()
                    skipped_tests.add(f"{current_suite}::{test_name}")
                    continue

            return TestResult(
                passed_count=len(passed_tests),
                failed_count=len(failed_tests),
                skipped_count=len(skipped_tests),
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                skipped_tests=skipped_tests,
            )

