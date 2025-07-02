import re
from typing import Optional, Union
import textwrap
from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.instance import Instance, TestResult
from multi_swe_bench.harness.pull_request import PullRequest
from multi_swe_bench.utils.python_test import python_test_command
from multi_swe_bench.harness.test_result import TestStatus, mapping_to_testresult

class spyderImageBase(Image):
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

WORKDIR /home/
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN apt update && apt install -y \
    wget \
    git \
    build-essential \
    libffi-dev \
    libtiff-dev \
    python3 \
    python3-pip \
    python-is-python3 \
    jq \
    curl \
    locales \
    locales-all \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --fix-missing \
  libgl1-mesa-glx \
  libglib2.0-0 \
  libx11-xcb1 \
  libxcb-xinerama0 \
  libxcomposite1 \
  libxcursor1 \
  libxdamage1 \
  libxi6 \
  libxtst6 \
  libxrandr2 \
  libxss1 \
  libxkbcommon-x11-0 \
  libasound2 \
  x11-utils \
  xterm \
  xvfb \
  libnss3 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libcups2 \
  lsof \
  curl \
  dbus-x11 \
  ca-certificates \
  fonts-liberation \
  libxshmfence1 \
  libxext6 \
  qt5ct \
  libqt5widgets5 \
  libqt5gui5 \
  libqt5core5a \
  qtbase5-dev \
  libqt5multimedia5 \
  libqt5multimediawidgets5 \
  libqt5network5 \
  libqt5sql5 \
  libqt5sql5-sqlite \
  libqt5webenginecore5 \
  libqt5webenginewidgets5 \
  qml-module-qtquick2 \
  qml-module-qtquick-controls \
  qml-module-qtgraphicaleffects \
  qml-module-qtwebengine \
  && apt-get clean && rm -rf /var/lib/apt/lists/*
  
RUN apt update && apt install -y pyqt5-dev-tools libxcb-xinerama0 xterm xvfb
RUN wget "https://repo.anaconda.com/miniconda/Miniconda3-py39_23.11.0-1-Linux-x86_64.sh" -O miniconda.sh \
    && bash miniconda.sh -b -p /opt/miniconda3 \
    && rm miniconda.sh

ENV PATH="/opt/miniconda3/bin:$PATH"
RUN conda init --all \
    && conda config --append channels conda-forge \
    && conda clean -y --all

    
{code}

{self.clear_env}

"""


class spyderImageDefault(Image):
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
        # if self.pr.number <= 958:
        #     return spyderImageBaseCpp7(self.pr, self._config)

        return spyderImageBase(self.pr, self._config)

    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:
        test_cmd = python_test_command(self.pr.test_patch)
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
. "/opt/miniconda3/etc/profile.d/conda.sh"

cd /home/{pr.repo}
git reset --hard
bash /home/check_git_changes.sh
git checkout {pr.base.sha}
bash /home/check_git_changes.sh

conda create -n testenv python=3.8 -y
conda activate testenv
pip install -e .[test] || true

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
set -e
. "/opt/miniconda3/etc/profile.d/conda.sh"
cd /home/{pr.repo}

conda activate testenv
pip install -e .[test] || true
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
{test_cmd}
""".format(
                    pr=self.pr,
                    test_cmd=test_cmd,
                ),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
set -e
. "/opt/miniconda3/etc/profile.d/conda.sh"
cd /home/{pr.repo}
git apply --whitespace=nowarn /home/test.patch

conda activate testenv
pip install -e .[test] || true
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
{test_cmd}
""".format(
                    pr=self.pr,
                    test_cmd=test_cmd,
                ),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
set -e
. "/opt/miniconda3/etc/profile.d/conda.sh"
cd /home/{pr.repo}
git apply --whitespace=nowarn /home/test.patch /home/fix.patch

conda activate testenv
pip install -e .[test] || true
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
{test_cmd}
""".format(
                    pr=self.pr,
                    test_cmd=test_cmd,
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
        proxy_setup = ""
        proxy_cleanup = ""

        return f"""FROM {name}:{tag}

{self.global_env}

{proxy_setup}

{copy_commands}

{prepare_commands}

{proxy_cleanup}

{self.clear_env}

"""


@Instance.register("spyder-ide", "spyder")
class spyder(Instance):
    def __init__(self, pr: PullRequest, config: Config, *args, **kwargs):
        super().__init__()
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    def dependency(self) -> Optional[Image]:
        return spyderImageDefault(self.pr, self._config)

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
        option_pattern = re.compile(r"(.*?)\[(.*)\]")
        test_status_map = {}
        for line in log.split("\n"):
            if any([line.startswith(x.value) for x in TestStatus]):
                # Additional parsing for FAILED status
                if line.startswith(TestStatus.FAILED.value):
                    line = line.replace(" - ", " ")
                test_case = line.split()
                if len(test_case) <= 1:
                    continue
                has_option = option_pattern.search(test_case[1])
                if has_option:
                    main, option = has_option.groups()
                    if (
                        option.startswith("/")
                        and not option.startswith("//")
                        and "*" not in option
                    ):
                        option = "/" + option.split("/")[-1]
                    test_name = f"{main}[{option}]"
                else:
                    test_name = test_case[1]
                test_status_map[test_name] = test_case[0]

        return mapping_to_testresult(test_status_map)
