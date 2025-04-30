#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout c9e75785c84a441199992ed38e49aeba2f061a24
bash /home/check_git_changes.sh

cargo test || true

