#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout 338e13b04baa3cf8db3feb1ba2266c0070a9efdf
bash /home/check_git_changes.sh

cargo test || true

