#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout df337de701ae1eb65175f6fbe71a7ff2686474f0
bash /home/check_git_changes.sh

cargo test || true

