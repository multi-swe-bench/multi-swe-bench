import argparse
import json
import random
import re
import sys
import time
from pathlib import Path
from typing import Optional

import requests
from tqdm import tqdm
from unidiff import PatchSet

from multi_swe_bench.collect.util import get_tokens, optional_int


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="A command-line tool for processing repositories."
    )
    parser.add_argument(
        "--out_dir", type=Path, required=True, help="Output directory path."
    )
    parser.add_argument(
        "--tokens",
        type=str,
        nargs="*",
        default=None,
        help="API token(s) or path to token file.",
    )
    parser.add_argument(
        "--filtered-prs-with-issues-file",
        type=Path,
        required=True,
        help="Filtered PRs with issues file.",
    )
    parser.add_argument(
        "--delay-on-error",
        type=optional_int,
        default=300,
        help="Delay in seconds before retrying on error. If none, exit on error.",
    )
    parser.add_argument(
        "--retry-attempts",
        type=int,
        default=3,
        help="Number of attempts to retry on error.",
    )

    return parser


def extract_patches(pull: dict, token: str) -> tuple[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    patch = requests.get(pull["diff_url"], headers=headers).text
    test_patch = ""
    fix_patch = ""
    for hunk in PatchSet(patch):
        if any(
            test_word in hunk.path for test_word in ["test", "tests", "e2e", "testing"]
        ):
            test_patch += str(hunk)
        else:
            fix_patch += str(hunk)
    return fix_patch, test_patch


def get_failed_number(log_file: Path) -> Optional[int]:
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as file:
            n = file.read().strip()
            if n != "":
                return int(n)
    return None


def set_failed_number(log_file: Path, failed_number: int):
    with open(log_file, "w", encoding="utf-8") as file:
        file.write(f"{failed_number}")


def main(
    tokens: list[str],
    out_dir: Path,
    filtered_prs_with_issues_file: Path,
    delay_on_error: int,
    retry_attempts: int,
):
    print("starting build complete dataset")
    print(f"Tokens: {tokens}")
    print(f"Output directory: {out_dir}")
    print(f"Dataset file: {filtered_prs_with_issues_file}")
    print(f"Delay on error: {delay_on_error}")
    print(f"Retry attempts: {retry_attempts}")

    org_repo_re = re.compile(r"(.+)__(.+)_filtered_prs_with_issues.jsonl")
    m = org_repo_re.match(filtered_prs_with_issues_file.name)
    if not m:
        print(f"Error: Invalid pull file name: {filtered_prs_with_issues_file.name}")
        sys.exit(1)

    org = m.group(1)
    repo = m.group(2)
    print(f"Org: {org}")
    print(f"Repo: {repo}")

    with open(filtered_prs_with_issues_file, "r", encoding="utf-8") as file:
        filtered_prs_with_issues = [json.loads(line) for line in file]

    try:
        with open(
            out_dir / f"{org}__{repo}_raw_dataset.jsonl", "r", encoding="utf-8"
        ) as file:
            raw_dataset = {}
            for line in file:
                data = json.loads(line)
                raw_dataset[data["number"]] = data
    except FileNotFoundError:
        raw_dataset = {}

    failed_number = max([pr["number"] for pr in filtered_prs_with_issues])

    log_file = out_dir / f"{org}__{repo}_raw_dataset.log"
    last_failed_number = get_failed_number(log_file)
    if last_failed_number is not None:
        failed_number = last_failed_number

    processed_number = min(raw_dataset.keys()) if raw_dataset else failed_number
    print(f"minimum processed number: {processed_number}")

    with open(
        out_dir / f"{org}__{repo}_raw_dataset.jsonl", "a", encoding="utf-8"
    ) as file:
        for pr in tqdm(filtered_prs_with_issues, desc="Building Dataset"):
            if (
                pr["number"] in raw_dataset
                or pr["number"] >= processed_number
                or pr["number"] > failed_number
            ):
                continue

            for attempt in range(retry_attempts):
                try:
                    fix_patch, test_patch = extract_patches(pr, random.choice(tokens))
                    pr["fix_patch"] = fix_patch
                    pr["test_patch"] = test_patch

                    if fix_patch == "" or test_patch == "":
                        break

                    file.write(json.dumps(pr, ensure_ascii=False) + "\n")
                    break
                except Exception as e:
                    set_failed_number(log_file, pr["number"])
                    if delay_on_error is None or attempt == retry_attempts - 1:
                        raise e
                    else:
                        print(
                            f"The {attempt + 1} attempt failed. Sleeping then retrying..."
                        )
                        for i in tqdm(range(delay_on_error), desc="Sleeping"):
                            time.sleep(1)


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    tokens = get_tokens(args.tokens)

    main(
        tokens,
        args.out_dir,
        args.filtered_prs_with_issues_file,
        args.delay_on_error,
        args.retry_attempts,
    )
