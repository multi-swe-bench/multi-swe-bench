from dataclasses import dataclass
from typing import Union

from multi_swe_bench.harness.pull_request import PullRequest


@dataclass
class File:
    dir: str
    name: str
    content: str


@dataclass
class Config:
    need_clone: bool


class Image:

    @property
    def pr(self) -> PullRequest:
        raise NotImplementedError

    @property
    def config(self) -> Config:
        raise NotImplementedError

    def dependency(self) -> Union[str, "Image"]:
        return NotImplementedError

    def image_full_name(self) -> str:
        return f"{self.image_name()}:{self.image_tag()}"

    def image_name(self) -> str:
        raise NotImplementedError

    def image_tag(self) -> str:
        raise NotImplementedError

    def workdir(self) -> str:
        raise NotImplementedError

    def files(self) -> list[File]:
        raise NotImplementedError

    def dockerfile_name(self) -> str:
        return "Dockerfile"

    def dockerfile(self) -> str:
        raise NotImplementedError
