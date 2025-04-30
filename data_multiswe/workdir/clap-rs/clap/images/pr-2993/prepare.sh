#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout b9d007d262a7a965c135f1d1b794732117fd5b8e
bash /home/check_git_changes.sh

cargo test || true

