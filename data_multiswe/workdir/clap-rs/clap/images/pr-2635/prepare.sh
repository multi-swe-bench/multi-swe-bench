#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 476dd190b7f7a91926dc696f1cb80146c67aabd2
bash /home/check_git_changes.sh

cargo test || true

