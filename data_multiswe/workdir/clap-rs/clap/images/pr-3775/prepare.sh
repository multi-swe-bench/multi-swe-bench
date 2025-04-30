#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 20ed49a535d14afac1972dd3cc3003c97bcc744f
bash /home/check_git_changes.sh

cargo test || true

