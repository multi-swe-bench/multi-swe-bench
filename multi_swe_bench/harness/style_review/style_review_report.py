from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import dataclass_json

from multi_swe_bench.harness.pull_request import PullRequestBase

@dataclass_json
@dataclass
class StyleIssue:
    line: int
    column: int
    type: str
    message: str
    source: str

@dataclass_json
@dataclass
class StyleFileReport:
    file: str
    score: float
    error_count: int
    messages: list[StyleIssue]

@dataclass_json
@dataclass
class StyleReviewSummary:
    global_score: float
    total_errors: int
    total_warnings: int

@dataclass_json
@dataclass
class JavaStyleReviewReport(PullRequestBase):
    original_score: Optional[StyleReviewSummary] = None
    patched_score: Optional[StyleReviewSummary] = None
    original_issues: list[StyleFileReport] = field(default_factory=list)
    patched_issues: list[StyleFileReport] = field(default_factory=list)
    improvement: Optional[float] = None
    
    def calculate_improvement(self):
        """Calculate the improvement in style score after applying the patch"""
        if self.original_score and self.patched_score:
            self.improvement = self.patched_score.global_score - self.original_score.global_score