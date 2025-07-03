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
        return "php:8.1-cli"

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
    zlib1g-dev \
    libicu-dev \
    && docker-php-ext-install intl

RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

{code}
{self.clear_env}

"""
class ImageBase7_2(Image):
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
        return "base7_2"

    def workdir(self) -> str:
        return "base7_2"

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
    zlib1g-dev \
    libicu-dev \
    && docker-php-ext-install intl

RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

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
        if self.pr.number <= 10314:
            return ImageBase7_2(self.pr, self.config)
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
composer install --prefer-dist --no-progress --no-suggest --ansi  || true
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
php -d memory_limit=256M vendor/bin/simple-phpunit --testdox
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
php -d memory_limit=256M vendor/bin/simple-phpunit --testdox

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
php -d memory_limit=256M vendor/bin/simple-phpunit --testdox

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


@Instance.register("composer", "composer")
class composer(Instance):
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

        current_class = None
        for line in test_log.splitlines():
            # 情况1：ANSI格式下划线类名
            class_match_ansi = re.search(r'\x1b\[4m(.+?)\x1b\[0m', line)
            if class_match_ansi:
                current_class = class_match_ansi.group(1).strip()
                continue

            # 情况2：纯文本类名（旧版phpunit输出），没有任何缩进和符号
            class_match_plain = re.match(r'^[A-Z][\w\\]+$', line.strip())
            if class_match_plain:
                current_class = line.strip()
                continue

            if not current_class:
                continue

            # ANSI格式结果匹配
            match_ansi = re.search(r'\x1b\[\d{2}m([✔✘↩])\x1b\[0m\s+(.*)', line)
            if match_ansi:
                symbol, name = match_ansi.groups()
                name = re.sub(r'\x1b\[[0-9;]*m', '', name).strip()
                full_name = f"{current_class}::{name}"
                if symbol == '✔':
                    passed_tests.add(full_name)
                elif symbol == '✘':
                    failed_tests.add(full_name)
                elif symbol == '↩':
                    skipped_tests.add(full_name)
                continue

            # 新增：纯文本格式 [x] / [ ] 表示测试状态
            match_plain = re.match(r'^\s*\[(.)\]\s+(.*)', line)
            if match_plain:
                symbol, name = match_plain.groups()
                name = name.strip()
                full_name = f"{current_class}::{name}"
                if symbol.lower() == 'x':
                    passed_tests.add(full_name)
                elif symbol == ' ':
                    failed_tests.add(full_name)
                continue

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )