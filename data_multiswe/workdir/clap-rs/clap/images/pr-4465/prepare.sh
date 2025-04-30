#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 6cbe5c4323153dd386aa74f8d1900649169228e6
bash /home/check_git_changes.sh

cargo test || true

