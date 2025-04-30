#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout e7033f775f5a435a827c9a16fc7f1538db2f31e7
bash /home/check_git_changes.sh

cargo test || true

