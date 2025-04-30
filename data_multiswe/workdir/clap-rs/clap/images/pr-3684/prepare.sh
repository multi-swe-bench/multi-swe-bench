#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 17ec7757891a38965e8492f7a0a48e674a9536eb
bash /home/check_git_changes.sh

cargo test || true

