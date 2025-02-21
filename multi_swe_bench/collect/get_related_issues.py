import argparse
import json
import random
import re
import sys
from pathlib import Path

from github import Auth, Github
from tqdm import tqdm

from multi_swe_bench.collect.util import get_tokens


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
        "--filtered_prs_file", type=Path, required=True, help="Path to pull file."
    )

    return parser


def get_github(token) -> Github:
    auth = Auth.Token(token)
    return Github(auth=auth, per_page=100)


def get_top_repositories(g: Github, language=None, limit=10):
    query = f"stars:>1"
    if language:
        query += f" language:{language}"

    # 搜索仓库，按 stars 排序
    result = g.search_repositories(query=query, sort="stars", order="desc")

    top_repos = []
    for repo in result[:limit]:
        top_repos.append((repo.full_name, repo.stargazers_count))

    return top_repos


def main(tokens, out_dir: Path, filtered_prs_file: Path):
    print("starting get all related issues")
    print(f"Output directory: {out_dir}")
    print(f"Tokens: {tokens}")
    print(f"Pull file: {filtered_prs_file}")

    org_repo_re = re.compile(r"(.+)__(.+)_filtered_prs.jsonl")
    m = org_repo_re.match(filtered_prs_file.name)
    if not m:
        print(f"Error: Invalid pull file name: {filtered_prs_file.name}")
        sys.exit(1)

    org = m.group(1)
    repo = m.group(2)
    print(f"Org: {org}")
    print(f"Repo: {repo}")

    with open(filtered_prs_file, "r", encoding="utf-8") as file:
        filtered_prs = [json.loads(line) for line in file]
        target_issues = set()
        for pr in filtered_prs:
            for issue in pr["resolved_issues"]:
                target_issues.add(issue)

    g = get_github(random.choice(tokens))
    r = g.get_repo(f"{org}/{repo}")

    with open(
        out_dir / f"{org}__{repo}_related_issues.jsonl", "w", encoding="utf-8"
    ) as out_file:
        for issue in tqdm(r.get_issues(state="all"), desc="Issues"):
            if issue.number not in target_issues:
                continue

            out_file.write(
                json.dumps(
                    {
                        "org": org,
                        "repo": repo,
                        "number": issue.number,
                        "state": issue.state,
                        "title": issue.title,
                        "body": issue.body,
                    },
                    ensure_ascii=False,
                )
                + "\n",
            )


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    tokens = get_tokens(args.tokens)

    main(tokens, Path.cwd() / args.out_dir, args.filtered_prs_file)
