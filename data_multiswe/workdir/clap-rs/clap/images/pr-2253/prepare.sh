#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 76effbd8f9d76df99b87826a2e8ec1b9960851b2
bash /home/check_git_changes.sh

cargo test || true

