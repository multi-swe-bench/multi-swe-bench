#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout 4609f22aff1ad88b81e749e2536761d6ee364d1f
bash /home/check_git_changes.sh

cargo test || true

