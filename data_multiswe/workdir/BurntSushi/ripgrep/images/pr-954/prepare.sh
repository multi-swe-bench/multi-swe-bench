#!/bin/bash
set -e

cd /home/ripgrep
git reset --hard
bash /home/check_git_changes.sh
git checkout 223d7d9846bff4a9aaf6ba84f5662a1ee7ffa900
bash /home/check_git_changes.sh

cargo test || true

