from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class ResolvedIssue:
    number: int
    title: str
    body: str


@dataclass_json
@dataclass
class Base:
    label: str
    ref: str
    sha: str


@dataclass_json
@dataclass
class PullRequest:
    org: str
    repo: str
    number: int
    state: str
    title: str
    body: str
    base: Base
    resolved_issues: list[ResolvedIssue]
    fix_patch: str
    test_patch: str

    @property
    def id(self) -> str:
        return f"{self.org}/{self.repo}:pr-{self.number}"

    @property
    def repo_full_name(self) -> str:
        return f"{self.org}/{self.repo}"
