import argparse
import json
import random
from datetime import datetime
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
    parser.add_argument("--org", type=str, required=True, help="Organization name.")
    parser.add_argument("--repo", type=str, required=True, help="Repository name.")

    return parser


def get_github(token) -> Github:
    auth = Auth.Token(token)
    return Github(auth=auth, per_page=100)


def main(tokens: list[str], out_dir: Path, org: str, repo: str):
    print("starting get all pull requests")
    print(f"Output directory: {out_dir}")
    print(f"Tokens: {tokens}")
    print(f"Org: {org}")
    print(f"Repo: {repo}")

    g = get_github(random.choice(tokens))
    r = g.get_repo(f"{org}/{repo}")

    def datetime_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    with open(out_dir / f"{org}__{repo}_prs.jsonl", "w", encoding="utf-8") as file:
        for pull in tqdm(r.get_pulls("all"), desc="Pull Requests"):
            file.write(
                json.dumps(
                    {
                        "org": org,
                        "repo": repo,
                        "number": pull.number,
                        "state": pull.state,
                        "title": pull.title,
                        "body": pull.body,
                        "url": pull.url,
                        "id": pull.id,
                        "node_id": pull.node_id,
                        "html_url": pull.html_url,
                        "diff_url": pull.diff_url,
                        "patch_url": pull.patch_url,
                        "issue_url": pull.issue_url,
                        # "user": pull.user.name,
                        "created_at": datetime_serializer(pull.created_at),
                        "updated_at": datetime_serializer(pull.updated_at),
                        "closed_at": datetime_serializer(pull.closed_at),
                        "merged_at": datetime_serializer(pull.merged_at),
                        "merge_commit_sha": pull.merge_commit_sha,
                        # "assignee": pull.assignee,
                        # "assignees": pull.assignees,
                        # "requested_reviewers": pull.requested_reviewers,
                        # "requested_teams": pull.requested_teams,
                        "labels": [label.name for label in pull.labels],
                        # "milestone": pull.milestone,
                        "draft": pull.draft,
                        "commits_url": pull.commits_url,
                        "review_comments_url": pull.review_comments_url,
                        "review_comment_url": pull.review_comment_url,
                        "comments_url": pull.comments_url,
                        # "head": pull.head.raw_data,
                        "base": pull.base.raw_data,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    tokens = get_tokens(args.tokens)

    main(tokens, Path.cwd() / args.out_dir, args.org, args.repo)
