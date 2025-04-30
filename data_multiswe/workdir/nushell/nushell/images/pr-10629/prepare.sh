#!/bin/bash
set -e

cd /home/nushell
git reset --hard
bash /home/check_git_changes.sh
git checkout 399319476aa4decd7cced93488180d96e56bad64
bash /home/check_git_changes.sh

cargo test || true

