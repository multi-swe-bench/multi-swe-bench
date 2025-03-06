import logging
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal, Optional, Tuple

from dataclasses_json import config, dataclass_json

from multi_swe_bench.harness.constant import (
    FINAL_REPORT_FILE,
    FIX_PATCH_RUN_LOG_FILE,
    GENERATE_REPORT_LOG_FILE,
    INSTANCE_WORKDIR,
    REPORT_FILE,
    RUN_LOG_FILE,
    TEST_PATCH_RUN_LOG_FILE,
)
from multi_swe_bench.harness.image import Config
from multi_swe_bench.harness.instance import Instance
from multi_swe_bench.harness.pull_request import Base, PullRequest
from multi_swe_bench.harness.test_result import Test, TestResult, TestStatus
from multi_swe_bench.utils.args_util import ArgumentParser
from multi_swe_bench.utils.logger import setup_logger


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="A command-line tool for generating reports for multi-swe-bench."
    )
    parser.add_argument(
        "--workdir",
        type=Path,
        help="Path to the workdir",
        default=None,
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["workdir", "org", "repo", "instance"],
        help="Mode to generate reports",
        default="workdir",
    )
    parser.add_argument(
        "--org",
        type=str,
        help="Org to generate reports",
        default=None,
    )
    parser.add_argument(
        "--repo",
        type=str,
        help="Repo to generate reports",
        default=None,
    )
    parser.add_argument(
        "--number", type=int, help="Number to generate reports", default=None
    )
    parser.add_argument(
        "--specific_orgs",
        type=set[str],
        help="Specific orgs to generate reports",
        default=None,
    )
    parser.add_argument(
        "--specific_repos",
        type=set[str],
        help="Specific repos to generate reports",
        default=None,
    )
    parser.add_argument(
        "--specific_instances",
        type=set[str],
        help="Specific instances to generate reports",
        default=None,
    )
    parser.add_argument(
        "--skip_orgs",
        type=set[str],
        help="Skip orgs to generate reports",
        default=None,
    )
    parser.add_argument(
        "--skip_repos",
        type=set[str],
        help="Skip repos to generate reports",
        default=None,
    )
    parser.add_argument(
        "--skip_instances",
        type=set[str],
        help="Skip instances to generate reports",
        default=None,
    )
    parser.add_argument(
        "--to_disk_workdir",
        type=bool,
        help="Save workdir reports to disk",
        default=True,
    )
    parser.add_argument(
        "--to_disk_org",
        type=bool,
        help="Save org reports to disk",
        default=True,
    )
    parser.add_argument(
        "--to_disk_repo",
        type=bool,
        help="Save repo reports to disk",
        default=True,
    )
    parser.add_argument(
        "--to_disk_instance",
        type=bool,
        help="Save instance report to disk",
        default=True,
    )
    parser.add_argument(
        "--report_file_name_workdir",
        type=str,
        help="Workdir report file name",
        default=FINAL_REPORT_FILE,
    )
    parser.add_argument(
        "--report_file_name_org",
        type=str,
        help="Org report file name",
        default=FINAL_REPORT_FILE,
    )
    parser.add_argument(
        "--report_file_name_repo",
        type=str,
        help="Repo report file name",
        default=FINAL_REPORT_FILE,
    )
    parser.add_argument(
        "--report_file_name_instance",
        type=str,
        help="Report file name",
        default=REPORT_FILE,
    )
    parser.add_argument(
        "--instance_workdir",
        type=str,
        help="Instance workdir",
        default=INSTANCE_WORKDIR,
    )
    parser.add_argument(
        "--log_dir",
        type=Path,
        help="Path to the log dir",
        default=None,
    )
    parser.add_argument(
        "--log_level",
        type=str,
        help="Log level",
        default="INFO",
    )
    parser.add_argument(
        "--log_to_console",
        type=bool,
        help="Print log to console",
        default=True,
    )

    return parser


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


def init_logger(workdir: Path, log_level: str, log_to_console: bool) -> logging.Logger:
    logger = setup_logger(workdir, GENERATE_REPORT_LOG_FILE, log_level, log_to_console)
    logger.info("Initialize logger successfully.")
    return logger


def create_log_helper_instance(org: str, repo: str, number: int) -> Instance:
    pr = PullRequest(
        org=org,
        repo=repo,
        number=number,
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


def generate_instance_report(
    org: str,
    repo: str,
    number: str,
    instance_dir: Path,
    to_disk_instance: bool = True,
    report_file_name_instance: str = REPORT_FILE,
) -> Report:
    if isinstance(number, str):
        if number.isdigit():
            number = int(number)
        elif number.startswith("pr-") and number[3:].isdigit():
            number = int(number[3:])
        else:
            raise ValueError(f"Invalid number: {number}")

    instance = create_log_helper_instance(org, repo, number)

    with open(instance_dir / RUN_LOG_FILE, "r", encoding="utf-8") as f:
        output_run = f.read()

    with open(instance_dir / TEST_PATCH_RUN_LOG_FILE, "r", encoding="utf-8") as f:
        output_test = f.read()

    with open(instance_dir / FIX_PATCH_RUN_LOG_FILE, "r", encoding="utf-8") as f:
        output_fix = f.read()

    report = generate_report(instance, output_run, output_test, output_fix)

    if to_disk_instance:
        with open(instance_dir / report_file_name_instance, "w", encoding="utf-8") as f:
            f.write(report.json())

    return report


def generate_repo_report(
    org: str,
    repo: str,
    repo_dir: Path,
    logger: logging.Logger,
    specific_instances: Optional[set[str]] = None,
    skip_instances: Optional[set[str]] = None,
    to_disk_instance: bool = True,
    to_disk_repo: bool = True,
    report_file_name_instance: str = REPORT_FILE,
    report_file_name_repo: str = FINAL_REPORT_FILE,
) -> list[Report]:
    logger.debug(f"Start to generate repo reports for {org}/{repo} in {repo_dir}...")

    if specific_instances:
        re_instance = re.compile(r"(.+)/(.+):(pr-\d+)")
        instances: set[str] = set()
        for instance in specific_instances:
            match = re_instance.match(instance)
            if not match:
                continue
            instance_org, instance_repo, instance_number = match.groups()
            if instance_org == org and instance_repo == repo:
                instances.add(instance_number)
        specific_instances = instances

    if specific_instances:
        re_instance = re.compile(r"(.+):(pr-\d+)")
        instances: set[str] = set()
        for instance in specific_instances:
            match = re_instance.match(instance)
            if not match:
                continue
            instance_repo, instance_number = match.groups()
            if instance_repo == repo:
                instances.add(instance_number)
        specific_instances = instances

    skip_instances = skip_instances if skip_instances else set()
    if not specific_instances or len(specific_instances) == 0:
        specific_instances: set[str] = set()
        re_instance = re.compile(r"(pr-\d+)")
        for instance_dir in repo_dir.iterdir():
            logger.debug(f"Checking instance_dir: {org}/{repo}:{instance_dir.name}")
            if not instance_dir.is_dir():
                continue

            match = re_instance.match(instance_dir.name)
            if not match or f"{org}/{repo}:{instance_dir.name}" in skip_instances:
                continue

            instance = match.group(1)
            specific_instances.add(instance)

    reports: list[Report] = []
    for instance in specific_instances:
        instance_dir = repo_dir / instance
        if not instance_dir.exists():
            logger.warning(f"No instance found for {org}/{repo}:{instance}")
            continue

        run_log = instance_dir / RUN_LOG_FILE
        test_patch_log = instance_dir / TEST_PATCH_RUN_LOG_FILE
        fix_patch_log = instance_dir / FIX_PATCH_RUN_LOG_FILE
        if not (
            run_log.exists() and test_patch_log.exists() and fix_patch_log.exists()
        ):
            logger.warning(
                f"Some logs are missing for {org}/{repo}:{instance}, run_log: {run_log.exists()}, test_patch_log: {test_patch_log.exists()}, fix_patch_log: {fix_patch_log.exists()}"
            )
            continue

        try:
            logger.debug(f"Start to generate report for {org}/{repo}:{instance}")
            report = generate_instance_report(
                org,
                repo,
                instance,
                instance_dir,
                to_disk_instance,
                report_file_name_instance,
            )
        except Exception as e:
            logging.error(f"Failed to generate report for {org}/{repo}:{instance}: {e}")
            continue
        else:
            logger.debug(f"Generate report for {org}/{repo}:{instance} successfully.")

        ok, error_msg = report.check()
        if not ok:
            logger.debug(
                f"Report for {org}/{repo}:{instance} is not valid: {error_msg}"
            )
            continue

        reports.append(report)

    if to_disk_repo:
        reports.sort(reverse=True)
        with open(repo_dir / report_file_name_repo, "w", encoding="utf-8") as f:
            for report in reports:
                f.write(report.json())
                f.write("\n")

    logger.info(
        f"Generate repo reports for {org}/{repo} successfully with {len(reports)}/{len(specific_instances)} reports."
    )

    return reports


def generate_org_report(
    org: str,
    org_dir: Path,
    logger: logging.Logger,
    specific_repos: Optional[set[str]] = None,
    specific_instances: Optional[set[str]] = None,
    skip_repos: Optional[set[str]] = None,
    skip_instances: Optional[set[str]] = None,
    to_disk_org: bool = True,
    to_disk_repo: bool = True,
    to_disk_instance: bool = True,
    report_file_name_org: str = FINAL_REPORT_FILE,
    report_file_name_repo: str = FINAL_REPORT_FILE,
    report_file_name_instance: str = REPORT_FILE,
    instance_workdir: Optional[str] = INSTANCE_WORKDIR,
) -> list[Report]:
    logger.debug(f"Start to generate org reports for {org} in {org_dir}...")

    if specific_repos:
        re_repo = re.compile(r"(.+)/(.+)")
        repos: set[str] = set()
        for repo in specific_repos:
            match = re_repo.match(repo)
            if not match:
                continue
            repo_org, repo_repo = match.groups()
            if repo_org == org:
                repos.add(repo_repo)
        specific_repos = repos

    skip_repos = skip_repos if skip_repos else set()
    if not specific_repos or len(specific_repos) == 0:
        specific_repos = set()
        for repo_dir in org_dir.iterdir():
            if not repo_dir.is_dir() or f"{org}/{repo_dir.name}" in skip_repos:
                continue
            specific_repos.add(repo_dir.name)

    reports: list[Report] = []
    for repo in specific_repos:
        repo_dir = org_dir / repo
        if not repo_dir.exists():
            logger.warning(f"No repo found for {org}/{repo}")
            continue

        if instance_workdir:
            repo_dir = repo_dir / instance_workdir

        repo_reports = generate_repo_report(
            org=org,
            repo=repo,
            repo_dir=repo_dir,
            logger=logger,
            specific_instances=specific_instances,
            skip_instances=skip_instances,
            to_disk_repo=to_disk_repo,
            to_disk_instance=to_disk_instance,
            report_file_name_repo=report_file_name_repo,
            report_file_name_instance=report_file_name_instance,
        )
        reports.extend(repo_reports)

    if to_disk_org:
        reports.sort(reverse=True)
        with open(org_dir / report_file_name_org, "w", encoding="utf-8") as f:
            for report in reports:
                f.write(report.json())
                f.write("\n")

    logger.debug(
        f"Generate org reports for {org} successfully with {len(reports)} reports."
    )

    return reports


def generate_workdir_report(
    workdir: Path,
    logger: logging.Logger,
    specific_orgs: Optional[set[str]] = None,
    specific_repos: Optional[set[str]] = None,
    specific_instances: Optional[set[str]] = None,
    skip_orgs: Optional[set[str]] = None,
    skip_repos: Optional[set[str]] = None,
    skip_instances: Optional[set[str]] = None,
    to_disk_workdir: bool = True,
    to_disk_org: bool = True,
    to_disk_repo: bool = True,
    to_disk_instance: bool = True,
    report_file_name_workdir: str = FINAL_REPORT_FILE,
    report_file_name_org: str = FINAL_REPORT_FILE,
    report_file_name_repo: str = FINAL_REPORT_FILE,
    report_file_name_instance: str = REPORT_FILE,
    instance_workdir: Optional[str] = INSTANCE_WORKDIR,
) -> list[Report]:
    logger.debug(f"Start to generate workdir reports for {workdir}...")

    skip_orgs = skip_orgs if skip_orgs else set()
    if not specific_orgs or len(specific_orgs) == 0:
        specific_orgs = set()
        for org_dir in workdir.iterdir():
            if not org_dir.is_dir() or org_dir.name in skip_orgs:
                continue
            specific_orgs.add(org_dir.name)

    reports: list[Report] = []
    for org in specific_orgs:
        org_dir = workdir / org
        if not org_dir.exists():
            logger.warning(f"No org found for {org}")
            continue

        org_reports = generate_org_report(
            org=org,
            org_dir=org_dir,
            logger=logger,
            specific_repos=specific_repos,
            specific_instances=specific_instances,
            skip_repos=skip_repos,
            skip_instances=skip_instances,
            to_disk_org=to_disk_org,
            to_disk_repo=to_disk_repo,
            to_disk_instance=to_disk_instance,
            report_file_name_instance=report_file_name_instance,
            report_file_name_repo=report_file_name_repo,
            report_file_name_org=report_file_name_org,
            instance_workdir=instance_workdir,
        )
        reports.extend(org_reports)

    if to_disk_workdir:
        reports.sort(reverse=True)
        with open(workdir / report_file_name_workdir, "w", encoding="utf-8") as f:
            for report in reports:
                f.write(report.json())
                f.write("\n")

    logger.debug(
        f"Generate workdir reports for {workdir} successfully with {len(reports)} reports."
    )

    return reports


@dataclass_json
@dataclass
class CliArgs:
    workdir: Path
    mode: Literal["workdir", "org", "repo", "instance"]
    org: Optional[str]
    repo: Optional[str]
    number: Optional[str]
    specific_orgs: Optional[set[str]]
    specific_repos: Optional[set[str]]
    specific_instances: Optional[set[str]]
    skip_orgs: Optional[set[str]]
    skip_repos: Optional[set[str]]
    skip_instances: Optional[set[str]]
    to_disk_workdir: bool
    to_disk_org: bool
    to_disk_repo: bool
    to_disk_instance: bool
    report_file_name_workdir: Optional[str]
    report_file_name_org: Optional[str]
    report_file_name_repo: Optional[str]
    report_file_name_instance: Optional[str]
    instance_workdir: Optional[str]
    log_dir: Path
    log_level: str
    log_to_console: bool

    def __post_init__(self):
        if not self.workdir:
            raise ValueError("Invalid workdir: None")
        if isinstance(self.workdir, str):
            self.workdir = Path(self.workdir)
        if self.mode not in ["workdir", "org", "repo", "instance"]:
            raise ValueError(f"Invalid mode: {self.mode}")
        if not self.log_dir:
            raise ValueError("Invalid log_dir: None")
        if isinstance(self.log_dir, str):
            self.log_dir = Path(self.log_dir)

    @classmethod
    def from_dict(cls, d: dict) -> "CliArgs":
        return cls(**d)

    @classmethod
    def from_json(cls, json_str: str) -> "CliArgs":
        return cls.from_dict(cls.schema().loads(json_str))

    def dict(self) -> dict:
        return asdict(self)

    def json(self) -> str:
        return self.to_json(ensure_ascii=False)

    def check_instance_mode(self) -> Tuple[bool, str]:
        if not self.org:
            return (False, "Invalid org: None")
        if not self.repo:
            return (False, "Invalid repo: None")
        if not self.number:
            return (False, "Invalid number: None")
        if isinstance(self.number, int) or self.number.isdigit():
            self.number = f"pr-{self.number}"

        workdir = self.workdir
        run_log = workdir / RUN_LOG_FILE
        test_patch_log = workdir / TEST_PATCH_RUN_LOG_FILE
        fix_patch_log = workdir / FIX_PATCH_RUN_LOG_FILE

        if run_log.exists() and test_patch_log.exists() and fix_patch_log.exists():
            return (True, "")

        if run_log.exists() or test_patch_log.exists() or fix_patch_log.exists():
            return (
                False,
                f"Some logs are missing in `{workdir}`, run_log: {run_log.exists()}, test_patch_log: {test_patch_log.exists()}, fix_patch_log: {fix_patch_log.exists()}",
            )

        if self.instance_workdir:
            workdir = (
                workdir / self.org / self.repo / self.instance_workdir / self.number
            )
        else:
            workdir = workdir / self.org / self.repo / self.number

        run_log = workdir / RUN_LOG_FILE
        test_patch_log = workdir / TEST_PATCH_RUN_LOG_FILE
        fix_patch_log = workdir / FIX_PATCH_RUN_LOG_FILE

        if run_log.exists() and test_patch_log.exists() and fix_patch_log.exists():
            self.workdir = workdir
            return (True, "")

        return (
            False,
            f"Some logs are missing in `{workdir}`, run_log: {run_log.exists()}, test_patch_log: {test_patch_log.exists()}, fix_patch_log: {fix_patch_log.exists()}",
        )

    def check_repo_mode(self) -> Tuple[bool, str]:
        if not self.org:
            return (False, "Invalid org: None")
        if not self.repo:
            return (False, "Invalid repo: None")
        if self.specific_instances:
            specific_instances: set[str] = set()
            for instance in self.specific_instances:
                if isinstance(instance, int) or instance.isdigit():
                    specific_instances.add(f"pr-{instance}")
                elif instance.startswith("pr-") and instance[3:].isdigit():
                    specific_instances.add(instance)
                else:
                    return (
                        False,
                        f"Invalid specific_instances: {self.specific_instances}",
                    )
            self.specific_instances = specific_instances

        workdir = self.workdir
        for instance_dir in workdir.iterdir():
            if (
                instance_dir.is_dir()
                and instance_dir.name.startswith("pr-")
                and instance_dir.name[3:].isdigit()
            ):
                return (True, "")

        if self.instance_workdir:
            workdir = workdir / self.org / self.repo / self.instance_workdir
        else:
            workdir = workdir / self.org / self.repo

        for instance_dir in workdir.iterdir():
            if (
                instance_dir.is_dir()
                and instance_dir.name.startswith("pr-")
                and instance_dir.name[3:].isdigit()
            ):
                self.workdir = workdir
                return (True, "")

        return (False, f"No instance found in `{workdir}`")

    def check_org_mode(self) -> Tuple[bool, str]:
        if not self.org:
            return (False, "Invalid org: None")

        workdir = self.workdir
        for repo_dir in workdir.iterdir():
            if not repo_dir.is_dir():
                continue

            if self.instance_workdir:
                repo_dir = repo_dir / self.instance_workdir

            if not repo_dir.exists():
                continue

            for instance_dir in repo_dir.iterdir():
                if (
                    instance_dir.exists()
                    and instance_dir.is_dir()
                    and instance_dir.name.startswith("pr-")
                    and instance_dir.name[3:].isdigit()
                ):
                    self.workdir = workdir
                    return (True, "")

        workdir = workdir / self.org
        for repo_dir in workdir.iterdir():
            if not repo_dir.is_dir():
                continue

            if self.instance_workdir:
                repo_dir = repo_dir / self.instance_workdir
            for instance_dir in repo_dir.iterdir():
                if (
                    instance_dir.exists()
                    and instance_dir.is_dir()
                    and instance_dir.name.startswith("pr-")
                    and instance_dir.name[3:].isdigit()
                ):
                    self.workdir = workdir
                    return (True, "")

        return (False, f"No instance found in `{workdir}`")

    def check_workdir_mode(self) -> Tuple[bool, str]:
        self.specific_orgs = self.specific_orgs if self.specific_orgs else set()
        self.skip_orgs = self.skip_orgs if self.skip_orgs else set()

        def fill_org_set(orgs: set[str], repos: set[str]) -> Tuple[bool, str]:
            if not repos:
                return (True, "")
            re_repo = re.compile(r"(.+)/(.+)")
            for repo in repos:
                repo_match = re_repo.match(repo)
                if not repo_match:
                    return (False, f"Invalid repo format: {repo}, expected: org/repo")
                org, repo = repo_match.groups()
                orgs.add(org)
            return (True, "")

        ok, error_msg = fill_org_set(self.specific_orgs, self.specific_repos)
        if not ok:
            return (False, error_msg)
        ok, error_msg = fill_org_set(self.skip_orgs, self.skip_repos)
        if not ok:
            return (False, error_msg)

        def check_instance_set(instances: set[str]) -> Tuple[bool, str]:
            if not instances:
                return (True, "")
            re_specific_instance = re.compile(r"(.+/.+:pr-\d+)")
            for instance in instances:
                if re_specific_instance.match(instance):
                    continue
                return (False, f"Invalid specific_instances: {instances}")

        ok, error_msg = check_instance_set(self.specific_instances)
        if not ok:
            return (False, error_msg)
        ok, error_msg = check_instance_set(self.skip_instances)
        if not ok:
            return (False, error_msg)

        for org_dir in self.workdir.iterdir():
            if not org_dir.is_dir():
                continue

            for repo_dir in org_dir.iterdir():
                if not repo_dir.is_dir():
                    continue

                if self.instance_workdir:
                    repo_dir = repo_dir / self.instance_workdir
                for instance_dir in repo_dir.iterdir():
                    if (
                        instance_dir.exists()
                        and instance_dir.is_dir()
                        and instance_dir.name.startswith("pr-")
                        and instance_dir.name[3:].isdigit()
                    ):
                        return (True, "")

        return (False, f"No instance found in `{self.workdir}`")

    def run_instance_mode(self):
        ok, error_msg = self.check_instance_mode()
        if not ok:
            raise ValueError(error_msg)

        report = generate_instance_report(
            self.org,
            self.repo,
            self.number,
            self.workdir,
            self.to_disk_instance,
            self.report_file_name_instance,
        )

        print(report.check())

    def run_repo_mode(self):
        ok, error_msg = self.check_repo_mode()
        if not ok:
            raise ValueError(error_msg)

        logger = init_logger(cli.log_dir, cli.log_level, cli.log_to_console)
        generate_repo_report(
            self.org,
            self.repo,
            self.workdir,
            logger,
            self.specific_instances,
            self.skip_instances,
            self.to_disk_instance,
            self.to_disk_repo,
            self.report_file_name_instance,
            self.report_file_name_repo,
        )

    def run_org_mode(self):
        ok, error_msg = self.check_org_mode()
        if not ok:
            raise ValueError(error_msg)

        logger = init_logger(cli.log_dir, cli.log_level, cli.log_to_console)
        generate_org_report(
            org=self.org,
            org_dir=self.workdir,
            logger=logger,
            specific_repos=self.specific_repos,
            specific_instances=self.specific_instances,
            skip_repos=self.skip_repos,
            skip_instances=self.skip_instances,
            to_disk_org=self.to_disk_org,
            to_disk_repo=self.to_disk_repo,
            to_disk_instance=self.to_disk_instance,
            report_file_name_org=self.report_file_name_org,
            report_file_name_repo=self.report_file_name_repo,
            report_file_name_instance=self.report_file_name_instance,
            instance_workdir=self.instance_workdir,
        )

    def run_workdir_mode(self):
        ok, error_msg = self.check_workdir_mode()
        if not ok:
            raise ValueError(error_msg)

        logger = init_logger(cli.log_dir, cli.log_level, cli.log_to_console)
        generate_workdir_report(
            workdir=self.workdir,
            logger=logger,
            specific_orgs=self.specific_orgs,
            specific_repos=self.specific_repos,
            specific_instances=self.specific_instances,
            skip_orgs=self.skip_orgs,
            skip_repos=self.skip_repos,
            skip_instances=self.skip_instances,
            to_disk_workdir=self.to_disk_org,
            to_disk_org=self.to_disk_org,
            to_disk_repo=self.to_disk_repo,
            to_disk_instance=self.to_disk_instance,
            report_file_name_workdir=self.report_file_name_org,
            report_file_name_org=self.report_file_name_org,
            report_file_name_repo=self.report_file_name_repo,
            report_file_name_instance=self.report_file_name_instance,
            instance_workdir=self.instance_workdir,
        )


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    cli = CliArgs.from_dict(vars(args))

    if cli.mode == "workdir":
        cli.run_workdir_mode()
    elif cli.mode == "org":
        cli.run_org_mode()
    elif cli.mode == "repo":
        cli.run_repo_mode()
    elif cli.mode == "instance":
        cli.run_instance_mode()
    else:
        raise ValueError(f"Invalid mode: {cli.mode}")
