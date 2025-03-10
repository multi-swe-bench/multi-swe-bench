from dataclasses import asdict, dataclass, field
from typing import Optional, Tuple

from dataclasses_json import config, dataclass_json

from multi_swe_bench.harness.test_result import Test, TestResult, TestStatus


@dataclass_json
@dataclass
class Report:
    org: str
    repo: str
    number: int
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

    def __lt__(self, other: "Report") -> bool:
        if self.org != other.org:
            return self.org < other.org

        if self.repo != other.repo:
            return self.repo < other.repo

        return self.number < other.number

    def __repr__(self) -> str:
        return f"{self.org}/{self.repo}:pr-{self.number}"

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


@dataclass_json
@dataclass
class FinalReport:
    total_instances: int
    submitted_instances: int
    completed_instances: int
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
    def from_reports(clc, reports: list[Report]) -> "FinalReport":
        submitted_ids = [
            f"{report.org}__{report.repo}-{report.number}" for report in reports
        ]
        completed_ids = [
            f"{report.org}__{report.repo}-{report.number}"
            for report in reports
            if report.fix_patch_result.all_count > 0
        ]
        incomplete_ids = [
            f"{report.org}__{report.repo}-{report.number}"
            for report in reports
            if report.fix_patch_result.all_count == 0
        ]
        resolved_ids = [
            f"{report.org}__{report.repo}-{report.number}"
            for report in reports
            if report.fix_patch_result.all_count > 0 and report.valid
        ]
        unresolved_ids = [
            f"{report.org}__{report.repo}-{report.number}"
            for report in reports
            if report.fix_patch_result.all_count > 0 and not report.valid
        ]
        empty_patch_ids = []
        error_ids = [
            f"{report.org}__{report.repo}-{report.number}"
            for report in reports
            if report.fix_patch_result.all_count == 0
        ]
        final_report = FinalReport(
            total_instances=len(reports),
            submitted_instances=len(submitted_ids),
            completed_instances=len(completed_ids),
            resolved_instances=len(resolved_ids),
            unresolved_instances=len(unresolved_ids),
            empty_patch_instances=empty_patch_ids,
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
