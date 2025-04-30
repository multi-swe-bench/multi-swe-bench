#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 62588bd82c16e081469b195d005103319adda220
bash /home/check_git_changes.sh

cargo test || true

