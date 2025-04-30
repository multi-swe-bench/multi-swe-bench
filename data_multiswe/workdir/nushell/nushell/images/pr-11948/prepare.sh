#!/bin/bash
set -e

cd /home/nushell
git reset --hard
bash /home/check_git_changes.sh
git checkout 6e37ad0275cb23c5a8a933ba6a46a45d70f74910
bash /home/check_git_changes.sh

cargo test || true

