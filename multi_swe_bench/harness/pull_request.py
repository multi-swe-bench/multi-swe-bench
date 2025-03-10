from dataclasses import asdict, dataclass

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

    @classmethod
    def from_dict(cls, d: dict) -> "PullRequest":
        return cls(**d)

    @classmethod
    def from_json(cls, json_str: str) -> "PullRequest":
        return cls.from_dict(cls.schema().loads(json_str))

    def dict(self) -> dict:
        return asdict(self)

    def json(self) -> str:
        return self.to_json(ensure_ascii=False)
