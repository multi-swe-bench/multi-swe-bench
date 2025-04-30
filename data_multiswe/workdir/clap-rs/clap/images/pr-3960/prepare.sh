#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 5e02445ce5f6eb89933d5985736c69059d0dc7af
bash /home/check_git_changes.sh

cargo test || true

