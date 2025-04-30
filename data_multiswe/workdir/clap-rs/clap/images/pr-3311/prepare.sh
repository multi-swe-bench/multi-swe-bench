#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 4b60440d91c02a472e31e66117c34b0fc9e6d09a
bash /home/check_git_changes.sh

cargo test || true

