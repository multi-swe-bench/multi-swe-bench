#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 54a153021b39803843c45a0fa976bc5ea0898bda
bash /home/check_git_changes.sh

cargo test || true

