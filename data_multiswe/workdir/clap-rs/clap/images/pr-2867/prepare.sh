#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 1f17d9e8ba5b64baca9e2d49c1b097b167bf4df6
bash /home/check_git_changes.sh

cargo test || true

