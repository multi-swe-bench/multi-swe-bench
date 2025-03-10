import re
from typing import Optional, Union

from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.instance import Instance, TestResult
from multi_swe_bench.harness.pull_request import PullRequest


class rootImageBase(Image):
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
        return "gcc:11"

    def image_name(self) -> str:
        return f"{self.pr.org}/{self.pr.repo}".lower()

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

WORKDIR /home/

{code}
RUN apt-get update && \
    apt-get install -y \
    wget \
    tar && \
    wget https://cmake.org/files/v3.20/cmake-3.20.0-linux-x86_64.tar.gz && \
    tar -zxvf cmake-3.20.0-linux-x86_64.tar.gz && \
    mv cmake-3.20.0-linux-x86_64 /opt/cmake && \
    ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake && \
    rm cmake-3.20.0-linux-x86_64.tar.gz

RUN apt-get install -y binutils cmake dpkg-dev libssl-dev git libx11-dev \
libxext-dev libxft-dev libxpm-dev python3 libtbb-dev libgif-dev

{self.clear_env}

"""


class rootImageBaseCpp12(Image):
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
        return "gcc:12"

    def image_name(self) -> str:
        return f"{self.pr.org}/{self.pr.repo}".lower()

    def image_tag(self) -> str:
        return "base-cpp-12"

    def workdir(self) -> str:
        return "base-cpp-12"

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

WORKDIR /home/

{code}
RUN apt-get update && apt-get install -y libbrotli-dev libcurl4-openssl-dev
RUN apt-get install -y clang build-essential cmake
RUN cd /home/ && git clone https://github.com/nlohmann/root_test_data.git

{self.clear_env}

"""


class rootImageBaseCpp7(Image):
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
        return "gcc:7"

    def image_name(self) -> str:
        return f"{self.pr.org}/{self.pr.repo}".lower()

    def image_tag(self) -> str:
        return "base-cpp-7"

    def workdir(self) -> str:
        return "base-cpp-7"

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

WORKDIR /home/

{code}
RUN apt-get update && apt-get install -y libbrotli-dev libcurl4-openssl-dev
RUN apt-get install -y clang build-essential cmake
RUN cd /home/ && git clone https://github.com/nlohmann/root_test_data.git

{self.clear_env}

"""


class rootImageBaseCpp6(Image):
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
        return "gcc:6"

    def image_name(self) -> str:
        return f"{self.pr.org}/{self.pr.repo}".lower()

    def image_tag(self) -> str:
        return "base-cpp-6"

    def workdir(self) -> str:
        return "base-cpp-6"

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

WORKDIR /home/

{code}
RUN apt-get update && apt-get install -y cmake
RUN cd /home/ && git clone https://github.com/nlohmann/root_test_data.git

{self.clear_env}

"""


class rootImageDefault(Image):
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
        # if 2825 <= self.pr.number and self.pr.number <= 3685:
        #     return rootImageBaseCpp12(self.pr, self._config)
        # elif self.pr.number <= 2576:
        #     return rootImageBaseCpp7(self.pr, self._config)

        return rootImageBase(self.pr, self._config)

    def image_name(self) -> str:
        return f"{self.pr.org}/{self.pr.repo}".lower()

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

mkdir -p build

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
cd build
cmake -Dtesting=ON ..
make -j 8
ctest -j 8
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
git apply --whitespace=nowarn /home/test.patch
cd build
cmake -Dtesting=ON ..
make -j 8
ctest -j 8

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
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
cd build
cmake -Dtesting=ON ..
make -j 8
ctest -j 8

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


@Instance.register("root-project", "root")
class root(Instance):
    def __init__(self, pr: PullRequest, config: Config, *args, **kwargs):
        super().__init__()
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    def dependency(self) -> Optional[Image]:
        return rootImageDefault(self.pr, self._config)

    def run(self) -> str:
        return "bash /home/run.sh"

    def test_patch_run(self) -> str:
        return "bash /home/test-run.sh"

    def fix_patch_run(self) -> str:
        return "bash /home/fix-run.sh"

    def parse_log(self, test_log: str) -> TestResult:
        re_pass = re.compile(r"\d*\/\d* *Test *#\d*: *(.*?) *\.* *Passed")
        re_fail = re.compile(r"\d*\/\d* *Test *#\d*: *(.*?) *\.* *Failed")
        re_skip = re.compile(r"\d*\/\d* *Test *#\d*: *(.*?) *\.* *Skipped")

        passed_tests = re_pass.findall(test_log)
        failed_tests = re_fail.findall(test_log)
        skipped_tests = re_skip.findall(test_log)

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
