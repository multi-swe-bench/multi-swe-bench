#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout a5494573af5aa217fb5af36a569bfa31f055eb9f
bash /home/check_git_changes.sh

cargo test || true

