#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 3ca1b7709408f8bb3ec6b48ac2b4854aabe643b7
bash /home/check_git_changes.sh

cargo test || true

