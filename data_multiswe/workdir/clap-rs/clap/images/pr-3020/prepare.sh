#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 91b5b395f522f1019dc499e9b52c545d640a954f
bash /home/check_git_changes.sh

cargo test || true

