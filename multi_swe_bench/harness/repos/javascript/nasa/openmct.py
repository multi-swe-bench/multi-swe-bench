import re
from typing import Optional, Union
import textwrap
from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.instance import Instance, TestResult
from multi_swe_bench.harness.pull_request import PullRequest


class openmctImageBase(Image):
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
        return "node:18"

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

RUN apt update && apt install -y libxkbfile-dev pkg-config build-essential python3 libkrb5-dev libxss1 xvfb libgtk-3-0 libgbm1
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg \
        fonts-khmeros fonts-kacst fonts-freefont-ttf libxss1 dbus dbus-x11 \
        --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && \
    export NVM_DIR="$HOME/.nvm" && \
    [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
{code}

{self.clear_env}

"""



class openmctImageDefault(Image):
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
        #     return openmctImageBaseCpp7(self.pr, self._config)

        return openmctImageBase(self.pr, self._config)

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
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

cd /home/{pr.repo}
git reset --hard
bash /home/check_git_changes.sh
git checkout {pr.base.sha}
bash /home/check_git_changes.sh
nvm install || true
nvm use || true
npm install || true
apt-get update --fix-missing || true
npx playwright install-deps chromium || true
npx playwright install chromium || true
""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
set -e
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

cd /home/{pr.repo}

nvm use || true
npm install || true
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
apt-get update --fix-missing || true
npx playwright install-deps chromium || true
npx playwright install chromium || true
CHROME_BIN=$(mktemp) && echo '#!/bin/bash' > $CHROME_BIN && echo 'exec /usr/bin/google-chrome --no-sandbox "$@"' >> $CHROME_BIN && chmod +x $CHROME_BIN && CHROME_BIN=$CHROME_BIN npm run test || true
CHROME_BIN=$(mktemp) && echo '#!/bin/bash' > $CHROME_BIN && echo 'exec /usr/bin/google-chrome --no-sandbox "$@"' >> $CHROME_BIN && chmod +x $CHROME_BIN && CHROME_BIN=$CHROME_BIN npm run test:e2e:ci || true


""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
set -e
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

cd /home/{pr.repo}
git apply --whitespace=nowarn /home/test.patch

nvm use || true
npm install || true
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
apt-get update --fix-missing || true
npx playwright install-deps chromium || true
npx playwright install chromium || true
CHROME_BIN=$(mktemp) && echo '#!/bin/bash' > $CHROME_BIN && echo 'exec /usr/bin/google-chrome --no-sandbox "$@"' >> $CHROME_BIN && chmod +x $CHROME_BIN && CHROME_BIN=$CHROME_BIN npm run test || true
CHROME_BIN=$(mktemp) && echo '#!/bin/bash' > $CHROME_BIN && echo 'exec /usr/bin/google-chrome --no-sandbox "$@"' >> $CHROME_BIN && chmod +x $CHROME_BIN && CHROME_BIN=$CHROME_BIN npm run test:e2e:ci || true
""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
set -e
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

cd /home/{pr.repo}
git apply --whitespace=nowarn /home/test.patch /home/fix.patch

nvm use || true
npm install || true
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
apt-get update --fix-missing || true
npx playwright install-deps chromium || true
npx playwright install chromium || true
CHROME_BIN=$(mktemp) && echo '#!/bin/bash' > $CHROME_BIN && echo 'exec /usr/bin/google-chrome --no-sandbox "$@"' >> $CHROME_BIN && chmod +x $CHROME_BIN && CHROME_BIN=$CHROME_BIN npm run test || true
CHROME_BIN=$(mktemp) && echo '#!/bin/bash' > $CHROME_BIN && echo 'exec /usr/bin/google-chrome --no-sandbox "$@"' >> $CHROME_BIN && chmod +x $CHROME_BIN && CHROME_BIN=$CHROME_BIN npm run test:e2e:ci || true
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
        proxy_setup = ""
        proxy_cleanup = ""

        if self.global_env:
            proxy_host = None
            proxy_port = None

            for line in self.global_env.splitlines():
                match = re.match(
                    r"^ENV\s*(http[s]?_proxy)=http[s]?://([^:]+):(\d+)", line
                )
                if match:
                    proxy_host = match.group(2)
                    proxy_port = match.group(3)
                    break

            if proxy_host and proxy_port:
                proxy_setup = textwrap.dedent(
                    f"""
                    RUN mkdir -p $HOME && \\
                        touch $HOME/.npmrc && \\
                        echo "proxy=http://{proxy_host}:{proxy_port}" >> $HOME/.npmrc && \\
                        echo "https-proxy=http://{proxy_host}:{proxy_port}" >> $HOME/.npmrc && \\
                        echo "strict-ssl=false" >> $HOME/.npmrc
                """
                )

                proxy_cleanup = textwrap.dedent(
                    """
                    RUN rm -f $HOME/.npmrc
                """
                )
        return f"""FROM {name}:{tag}

{self.global_env}

{proxy_setup}

{copy_commands}

{prepare_commands}

{proxy_cleanup}

{self.clear_env}

"""


@Instance.register("nasa", "openmct")
class openmct(Instance):
    def __init__(self, pr: PullRequest, config: Config, *args, **kwargs):
        super().__init__()
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    def dependency(self) -> Optional[Image]:
        return openmctImageDefault(self.pr, self._config)

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

        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')

        pass_patterns = [
            re.compile(r'^[\s]*[✔✓]\s+(.*?)(?:\s+\([\d\.]+\s*\w+\))?$'),
        ]

        fail_patterns = [
            re.compile(r'^[\s]*✖\s+(.*?)(?:\s+\([\d\.]+\s*\w+\))?$'),
            re.compile(r'^\s*\d+\)\s*(.+)$')
        ]

        skip_patterns = [
            re.compile(r'^\s*-\s+(.*)$'),  # - skipped
        ]

        for line in test_log.splitlines():
            line = ansi_escape.sub('', line).strip()
            if not line:
                continue

            matched = False

            for fail_re in fail_patterns:
                m = fail_re.match(line)
                if m:
                    test_name = m.group(1).strip()
                    failed_tests.add(test_name)
                    passed_tests.discard(test_name)
                    skipped_tests.discard(test_name)
                    matched = True
                    break
            if matched:
                continue

            for skip_re in skip_patterns:
                m = skip_re.match(line)
                if m:
                    test_name = m.group(1).strip()
                    if test_name not in failed_tests:
                        skipped_tests.add(test_name)
                        passed_tests.discard(test_name)
                    matched = True
                    break
            if matched:
                continue

            for pass_re in pass_patterns:
                m = pass_re.match(line)
                if m:
                    test_name = m.group(1).strip()
                    if test_name not in failed_tests and test_name not in skipped_tests:
                        passed_tests.add(test_name)
                    break

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
