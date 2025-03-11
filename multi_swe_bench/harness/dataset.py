from dataclasses import asdict, dataclass, field

from dataclasses_json import dataclass_json

from multi_swe_bench.harness.pull_request import PullRequest
from multi_swe_bench.harness.report import Report
from multi_swe_bench.harness.test_result import Test, TestResult


@dataclass_json
@dataclass
class Dataset(PullRequest):
    fixed_tests: dict[str, Test] = field(default_factory=dict)
    run_result: TestResult = None
    test_patch_result: TestResult = None
    fix_patch_result: TestResult = None

    @classmethod
    def from_dict(cls, d: dict) -> "Dataset":
        return cls(**d)

    @classmethod
    def from_json(cls, json_str: str) -> "Dataset":
        return cls.from_dict(cls.schema().loads(json_str))

    def dict(self) -> dict:
        return asdict(self)

    def json(self) -> str:
        return self.to_json(ensure_ascii=False)

    @classmethod
    def build(cls, pr: PullRequest, report: Report) -> "Dataset":
        return cls(
            org=pr.org,
            repo=pr.repo,
            number=pr.number,
            state=pr.state,
            title=pr.title,
            body=pr.body,
            base=pr.base,
            resolved_issues=pr.resolved_issues,
            fix_patch=pr.fix_patch,
            test_patch=pr.test_patch,
            fixed_tests=report.fixed_tests,
            run_result=report.run_result,
            test_patch_result=report.test_patch_result,
            fix_patch_result=report.fix_patch_result,
        )
