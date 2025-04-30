#!/bin/bash
set -e

cd /home/serde
git reset --hard
bash /home/check_git_changes.sh
git checkout 5b24f88e73caa9c607527b5b4696fc34263cd238
bash /home/check_git_changes.sh

cargo test || true

