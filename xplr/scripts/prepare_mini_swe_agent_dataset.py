#!/usr/bin/env python3
"""Fetch mini-swe-agent PR metadata and build a raw_dataset JSONL file."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable

API_ROOT = "https://api.github.com/repos/SWE-agent/mini-swe-agent"
PATCH_ROOT = "https://patch-diff.githubusercontent.com/raw/SWE-agent/mini-swe-agent"

def http_get(url: str, token: str | None = None, accept: str | None = None) -> bytes:
    headers = {"User-Agent": "multi-swe-bench-autogen/0.1"}
    if accept:
        headers["Accept"] = accept
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def is_test_path(path: str) -> bool:
    path = path.lower()
    parts = path.split("/")
    if any(part.startswith("test") for part in parts):
        return True
    if "tests" in parts:
        return True
    if path.endswith("_test.py") or path.endswith("_tests.py"):
        return True
    return False


def split_patch(patch_text: str) -> tuple[str, str]:
    test_lines: list[str] = []
    fix_lines: list[str] = []
    current_block: list[str] = []
    current_is_test = False

    def flush():
        if not current_block:
            return
        target = test_lines if current_is_test else fix_lines
        target.extend(current_block)
        current_block.clear()

    for line in patch_text.splitlines(keepends=True):
        if line.startswith("diff --git "):
            flush()
            current_block.append(line)
            current_is_test = False
            continue
        current_block.append(line)
        if line.startswith("+++ b/"):
            path = line[6:].strip()
            current_is_test = is_test_path(path)

    flush()
    return ("".join(test_lines), "".join(fix_lines))


def build_entry(pr_data: dict, patch_text: str) -> dict:
    test_patch, fix_patch = split_patch(patch_text)
    if not fix_patch:
        fix_patch = patch_text
        test_patch = ""
    base = pr_data["base"]
    entry = {
        "org": pr_data["base"]["repo"]["owner"]["login"],
        "repo": pr_data["base"]["repo"]["name"],
        "number": pr_data["number"],
        "state": pr_data["state"],
        "title": pr_data.get("title") or "",
        "body": pr_data.get("body"),
        "base": {
            "label": f"{base['repo']['full_name']}:{base['ref']}",
            "ref": base["ref"],
            "sha": base["sha"],
        },
        "resolved_issues": [],
        "fix_patch": fix_patch,
        "test_patch": test_patch,
        "tag": "",
        "number_interval": "",
        "lang": "python",
    }
    return entry


def fetch_pull(pr_number: int, token: str | None) -> dict:
    url = f"{API_ROOT}/pulls/{pr_number}"
    payload = http_get(url, token=token, accept="application/vnd.github+json")
    return json.loads(payload)


def fetch_patch(pr_number: int, token: str | None) -> str:
    url = f"{PATCH_ROOT}/pull/{pr_number}.patch"
    payload = http_get(url, token=None, accept="text/plain")
    return payload.decode("utf-8")


def parse_prs(values: Iterable[str]) -> list[int]:
    result: list[int] = []
    for value in values:
        if "-" in value:
            start, end = value.split("-", 1)
            result.extend(range(int(start), int(end) + 1))
        else:
            result.append(int(value))
    return sorted(set(result))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prs", nargs="*", default=["1"], help="PR numbers or ranges (e.g. 1 5-7)")
    parser.add_argument("--output", default="xplr/artifacts/raw/SWE-agent__mini-swe-agent_raw_dataset.jsonl")
    parser.add_argument("--patch-dir", default="xplr/artifacts/raw/patches")
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN"))
    args = parser.parse_args()

    pr_numbers = parse_prs(args.prs)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    patch_dir = Path(args.patch_dir)
    patch_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    for pr_number in pr_numbers:
        print(f"Fetching PR #{pr_number}...")
        data = fetch_pull(pr_number, args.token)
        patch_text = fetch_patch(pr_number, args.token)
        patch_file = patch_dir / f"pr-{pr_number}.patch"
        patch_file.write_text(patch_text, encoding="utf-8")
        entry = build_entry(data, patch_text)
        records.append(entry)
        time.sleep(0.5)

    with output_path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Wrote {len(records)} entries to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
