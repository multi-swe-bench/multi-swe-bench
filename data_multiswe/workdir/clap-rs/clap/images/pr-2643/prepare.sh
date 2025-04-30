#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 6ea223bc6e580db88b0cbe073ddd227434ad1127
bash /home/check_git_changes.sh

cargo test || true

