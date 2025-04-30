#!/bin/bash
set -e

cd /home/bytes
git reset --hard
bash /home/check_git_changes.sh
git checkout 291df5acc94b82a48765e67eeb1c1a2074539e68
bash /home/check_git_changes.sh

cargo test || true

