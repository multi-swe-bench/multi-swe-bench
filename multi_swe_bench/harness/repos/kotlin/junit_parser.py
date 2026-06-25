from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Iterable

from multi_swe_bench.harness.test_result import TestResult

Status = str
TestId = str

STATUS_PRIORITY: Dict[Status, int] = {"FAIL": 3, "SKIP": 2, "PASS": 1}
PARAM_RE = re.compile(r"\[.+?\]")
HASH_SUFFIX_RE = re.compile(r"@[0-9a-fA-F]+$")
XML_ROOT_RE = re.compile(r"<testsuites?", re.IGNORECASE)
XML_END_TAGS = ("</testsuites>", "</testsuite>")


def is_parameterized(name: str | None) -> bool:
    return bool(name and PARAM_RE.search(name))


def _strip_hash(part: str | None) -> str:
    part = (part or "").strip()
    return HASH_SUFFIX_RE.sub("", part)


def make_test_id(classname: str | None, name: str | None, fallback: str | None) -> str:
    cls = _strip_hash(classname) or (fallback or "").strip()
    method = _strip_hash(name) or "<unnamed>"
    return f"{cls}.{method}" if cls else method


def _repair_xml(xml_text: str) -> str:
    """Insert missing </testsuite> closing tags before </testsuites>."""
    open_count = len(re.findall(r"<testsuite\b", xml_text, re.IGNORECASE))
    close_count = len(re.findall(r"</testsuite>", xml_text, re.IGNORECASE))
    missing = open_count - close_count
    if missing > 0 and "</testsuites>" in xml_text:
        xml_text = xml_text.replace(
            "</testsuites>", "</testsuite>" * missing + "</testsuites>", 1
        )
    return xml_text


def _load_xml(xml_text: str) -> ET.Element:
    try:
        return ET.fromstring(xml_text)
    except ET.ParseError:
        cleaned = re.sub(r"<!--.*?-->", "", xml_text, flags=re.DOTALL)
        try:
            return ET.fromstring(cleaned)
        except ET.ParseError:
            return ET.fromstring(_repair_xml(cleaned))


def extract_junit_xml(log_text: str) -> str:
    """
    Extract the JUnit XML payload from a log stream.
    """
    match = XML_ROOT_RE.search(log_text)
    if not match:
        raise ValueError("JUnit XML root not found in log")

    start = match.start()
    end = -1
    for tag in XML_END_TAGS:
        idx = log_text.rfind(tag)
        if idx != -1:
            end = max(end, idx + len(tag))

    if end == -1 or end <= start:
        raise ValueError("JUnit XML closing tag not found in log")

    return log_text[start:end]


def parse_junit_xml(
    xml_text: str, *, fallback_suite: str | None = None, drop_parameterized: bool = True
) -> Dict[TestId, Status]:
    """
    Parse a JUnit XML string into a map of test_id -> status.
    """
    xml_text = xml_text.lstrip("\ufeff").strip()
    try:
        root = _load_xml(xml_text)
    except ET.ParseError as exc:
        raise ValueError(f"Failed to parse JUnit XML: {exc}") from exc

    results: Dict[TestId, Status] = {}
    for case in root.iter("testcase"):
        classname = case.get("classname")
        name = case.get("name")

        if drop_parameterized and (is_parameterized(name) or is_parameterized(classname)):
            continue

        test_id = make_test_id(classname, name, fallback_suite)

        status: Status = "PASS"
        if case.find("skipped") is not None:
            status = "SKIP"
        elif case.find("failure") is not None or case.find("error") is not None:
            status = "FAIL"

        prev = results.get(test_id)
        if prev is None or STATUS_PRIORITY[status] > STATUS_PRIORITY[prev]:
            results[test_id] = status

    return results


def parse_junit_file(path: Path, *, drop_parameterized: bool = True) -> Dict[TestId, Status]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return parse_junit_xml(text, fallback_suite=path.stem, drop_parameterized=drop_parameterized)


def parse_junit_paths(paths: Iterable[Path], *, drop_parameterized: bool = True) -> Dict[TestId, Status]:
    results: Dict[TestId, Status] = {}
    for path in paths:
        statuses = parse_junit_file(path, drop_parameterized=drop_parameterized)
        for test_id, status in statuses.items():
            prev = results.get(test_id)
            if prev is None or STATUS_PRIORITY[status] > STATUS_PRIORITY[prev]:
                results[test_id] = status
    return results


def parse_junit_from_log(test_log: str, *, drop_parameterized: bool = True) -> Dict[TestId, Status]:
    candidate_path = Path(test_log.strip())
    if "\n" not in test_log and candidate_path.exists() and candidate_path.is_file():
        return parse_junit_file(candidate_path, drop_parameterized=drop_parameterized)

    try:
        return parse_junit_xml(test_log, drop_parameterized=drop_parameterized)
    except ValueError:
        xml_payload = extract_junit_xml(test_log)
        return parse_junit_xml(xml_payload, drop_parameterized=drop_parameterized)


def to_test_result(status_map: Dict[TestId, Status]) -> TestResult:
    passed = {tid for tid, status in status_map.items() if status == "PASS"}
    failed = {tid for tid, status in status_map.items() if status == "FAIL"}
    skipped = {tid for tid, status in status_map.items() if status == "SKIP"}

    return TestResult(
        passed_count=len(passed),
        failed_count=len(failed),
        skipped_count=len(skipped),
        passed_tests=passed,
        failed_tests=failed,
        skipped_tests=skipped,
    )


def summarize(status_map: Dict[TestId, Status]) -> dict[str, object]:
    """Return counts and explicit lists for convenience."""
    passed = sorted(tid for tid, status in status_map.items() if status == "PASS")
    failed = sorted(tid for tid, status in status_map.items() if status == "FAIL")
    skipped = sorted(tid for tid, status in status_map.items() if status == "SKIP")
    return {
        "passed_count": len(passed),
        "failed_count": len(failed),
        "skipped_count": len(skipped),
        "passed_tests": passed,
        "failed_tests": failed,
        "skipped_tests": skipped,
    }
