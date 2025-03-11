from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional, Tuple

from dataclasses_json import config, dataclass_json

from multi_swe_bench.harness.constant import (
    FIX_PATCH_RUN_LOG_FILE,
    REPORT_FILE,
    RUN_LOG_FILE,
    TEST_PATCH_RUN_LOG_FILE,
)
from multi_swe_bench.harness.image import Config
from multi_swe_bench.harness.instance import Instance
from multi_swe_bench.harness.pull_request import (
    Base,
    PullRequest,
    PullRequestBase,
)
from multi_swe_bench.harness.test_result import Test, TestResult, TestStatus


@dataclass_json
@dataclass
class Report(PullRequestBase):
    valid: Optional[bool] = None
    error_msg: Optional[str] = None
    fixed_tests: dict[str, Test] = field(default_factory=dict)
    run_result: TestResult = None
    test_patch_result: TestResult = None
    fix_patch_result: TestResult = None
    _tests: dict[str, Test] = field(
        default_factory=dict, metadata=config(exclude=lambda _: True)
    )

    def __post_init__(self):
        if not self.run_result:
            raise ValueError("Invalid run_result: None")
        if not self.test_patch_result:
            raise ValueError("Invalid test_patch_result: None")
        if not self.fix_patch_result:
            raise ValueError("Invalid fix_patch_result: None")

        all_tests = (
            self.run_result._tests.keys()
            | self.test_patch_result._tests.keys()
            | self.fix_patch_result._tests.keys()
        )

        for test_name in all_tests:
            run = self.run_result._tests.get(test_name, TestStatus.NONE)
            test = self.test_patch_result._tests.get(test_name, TestStatus.NONE)
            fix = self.fix_patch_result._tests.get(test_name, TestStatus.NONE)
            self._tests[test_name] = Test(run, test, fix)

        self.valid, self.error_msg = self.check()

    @classmethod
    def from_dict(cls, d: dict) -> "Report":
        return cls(**d)

    @classmethod
    def from_json(cls, json_str: str) -> "Report":
        return cls.from_dict(cls.schema().loads(json_str))

    def dict(self) -> dict:
        return asdict(self)

    def json(self) -> str:
        return self.to_json(ensure_ascii=False)

    def check(self, force: bool = False) -> Tuple[bool, str]:
        if not force and self.valid is not None:
            return (self.valid, self.error_msg)

        # 1. Exist valid fix patch result
        if self.fix_patch_result.all_count == 0:
            self.valid = False
            self.error_msg = (
                f"There is no valid fix patch result: {self.short_report()}"
            )
            return (self.valid, self.error_msg)

        # 2. No new failures
        for name, test in self._tests.items():
            if test.test == TestStatus.PASS and test.fix == TestStatus.FAIL:
                self.valid = False
                # self._error_msg = f"Test passed but not fixed: {self.short_report()}"
                self.error_msg = f"Test passed in test patch but failed in fix patch: {self.short_report()}. `{name}`: {test}"
                return (self.valid, self.error_msg)

        # 3. Fix something
        fix_something = False
        for name, test in self._tests.items():
            if test.test != TestStatus.PASS and test.fix == TestStatus.PASS:
                fix_something = True
                self.fixed_tests[name] = test

        if not fix_something:
            self.valid = False
            self.error_msg = f"No fix for failed test: {self.short_report()}"
            return (self.valid, self.error_msg)

        # 4. Anomalous Pattern
        for name, test in self._tests.items():
            if (
                (test.test == TestStatus.NONE or test.test == TestStatus.SKIP)
                and test.fix == TestStatus.FAIL
                and test.run == TestStatus.PASS
            ):
                self.valid = False
                self.error_msg = (
                    f"Anomalous pattern: {self.short_report()}. `{name}`: {test}"
                )
                return (self.valid, self.error_msg)

        self.valid = True
        self.error_msg = ""
        return (self.valid, self.error_msg)

    def short_report(self) -> str:
        return f"run=({self.run_result.passed_count}, {self.run_result.failed_count}, {self.run_result.skipped_count}), test=({self.test_patch_result.passed_count}, {self.test_patch_result.failed_count}, {self.test_patch_result.skipped_count}), fix=({self.fix_patch_result.passed_count}, {self.fix_patch_result.failed_count}, {self.fix_patch_result.skipped_count})"


def generate_report(
    instance: Instance, output_run: str, output_test: str, output_fix: str
) -> Report:
    report = Report(
        org=instance.pr.org,
        repo=instance.pr.repo,
        number=instance.pr.number,
        run_result=instance.parse_log(output_run),
        test_patch_result=instance.parse_log(output_test),
        fix_patch_result=instance.parse_log(output_fix),
    )

    return report


@dataclass_json
@dataclass
class ReportTask(PullRequestBase):
    instance_dir: Path

    @property
    def instance(self) -> Instance:
        pr = PullRequest(
            org=self.org,
            repo=self.repo,
            number=self.number,
            state="",
            title="",
            body="",
            base=Base(label="", ref="", sha=""),
            resolved_issues=[],
            fix_patch="",
            test_patch="",
        )

        config = Config(
            need_clone=False,
            global_env=None,
            clear_env=False,
        )

        return Instance.create(pr, config)

    @property
    def run_log(self) -> str:
        run_log_path = self.instance_dir / RUN_LOG_FILE
        if not run_log_path.exists():
            raise FileNotFoundError(f"Run log file not found: {run_log_path}")
        with open(run_log_path, "r", encoding="utf-8") as f:
            run_log = f.read()
        return run_log

    @property
    def test_patch_run_log(self) -> str:
        test_patch_run_log_path = self.instance_dir / TEST_PATCH_RUN_LOG_FILE
        if not test_patch_run_log_path.exists():
            raise FileNotFoundError(
                f"Test patch run log file not found: {test_patch_run_log_path}"
            )
        with open(test_patch_run_log_path, "r", encoding="utf-8") as f:
            test_patch_run_log = f.read()
        return test_patch_run_log

    @property
    def fix_patch_run_log(self) -> str:
        fix_patch_run_log_path = self.instance_dir / FIX_PATCH_RUN_LOG_FILE
        if not fix_patch_run_log_path.exists():
            raise FileNotFoundError(
                f"Fix patch run log file not found: {fix_patch_run_log_path}"
            )
        with open(fix_patch_run_log_path, "r", encoding="utf-8") as f:
            fix_patch_run_log = f.read()
        return fix_patch_run_log

    def generate_report(self) -> Report:
        report = generate_report(
            self.instance,
            self.run_log,
            self.test_patch_run_log,
            self.fix_patch_run_log,
        )

        with open(self.instance_dir / REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(report.json())

        return report


@dataclass_json
@dataclass
class FinalReport:
    total_instances: int
    submitted_instances: int
    completed_instances: int
    incomplete_instances: int
    resolved_instances: int
    unresolved_instances: int
    empty_patch_instances: int
    error_instances: int

    submitted_ids: list[str]
    completed_ids: list[str]
    incomplete_ids: list[str]
    resolved_ids: list[str]
    unresolved_ids: list[str]
    empty_patch_ids: list[str]
    error_ids: list[str]

    @classmethod
    def from_dict(cls, d: dict) -> "FinalReport":
        return cls(**d)

    @classmethod
    def from_json(cls, json_str: str) -> "FinalReport":
        return cls.from_dict(cls.schema().loads(json_str))

    def dict(self) -> dict:
        return asdict(self)

    def json(self) -> str:
        return self.to_json(ensure_ascii=False)

    @classmethod
    def from_reports(
        clc, reports: list[Report], failed_tasks: list[ReportTask] = []
    ) -> "FinalReport":
        submitted_ids = [report.id for report in reports] + [
            task.id for task in failed_tasks
        ]
        completed_ids = [report.id for report in reports]
        incomplete_ids = [task.id for task in failed_tasks]
        resolved_ids = [report.id for report in reports if report.valid]
        unresolved_ids = [report.id for report in reports if not report.valid]
        empty_patch_ids = []
        error_ids = [task.id for task in failed_tasks]

        final_report = FinalReport(
            total_instances=len(reports) + len(failed_tasks),
            submitted_instances=len(submitted_ids),
            completed_instances=len(completed_ids),
            incomplete_instances=len(incomplete_ids),
            resolved_instances=len(resolved_ids),
            unresolved_instances=len(unresolved_ids),
            empty_patch_instances=len(empty_patch_ids),
            error_instances=len(error_ids),
            submitted_ids=submitted_ids,
            completed_ids=completed_ids,
            incomplete_ids=incomplete_ids,
            resolved_ids=resolved_ids,
            unresolved_ids=unresolved_ids,
            empty_patch_ids=empty_patch_ids,
            error_ids=error_ids,
        )

        return final_report
