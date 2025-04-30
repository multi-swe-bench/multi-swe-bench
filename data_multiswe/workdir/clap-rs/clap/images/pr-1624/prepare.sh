#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 1c3958c56eca35235ed6837c666adb8ede979961
bash /home/check_git_changes.sh

cargo test || true

