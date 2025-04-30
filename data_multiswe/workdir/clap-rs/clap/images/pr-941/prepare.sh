#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout dd485ebc6a13075dfb7773dd81a6c11f7d0a3a6e
bash /home/check_git_changes.sh

cargo test || true

