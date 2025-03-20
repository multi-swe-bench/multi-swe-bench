import argparse
import json
import random
import re
import sys
from pathlib import Path

from github import Auth, Github
from tqdm import tqdm


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="A command-line tool for processing repositories."
    )
    parser.add_argument(
        "--out_dir", type=Path, required=True, help="Output directory path."
    )
    parser.add_argument(
        "--prs_file", type=Path, required=True, help="Path to pull file."
    )

    return parser


def extract_resolved_issues(pull: dict) -> list[str]:
    # Define 1. issue number regex pattern 2. comment regex pattern 3. keywords
    issues_pat = re.compile(r"(\w+)\s+\#(\d+)")
    comments_pat = re.compile(r"(?s)<!--.*?-->")
    keywords = {
        "close",
        "closes",
        "closed",
        "fix",
        "fixes",
        "fixed",
        "resolve",
        "resolves",
        "resolved",
    }

    # Construct text to search over for issue numbers from PR body and commit messages
    text = pull["title"] if pull["title"] else ""
    text += "\n" + (pull["body"] if pull["body"] else "")
    text += "\n" + "\n".join([commit["message"] for commit in pull["commits"]])

    # Remove comments from text
    text = comments_pat.sub("", text)
    # Look for issue numbers in text via scraping <keyword, number> patterns
    references = dict(issues_pat.findall(text))
    resolved_issues = set()
    if references:
        for word, issue_num in references.items():
            if word.lower() in keywords:
                resolved_issues.add(int(issue_num))

    if 0 in resolved_issues:
        resolved_issues.remove(0)

    return list(resolved_issues)


def get_github(token) -> Github:
    auth = Auth.Token(token)
    return Github(auth=auth, per_page=100)


def main(tokens: list[str], out_dir: Path, prs_file: Path, skip_commit_message: bool):
    print("starting filter to obtain required pull requests")
    print(f"Output directory: {out_dir}")
    print((f"All Pull Requests: {prs_file}"))
    print(f"Skip commit message: {skip_commit_message}")

    org_repo_re = re.compile(r"(.+)__(.+)_prs.jsonl")
    m = org_repo_re.match(prs_file.name)
    if not m:
        print(f"Error: Invalid pull file name: {prs_file.name}")
        sys.exit(1)

    org = m.group(1)
    repo = m.group(2)
    print(f"Org: {org}")
    print(f"Repo: {repo}")

    if not skip_commit_message:
        g = get_github(random.choice(tokens))
        r = g.get_repo(f"{org}/{repo}")

    with open(
        out_dir / f"{org}__{repo}_filtered_prs.jsonl",
        "w",
        encoding="utf-8",
    ) as out_file, open(prs_file, "r", encoding="utf-8") as in_file:
        prs = [json.loads(line) for line in in_file]

        for pull in tqdm(prs, desc="Pull Requests"):
            if pull["state"] != "closed":
                continue

            pull["commits"] = []
            if not skip_commit_message:
                pr = r.get_pull(pull["number"])
                pull["commits"] = [
                    {
                        "sha": commit.sha,
                        "parents": [parent.sha for parent in commit.parents],
                        "message": commit.commit.message,
                    }
                    for commit in pr.get_commits()
                ]

            resolved_issues = extract_resolved_issues(pull)
            if len(resolved_issues) == 0:
                continue

            pull["resolved_issues"] = resolved_issues
            out_file.write(json.dumps(pull, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    main(Path.cwd() / args.out_dir, args.prs_file)
