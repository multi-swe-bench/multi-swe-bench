import re
from pathlib import Path
from typing import Optional, Union
import textwrap
from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.instance import Instance, TestResult
from multi_swe_bench.harness.pull_request import PullRequest
from multi_swe_bench.harness.repos.kotlin.junit_parser import (
    parse_junit_from_log,
    to_test_result,
)

# Flaky IntelliJ quickfix tests (JVM shared, nondeterministic stub-lookups).
# DO NOT add lookalikes (f2p): LatexPrimitiveStyleInspectionTest.* (pr-2935),
# LatexUnicodeInspectionQuickFix.* (pr-3920), LatexDuplicateDefinitionInspectionTest.testIfthenelse (pr-3810),
# LatexFoldingTest.testSectionFolding (pr-3887), LatexNonBreakingSpaceInspectionTest.* (pr-3128).
FLAKY_TESTS = (
    "*LatexLabelConventionInspectionTest.testFigureLabelConventionQuickFix",
    "*LatexLabelConventionInspectionTest.testSectionLabelConventionQuickFix",
    "*LatexLabelConventionInspectionTest.testListingLabelConventionQuickFix",
    "*LatexLabelConventionInspectionTest.testInputListingLabelConventionQuickFix",
    "*LatexLabelConventionInspectionTest.testListingLabelConventionQuickFixWithGroup",
)

FLAKY_TESTS_INIT_SCRIPT = "/home/exclude-flaky-tests.gradle.kts"


def _exclude_flaky_tests_init_script() -> str:
    """Render a Kotlin-DSL Gradle init script excluding the flaky tests from every Test task."""
    exclude_lines = "\n".join(
        f'            excludeTestsMatching("{pat}")' for pat in FLAKY_TESTS
    )
    return f"""
allprojects {{
    tasks.withType<org.gradle.api.tasks.testing.Test>().configureEach {{
        filter {{
{exclude_lines}
            isFailOnNoMatchingTests = false
        }}
    }}
}}
"""


class TeXiFyImageBase(Image):
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
        return "eclipse-temurin:21-jdk"

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
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN apt-get update && \\
  apt-get install -y --no-install-recommends \\
  curl \\
  git \\
  bash \\
  ca-certificates \\
  unzip && \\
  apt-get clean && \\
  rm -rf /var/lib/apt/lists/*

RUN $JAVA_HOME/bin/keytool -importkeystore -noprompt -trustcacerts \\
  -srckeystore /etc/ssl/certs/java/cacerts \\
  -destkeystore $JAVA_HOME/lib/security/cacerts \\
  -srcstorepass changeit -deststorepass changeit || true

{code}

{self.clear_env}

RUN git config --global --add safe.directory /home
"""


class TeXiFyImageDefault(Image):
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
        return TeXiFyImageBase(self.pr, self._config)

    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:
        logs_collector = (Path(__file__).parents[1] / "kotlin_logs_collector.sh").read_text(encoding="utf-8")
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
                "kotlin_logs_collector.sh",
                logs_collector,
            ),
            File(
                ".",
                "exclude-flaky-tests.gradle.kts",
                _exclude_flaky_tests_init_script(),
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
""",
            ),
            File(
                ".",
                "prepare.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git config core.autocrlf input
git config core.filemode false
echo ".gitattributes" >> .git/info/exclude
git add .
git reset --hard
bash /home/check_git_changes.sh
git checkout {pr.base.sha}
bash /home/check_git_changes.sh

./gradlew clean test --init-script {init_script} || true

""".format(pr=self.pr, init_script=FLAKY_TESTS_INIT_SCRIPT),
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}

./gradlew clean test --continue --init-script {init_script} || true

/home/kotlin_logs_collector.sh --root . --output /home/all-testsuites.xml
cat /home/all-testsuites.xml

""".format(pr=self.pr, init_script=FLAKY_TESTS_INIT_SCRIPT),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git apply --whitespace=nowarn /home/test.patch

./gradlew clean test --continue --init-script {init_script} || true

/home/kotlin_logs_collector.sh --root . --output /home/all-testsuites.xml
cat /home/all-testsuites.xml

""".format(pr=self.pr, init_script=FLAKY_TESTS_INIT_SCRIPT),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git apply --whitespace=nowarn /home/test.patch /home/fix.patch

./gradlew clean test --continue --init-script {init_script} || true

/home/kotlin_logs_collector.sh --root . --output /home/all-testsuites.xml
cat /home/all-testsuites.xml

""".format(pr=self.pr, init_script=FLAKY_TESTS_INIT_SCRIPT),
            ),
        ]

    def dockerfile(self) -> str:
        image = self.dependency()
        name = image.image_name()
        tag = image.image_tag()

        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        prepare_commands = textwrap.dedent(
            """
            RUN bash /home/prepare.sh
            RUN chmod +x /home/*.sh
            """
        ).strip()
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
                    RUN mkdir -p ~/.gradle && \\
                        if [ ! -f "$HOME/.gradle/gradle.properties" ]; then \\
                            touch "$HOME/.gradle/gradle.properties"; \\
                        fi && \\
                        if ! grep -q "systemProp.http.proxyHost" "$HOME/.gradle/gradle.properties"; then \\
                            echo 'systemProp.http.proxyHost={proxy_host}' >> "$HOME/.gradle/gradle.properties" && \\
                            echo 'systemProp.http.proxyPort={proxy_port}' >> "$HOME/.gradle/gradle.properties" && \\
                            echo 'systemProp.https.proxyHost={proxy_host}' >> "$HOME/.gradle/gradle.properties" && \\
                            echo 'systemProp.https.proxyPort={proxy_port}' >> "$HOME/.gradle/gradle.properties"; \\
                        fi && \\
                        echo 'export GRADLE_USER_HOME=/root/.gradle' >> ~/.bashrc && \\
                        /bin/bash -c "source ~/.bashrc"
                """
                )

                proxy_cleanup = textwrap.dedent(
                    """
                    RUN rm -f ~/.gradle/gradle.properties
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


@Instance.register("Hannah-Sten", "TeXiFy-IDEA")
class TeXiFyInstance(Instance):
    def __init__(self, pr: PullRequest, config: Config, *args, **kwargs):
        super().__init__()
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    def dependency(self) -> Optional[Image]:
        return TeXiFyImageDefault(self.pr, self._config)

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
        try:
            status_map = parse_junit_from_log(test_log, drop_parameterized=True)
        except ValueError as exc:
            raise RuntimeError("Failed to locate JUnit XML in test log") from exc

        return to_test_result(status_map)
