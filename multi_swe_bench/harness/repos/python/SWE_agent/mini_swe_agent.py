#!/usr/bin/env python3
"""Mini SWE-agent Instance wiring for Multi-SWE-bench."""

from __future__ import annotations

import re
from textwrap import dedent

from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.instance import Instance
from multi_swe_bench.harness.pull_request import PullRequest
from multi_swe_bench.harness.test_result import TestResult


def _script(body: str) -> str:
    return dedent(body).strip() + "\n"


class MiniSWEAgentImage(Image):
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
        return "python:3.11-slim"

    def image_prefix(self) -> str:
        return "msb-mini-swe"

    def image_tag(self) -> str:
        return f"mini-swe-agent-pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:
        scripts = [
            ("fix.patch", self.pr.fix_patch or ""),
            ("test.patch", self.pr.test_patch or ""),
            (
                "prepare.sh",
                _script(
                    """#!/bin/bash
                    set -e
                    pip install --upgrade pip pytest pytest-cov python-dotenv
                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    fi
                    if [ -f requirements-dev.txt ]; then
                        pip install -r requirements-dev.txt
                    fi
                    if [ -f pyproject.toml ]; then
                        pip install -e ".[dev]" || pip install -e .
                    elif [ -f setup.py ]; then
                        pip install -e .
                    fi
                    """,
                ),
            ),
            (
                "run.sh",
                _script(
                    f"""#!/bin/bash
                    cd /home/{self.pr.repo}
                    python -m pytest -vv tests/agents/test_interactive_textual.py || true
                    """,
                ),
            ),
            (
                "test-run.sh",
                _script(
                    f"""#!/bin/bash
                    cd /home/{self.pr.repo}
                    git apply --whitespace=nowarn /home/test.patch || true
                    python -m pytest -vv tests/agents/test_interactive_textual.py || true
                    """,
                ),
            ),
            (
                "fix-run.sh",
                _script(
                    f"""#!/bin/bash
                    cd /home/{self.pr.repo}
                    git apply --whitespace=nowarn /home/test.patch /home/fix.patch || true
                    python -m pytest -vv tests/agents/test_interactive_textual.py || true
                    """,
                ),
            ),
        ]
        return [File(".", name, content) for name, content in scripts]

    def dockerfile(self) -> str:
        return (
            dedent(
                f"""
                FROM python:3.11-slim
                ENV DEBIAN_FRONTEND=noninteractive
                RUN apt-get update && apt-get install -y git bash
                WORKDIR /home/
                COPY fix.patch test.patch /home/
                RUN git clone https://github.com/{self.pr.org}/{self.pr.repo}.git /home/{self.pr.repo}
                WORKDIR /home/{self.pr.repo}
                RUN git reset --hard
                RUN git checkout {self.pr.base.sha}
                COPY prepare.sh /home/
                RUN bash /home/prepare.sh
                COPY run.sh test-run.sh fix-run.sh /home/
                RUN chmod +x /home/*.sh
                """
            ).strip()
            + "\n"
        )


@Instance.register("SWE-agent", "mini-swe-agent")
class MiniSWEAgentInstance(Instance):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config
        self._image = MiniSWEAgentImage(pr, config)

    @property
    def pr(self) -> PullRequest:
        return self._pr

    def dependency(self) -> Image:
        return self._image

    def run(self) -> str:
        return "bash /home/run.sh"

    def test_patch_run(self) -> str:
        return "bash /home/test-run.sh"

    def fix_patch_run(self, fix_patch_run_cmd: str = "") -> str:
        return fix_patch_run_cmd or "bash /home/fix-run.sh"

    def parse_log(self, test_log: str) -> TestResult:
        pattern = re.compile(r"([\w/\-.]+\.py::[\w\[\]_-]+)\s+(PASSED|FAILED|SKIPPED|ERROR)")
        passed, failed, skipped = set(), set(), set()
        for line in test_log.splitlines():
            match = pattern.search(line)
            if not match:
                continue
            test_case, status = match.groups()
            if status == "PASSED":
                passed.add(test_case)
            elif status in {"FAILED", "ERROR"}:
                failed.add(test_case)
            else:
                skipped.add(test_case)
        return TestResult(
            passed_count=len(passed),
            failed_count=len(failed),
            skipped_count=len(skipped),
            passed_tests=passed,
            failed_tests=failed,
            skipped_tests=skipped,
        )
