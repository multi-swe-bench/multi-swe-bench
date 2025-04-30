#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout d51c0b5a55030f826b302441d6eb2864b2e91ff1
bash /home/check_git_changes.sh

cargo test || true

