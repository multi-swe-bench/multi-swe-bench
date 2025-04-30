#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 5e3386bb40948bc6a608e6c951ce1b86a686e32b
bash /home/check_git_changes.sh

cargo test || true

