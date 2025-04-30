#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout dcfbee978721fa7a0dc3bb1a6cdc46ed4969d156
bash /home/check_git_changes.sh

cargo test || true

