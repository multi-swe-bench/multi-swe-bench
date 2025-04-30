#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 6eacd8a7476e352d590c1bfae4b983e9eafae2b3
bash /home/check_git_changes.sh

cargo test || true

