#!/usr/bin/env python3
"""Lean integration test that exercises the mini-swe-agent workflow."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from textwrap import dedent
from typing import Callable, Dict, List, Tuple, cast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.instance import Instance
from multi_swe_bench.harness.pull_request import Base, PullRequest, ResolvedIssue
from multi_swe_bench.harness.test_result import TestResult

CONFIG_PATH = Path(__file__).with_name("test_workflow_config.json")


def _script(body: str) -> str:
    return dedent(body).strip() + "\n"


class TestMiniSWEAgentImage(Image):
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
        return "msb-test"

    def image_tag(self) -> str:
        return f"mini-swe-agent-pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> List[File]:
        scripts: List[Tuple[str, str]] = [
            ("fix.patch", self.pr.fix_patch),
            ("test.patch", self.pr.test_patch),
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
                    """
                ),
            ),
            (
                "run.sh",
                _script(
                    f"""#!/bin/bash
                    cd /home/{self.pr.repo}
                    python -m pytest -vv tests/agents/test_interactive_textual.py || true
                    """
                ),
            ),
            (
                "test-run.sh",
                _script(
                    f"""#!/bin/bash
                    cd /home/{self.pr.repo}
                    git apply --whitespace=nowarn /home/test.patch || true
                    python -m pytest -vv tests/agents/test_interactive_textual.py || true
                    """
                ),
            ),
            (
                "fix-run.sh",
                _script(
                    f"""#!/bin/bash
                    cd /home/{self.pr.repo}
                    git apply --whitespace=nowarn /home/test.patch /home/fix.patch || true
                    python -m pytest -vv tests/agents/test_interactive_textual.py || true
                    """
                ),
            ),
        ]
        return [File(".", name, content) for name, content in scripts]

    def dockerfile(self) -> str:
        return dedent(
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
        ).strip() + "\n"


@Instance.register("SWE-agent", "mini-swe-agent")
class TestMiniSWEAgentInstance(Instance):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config
        self._image = TestMiniSWEAgentImage(pr, config)

    @property
    def pr(self) -> PullRequest:
        return self._pr

    @property
    def config(self) -> Config:
        return self._config

    def dependency(self) -> Image:
        return self._image

    def run(self) -> str:
        return "bash /home/run.sh"

    def test_patch_run(self) -> str:
        return "bash /home/test-run.sh"

    def fix_patch_run(self, fix_patch_run_cmd: str = "") -> str:
        return fix_patch_run_cmd or "bash /home/fix-run.sh"

    def parse_log(self, test_log: str) -> TestResult:
        match = re.findall(r"([\w/\-.]+\.py::[\w\[\]_-]+)\s+(PASSED|FAILED|SKIPPED|ERROR)", test_log)
        passed, failed, skipped = set(), set(), set()
        for test_case, status in match:
            target = {
                "PASSED": passed,
                "FAILED": failed,
                "ERROR": failed,
                "SKIPPED": skipped,
            }[status]
            target.add(test_case)
        return TestResult(
            passed_count=len(passed),
            failed_count=len(failed),
            skipped_count=len(skipped),
            passed_tests=passed,
            failed_tests=failed,
            skipped_tests=skipped,
        )


def create_test_pr() -> PullRequest:
    return PullRequest(
        org="SWE-agent",
        repo="mini-swe-agent",
        number=1,
        state="closed",
        title="Test PR for integration",
        body="Testing Multi-SWE-bench workflow",
        base=Base(label="SWE-agent:main", ref="main", sha="HEAD"),
        resolved_issues=[ResolvedIssue(number=1, title="Test issue", body="Test issue description")],
        fix_patch="",
        test_patch="",
        tag="",
        number_interval="",
        lang="python",
    )


MOCK_LOG = dedent(
    """
    tests/test_core.py::test_basic PASSED
    tests/test_core.py::test_advanced FAILED
    tests/test_core.py::test_edge_case PASSED
    tests/test_utils.py::test_helper_func PASSED
    tests/test_utils.py::test_validation SKIPPED
    tests/test_parser.py::test_parse_simple PASSED
    tests/test_parser.py::test_parse_complex FAILED
    tests/test_integration.py::test_e2e SKIPPED
    """
).strip()


TestFunc = Callable[[Dict[str, object]], str]


def test_instance_registration(state: Dict[str, object]) -> str:
    pr = create_test_pr()
    config = Config(need_clone=False, global_env=None, clear_env=True)
    instance = Instance.create(pr, config)
    state["instance"] = instance
    return f"registered {instance.name()}"


def _require_instance(state: Dict[str, object]) -> TestMiniSWEAgentInstance:
    instance = state.get("instance")
    if instance is None:
        raise RuntimeError("instance not created yet")
    return cast(TestMiniSWEAgentInstance, instance)


def test_dockerfile_generation(state: Dict[str, object]) -> str:
    instance = _require_instance(state)
    dockerfile = instance.dependency().dockerfile()
    for snippet in ("FROM python:3.10-slim", "git clone", "prepare.sh"):
        assert snippet in dockerfile
    return f"{len(dockerfile.splitlines())} dockerfile lines"


def test_command_generation(state: Dict[str, object]) -> str:
    instance = _require_instance(state)
    commands = (instance.run(), instance.test_patch_run(), instance.fix_patch_run())
    assert all(cmd.startswith("bash ") for cmd in commands)
    return " / ".join(commands)


def test_log_parsing(state: Dict[str, object]) -> str:
    instance = _require_instance(state)
    result = instance.parse_log(MOCK_LOG)
    assert (result.passed_count, result.failed_count, result.skipped_count) == (4, 2, 2)
    return "parsed pytest log"


def test_files_generation(state: Dict[str, object]) -> str:
    instance = _require_instance(state)
    files = instance.dependency().files()
    expected = {"fix.patch", "test.patch", "prepare.sh", "run.sh", "test-run.sh", "fix-run.sh"}
    assert {f.name for f in files} == expected
    return "generated helper scripts"


def test_config_export(state: Dict[str, object]) -> str:
    instance = _require_instance(state)
    payload = {
        "instance_type": type(instance).__name__,
        "instance_name": instance.name(),
        "repository": {"org": instance.pr.org, "repo": instance.pr.repo},
        "docker": {
            "base_image": instance.dependency().dependency(),
            "image_name": instance.name(),
            "image_tag": instance.dependency().image_tag(),
        },
        "commands": {
            "run": instance.run(),
            "test_patch": instance.test_patch_run(),
            "fix_patch": instance.fix_patch_run(),
        },
        "language": instance.pr.lang,
    }
    CONFIG_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return f"wrote {CONFIG_PATH.name}"


def main() -> int:
    tests: List[Tuple[str, TestFunc]] = [
        ("Instance registration", test_instance_registration),
        ("Dockerfile generation", test_dockerfile_generation),
        ("Command generation", test_command_generation),
        ("Log parsing", test_log_parsing),
        ("Files generation", test_files_generation),
        ("Configuration export", test_config_export),
    ]
    state: Dict[str, object] = {}
    passed = 0
    for name, func in tests:
        try:
            detail = func(state)
            passed += 1
            print(f"[PASS] {name} — {detail}")
        except Exception as exc:  # pragma: no cover - quick smoke script
            print(f"[FAIL] {name}: {exc}")
            return 1
    print(f"All {passed}/{len(tests)} checks passed. ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
